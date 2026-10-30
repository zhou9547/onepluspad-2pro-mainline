#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the Linux NFC generic-netlink interface on a RAM session only."""

import argparse
import json
from pathlib import Path
import select
import socket
import struct
import time


NETLINK_GENERIC = 16
# Linux UAPI constants are not exported by every Python socket build.
SOL_NETLINK = getattr(socket, "SOL_NETLINK", 270)
NETLINK_ADD_MEMBERSHIP = getattr(socket, "NETLINK_ADD_MEMBERSHIP", 1)
GENL_ID_CTRL = 0x10
NLMSG_ERROR = 2
NLMSG_DONE = 3
NLM_F_REQUEST = 0x01
NLM_F_MULTI = 0x02
NLM_F_ACK = 0x04
NLM_F_DUMP = 0x300

CTRL_CMD_GETFAMILY = 3
CTRL_ATTR_FAMILY_ID = 1
CTRL_ATTR_FAMILY_NAME = 2
CTRL_ATTR_MCAST_GROUPS = 7
CTRL_ATTR_MCAST_GRP_NAME = 1
CTRL_ATTR_MCAST_GRP_ID = 2

NFC_CMD_GET_DEVICE = 1
NFC_CMD_DEV_UP = 2
NFC_CMD_DEV_DOWN = 3
NFC_CMD_START_POLL = 6
NFC_CMD_STOP_POLL = 7
NFC_CMD_GET_TARGET = 8
NFC_EVENT_TARGETS_FOUND = 9
NFC_EVENT_TARGET_LOST = 12

NFC_ATTR_DEVICE_INDEX = 1
NFC_ATTR_DEVICE_NAME = 2
NFC_ATTR_PROTOCOLS = 3
NFC_ATTR_TARGET_INDEX = 4
NFC_ATTR_TARGET_SENS_RES = 5
NFC_ATTR_TARGET_SEL_RES = 6
NFC_ATTR_TARGET_NFCID1 = 7
NFC_ATTR_TARGET_SENSB_RES = 8
NFC_ATTR_TARGET_SENSF_RES = 9
NFC_ATTR_DEVICE_POWERED = 12
NFC_ATTR_IM_PROTOCOLS = 13
NFC_ATTR_TARGET_ISO15693_DSFID = 26
NFC_ATTR_TARGET_ISO15693_UID = 27
NFC_ATTR_TARGET_ATS = 31

PROTOCOL_MASK = (
    (1 << 1)  # Jewel
    | (1 << 2)  # MIFARE
    | (1 << 3)  # FeliCa
    | (1 << 4)  # ISO-DEP / NFC-A
    | (1 << 6)  # NFC-B
    | (1 << 7)  # ISO15693
)
TARGET_ATTRS = {
    NFC_ATTR_TARGET_INDEX,
    NFC_ATTR_TARGET_SENS_RES,
    NFC_ATTR_TARGET_SEL_RES,
    NFC_ATTR_TARGET_NFCID1,
    NFC_ATTR_TARGET_SENSB_RES,
    NFC_ATTR_TARGET_SENSF_RES,
    NFC_ATTR_TARGET_ISO15693_DSFID,
    NFC_ATTR_TARGET_ISO15693_UID,
    NFC_ATTR_TARGET_ATS,
}


def align4(value):
    return (value + 3) & ~3


def attr(kind, value):
    body = bytes(value)
    size = 4 + len(body)
    return struct.pack("<HH", size, kind) + body + b"\0" * (align4(size) - size)


def attr_u32(kind, value):
    return attr(kind, struct.pack("<I", value))


def attr_string(kind, value):
    return attr(kind, value.encode("utf-8") + b"\0")


def parse_attrs(data):
    rows = []
    offset = 0
    while offset < len(data):
        if offset + 4 > len(data):
            raise ValueError("Truncated netlink attribute")
        size, kind = struct.unpack_from("<HH", data, offset)
        if size < 4 or offset + size > len(data):
            raise ValueError("Invalid netlink attribute length")
        value = data[offset + 4 : offset + size]
        nested = kind & 0x8000
        rows.append((kind & 0x3FFF, value, bool(nested)))
        offset += align4(size)
    return rows


def message(sequence, kind, command, version, flags, attributes):
    payload = struct.pack("<BBH", command, version, 0) + b"".join(attributes)
    return struct.pack("<IHHII", 16 + len(payload), kind, flags, sequence, 0) + payload


def messages(data):
    offset = 0
    while offset + 16 <= len(data):
        length, kind, flags, sequence, pid = struct.unpack_from(
            "<IHHII", data, offset
        )
        if length < 16 or offset + length > len(data):
            raise ValueError("Invalid netlink message length")
        payload = data[offset + 16 : offset + length]
        yield kind, flags, sequence, pid, payload
        offset += align4(length)


def parse_error(payload):
    if len(payload) < 4:
        raise ValueError("Truncated netlink error")
    code = struct.unpack_from("<i", payload)[0]
    return -code if code < 0 else 0


def recv_packets(sock):
    data, _ = sock.recvfrom(65536)
    return list(messages(data))


class NfcNetlink:
    def __init__(self, deadline):
        if not Path("/run/oneplus13/ram-session").is_file():
            raise RuntimeError("Protected phone RAM session required")
        self.sock = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, NETLINK_GENERIC)
        self.sock.bind((0, 0))
        self.sock.setblocking(False)
        self.sequence = 1
        self.deadline = deadline
        self.family, self.events_group = self._family()
        self.last_targets = []
        if self.events_group is not None:
            self.sock.setsockopt(
                SOL_NETLINK, NETLINK_ADD_MEMBERSHIP, self.events_group
            )

    def _next(self):
        value = self.sequence
        self.sequence = (self.sequence + 1) & 0xFFFFFFFF
        return value

    def send(
        self,
        command,
        flags=NLM_F_REQUEST | NLM_F_ACK,
        attributes=(),
        kind=None,
    ):
        sequence = self._next()
        if kind is None:
            kind = getattr(self, "family", GENL_ID_CTRL)
        packet = message(
            sequence, kind, command, 1, flags, attributes
        )
        self.sock.send(packet)
        return sequence

    def _receive_until(self, sequence, timeout):
        end = min(time.monotonic() + timeout, self.deadline)
        rows = []
        while time.monotonic() < end:
            ready, _, _ = select.select([self.sock], [], [], max(0, end - time.monotonic()))
            if not ready:
                break
            for kind, flags, seq, _, payload in recv_packets(self.sock):
                if kind == NLMSG_ERROR:
                    code = parse_error(payload)
                    if seq == sequence:
                        if code:
                            raise OSError(code, "NFC netlink request failed")
                        return rows
                elif seq == sequence:
                    rows.append((kind, flags, payload))
                    if flags & NLM_F_MULTI == 0 and kind != NLMSG_DONE:
                        # Requests with ACK may return data followed by ACK.
                        continue
        if rows:
            return rows
        raise TimeoutError("NFC netlink request timed out")

    def request(self, command, attributes=(), timeout=8):
        sequence = self.send(command, attributes=attributes)
        self._receive_until(sequence, timeout)

    def dump(self, command, attributes=(), timeout=8):
        sequence = self.send(
            command,
            flags=NLM_F_REQUEST | NLM_F_DUMP,
            attributes=attributes,
        )
        end = min(time.monotonic() + timeout, self.deadline)
        rows = []
        while time.monotonic() < end:
            ready, _, _ = select.select(
                [self.sock], [], [], max(0, end - time.monotonic())
            )
            if not ready:
                break
            for kind, flags, seq, _, payload in recv_packets(self.sock):
                if seq != sequence:
                    continue
                if kind == NLMSG_ERROR:
                    code = parse_error(payload)
                    if code:
                        raise OSError(code, "NFC netlink dump failed")
                    return rows
                if kind == NLMSG_DONE:
                    return rows
                if len(payload) >= 4:
                    rows.append((payload[0], payload[4:]))
        raise TimeoutError("NFC netlink dump timed out")

    def _family(self):
        sequence = self.send(
            CTRL_CMD_GETFAMILY,
            attributes=(attr_string(CTRL_ATTR_FAMILY_NAME, "nfc"),),
            kind=GENL_ID_CTRL,
        )
        rows = self._receive_until(sequence, 5)
        for _, _, payload in rows:
            if len(payload) < 4:
                continue
            attributes = parse_attrs(payload[4:])
            family = next(
                (
                    struct.unpack("<H", value)[0]
                    for kind, value, _ in attributes
                    if kind == CTRL_ATTR_FAMILY_ID and len(value) == 2
                ),
                None,
            )
            if family is None:
                continue
            event_group = None
            for kind, value, _ in attributes:
                if kind != CTRL_ATTR_MCAST_GROUPS:
                    continue
                # nlctrl uses nla_nest_start_noflag() for both containers.
                # Their schema determines nesting even without NLA_F_NESTED.
                for _, group_value, _ in parse_attrs(value):
                    group = parse_attrs(group_value)
                    name = next(
                        (
                            item.decode("utf-8", errors="replace").rstrip("\0")
                            for item_kind, item, _ in group
                            if item_kind == CTRL_ATTR_MCAST_GRP_NAME
                        ),
                        None,
                    )
                    group_id = next(
                        (
                            struct.unpack("<I", item)[0]
                            for item_kind, item, _ in group
                            if item_kind == CTRL_ATTR_MCAST_GRP_ID
                            and len(item) == 4
                        ),
                        None,
                    )
                    if name == "events":
                        event_group = group_id
            return family, event_group
        raise RuntimeError("NFC generic-netlink family is absent")

    def devices(self):
        rows = []
        for command, payload in self.dump(NFC_CMD_GET_DEVICE):
            if command != NFC_CMD_GET_DEVICE:
                continue
            facts = {}
            for kind, value, _ in parse_attrs(payload):
                if kind == NFC_ATTR_DEVICE_INDEX and len(value) == 4:
                    facts["index"] = struct.unpack("<I", value)[0]
                elif kind == NFC_ATTR_DEVICE_NAME:
                    facts["name"] = value.rstrip(b"\0").decode(
                        "utf-8", errors="replace"
                    )
                elif kind in (NFC_ATTR_PROTOCOLS, NFC_ATTR_IM_PROTOCOLS) and len(value) == 4:
                    facts[
                        "protocols" if kind == NFC_ATTR_PROTOCOLS else "initiator_protocols"
                    ] = struct.unpack("<I", value)[0]
                elif kind == NFC_ATTR_DEVICE_POWERED and len(value) == 1:
                    facts["powered"] = bool(value[0])
            rows.append(facts)
        return rows

    def targets(self, index):
        rows = []
        current = None
        for command, payload in self.dump(
            NFC_CMD_GET_TARGET, attributes=(attr_u32(NFC_ATTR_DEVICE_INDEX, index),)
        ):
            if command != NFC_CMD_GET_TARGET:
                continue
            target_found = False
            for kind, value, _ in parse_attrs(payload):
                if kind == NFC_ATTR_TARGET_INDEX:
                    if current is not None:
                        rows.append(current)
                    target_found = True
                    current = {
                        "index": struct.unpack("<I", value)[0]
                        if len(value) == 4
                        else None
                    }
                elif current is not None and kind in TARGET_ATTRS:
                    current[f"attr_{kind}_hex"] = value.hex()
            if not target_found and current is not None and any(
                kind in TARGET_ATTRS for kind, _, _ in parse_attrs(payload)
            ):
                continue
        if current is not None:
            rows.append(current)
        return rows

    def wait_found(self, index, seconds):
        end = min(time.monotonic() + seconds, self.deadline)
        next_poll = 0.0
        while time.monotonic() < end:
            now = time.monotonic()
            if now >= next_poll:
                try:
                    targets = self.targets(index)
                    if targets:
                        self.last_targets = targets
                        return True
                except (OSError, TimeoutError, ValueError):
                    pass
                next_poll = now + 1.0
            ready, _, _ = select.select(
                [self.sock], [], [], max(0, end - time.monotonic())
            )
            if not ready:
                return False
            for kind, _, _, _, payload in recv_packets(self.sock):
                if kind != self.family or len(payload) < 4:
                    continue
                command = payload[0]
                if command != NFC_EVENT_TARGETS_FOUND:
                    continue
                attributes = parse_attrs(payload[4:])
                event_index = next(
                    (
                        struct.unpack("<I", value)[0]
                        for attr_kind, value, _ in attributes
                        if attr_kind == NFC_ATTR_DEVICE_INDEX and len(value) == 4
                    ),
                    None,
                )
                if event_index == index:
                    return True
        return False

    def close(self):
        self.sock.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--require-target", action="store_true")
    args = parser.parse_args()
    deadline = time.monotonic() + max(15, args.wait_seconds + 12)
    netlink = NfcNetlink(deadline)
    result = {
        "scope": "ONEPLUS13_RAM_NFC_GENERIC_NETLINK",
        "device_index": args.device,
        "family_resolved": True,
        "event_multicast_subscribed": netlink.events_group is not None,
        "controller_started": False,
        "target_event_observed": False,
        "targets": [],
        "cleanup_complete": False,
    }
    pass_ = False
    try:
        result["devices_before"] = netlink.devices()
        netlink.request(
            NFC_CMD_DEV_UP,
            attributes=(attr_u32(NFC_ATTR_DEVICE_INDEX, args.device),),
        )
        netlink.request(
            NFC_CMD_START_POLL,
            attributes=(
                attr_u32(NFC_ATTR_DEVICE_INDEX, args.device),
                attr_u32(NFC_ATTR_PROTOCOLS, PROTOCOL_MASK),
            ),
            timeout=10,
        )
        result["controller_started"] = True
        result["devices_after_start"] = netlink.devices()
        if args.wait_seconds:
            result["target_event_observed"] = netlink.wait_found(
                args.device, args.wait_seconds
            )
            if result["target_event_observed"]:
                result["targets"] = netlink.last_targets or netlink.targets(args.device)
        pass_ = result["controller_started"] and bool(result["devices_after_start"])
        if args.require_target:
            pass_ = pass_ and result["target_event_observed"] and bool(result["targets"])
    finally:
        for command in (NFC_CMD_STOP_POLL, NFC_CMD_DEV_DOWN):
            try:
                netlink.request(
                    command,
                    attributes=(attr_u32(NFC_ATTR_DEVICE_INDEX, args.device),),
                    timeout=6,
                )
            except (OSError, TimeoutError, ValueError):
                pass
        netlink.close()
        result["cleanup_complete"] = True
    result["pass"] = pass_
    print("NFC_POLL_RESULT " + json.dumps(result, sort_keys=True))
    raise SystemExit(0 if pass_ else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import struct
import unittest
from unittest.mock import Mock, patch


PATH = Path(__file__).resolve().parents[1] / "tools/oneplus13/ram-nfc-poll.py"
SPEC = importlib.util.spec_from_file_location("ram_nfc_poll", PATH)
POLL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLL)


class NfcNetlinkEncodingTests(unittest.TestCase):
    def test_family_multicast_groups_accept_linux_noflag_nesting(self):
        for flag in (0, 0x8000):
            with self.subTest(nested_flag=flag):
                group = POLL.attr_string(POLL.CTRL_ATTR_MCAST_GRP_NAME, "events")
                group += POLL.attr_u32(POLL.CTRL_ATTR_MCAST_GRP_ID, 37)
                attributes = POLL.attr(POLL.CTRL_ATTR_FAMILY_ID, struct.pack("<H", 42))
                attributes += POLL.attr(
                    POLL.CTRL_ATTR_MCAST_GROUPS | flag,
                    POLL.attr(1 | flag, group),
                )
                payload = struct.pack("<BBH", 1, 1, 0) + attributes
                netlink = POLL.NfcNetlink.__new__(POLL.NfcNetlink)
                netlink.send = Mock(return_value=1)
                netlink._receive_until = Mock(return_value=[(POLL.GENL_ID_CTRL, 0, payload)])
                self.assertEqual(netlink._family(), (42, 37))

    def test_constructor_subscribes_with_linux_netlink_socket_options(self):
        sock = Mock()
        with patch.object(POLL.Path, "is_file", return_value=True), patch.object(
            POLL.socket, "AF_NETLINK", 16, create=True
        ), patch.object(POLL.socket, "socket", return_value=sock), patch.object(
            POLL.NfcNetlink, "_family", return_value=(42, 37)
        ):
            netlink = POLL.NfcNetlink(100)
        sock.setsockopt.assert_called_once_with(270, 1, 37)
        self.assertEqual(netlink.events_group, 37)

    def test_alignment_and_u32_attribute(self):
        row = POLL.attr_u32(POLL.NFC_ATTR_DEVICE_INDEX, 7)
        self.assertEqual(len(row), 8)
        self.assertEqual(struct.unpack_from("<HH", row), (8, 1))
        self.assertEqual(struct.unpack_from("<I", row, 4)[0], 7)

    def test_rejects_truncated_and_zero_length_attributes(self):
        for row in (b"\x08\x00", b"\x00\x00\x00\x00"):
            with self.subTest(row=row), self.assertRaises(ValueError):
                POLL.parse_attrs(row)

    def test_protocol_mask_covers_expected_initiator_types(self):
        self.assertEqual(
            POLL.PROTOCOL_MASK,
            (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 6) | (1 << 7),
        )

    def test_message_headers_round_trip(self):
        packet = POLL.message(9, 0x22, 7, 1, POLL.NLM_F_REQUEST, ())
        rows = list(POLL.messages(packet))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][:4], (0x22, POLL.NLM_F_REQUEST, 9, 0))
        self.assertEqual(rows[0][4][0], 7)

    def test_family_lookup_does_not_require_a_resolved_family(self):
        class Socket:
            def __init__(self):
                self.values = []

            def send(self, value):
                self.values.append(value)

        netlink = POLL.NfcNetlink.__new__(POLL.NfcNetlink)
        netlink.sock = Socket()
        netlink.sequence = 1
        netlink.send(POLL.CTRL_CMD_GETFAMILY)
        rows = list(POLL.messages(netlink.sock.values[0]))
        self.assertEqual(rows[0][0], POLL.GENL_ID_CTRL)


if __name__ == "__main__":
    unittest.main()

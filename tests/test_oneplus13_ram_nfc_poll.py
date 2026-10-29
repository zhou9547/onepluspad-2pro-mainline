#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import struct
import unittest


PATH = Path(__file__).resolve().parents[1] / "tools/oneplus13/ram-nfc-poll.py"
SPEC = importlib.util.spec_from_file_location("ram_nfc_poll", PATH)
POLL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLL)


class NfcNetlinkEncodingTests(unittest.TestCase):
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

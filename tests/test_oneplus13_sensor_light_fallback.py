# SPDX-License-Identifier: GPL-2.0-only
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / 'packaging/sensors/patches/libssc/0003-libssc-retry-light-discovery-with-non-default-uids.patch'


class SensorLightFallback(unittest.TestCase):
    def setUp(self):
        self.sources = json.loads((ROOT / 'packaging/sensors/sources.json').read_text())
        self.text = PATCH.read_text()

    def test_patch_is_pinned_and_only_retries_ambient_light_once(self):
        source = next(item for item in self.sources['sources'] if item['name'] == 'libssc')
        patch = next(item for item in source['patches'] if Path(item['file']).name == PATCH.name)
        self.assertEqual(hashlib.sha256(PATCH.read_bytes()).hexdigest(), patch['sha256'])
        self.assertEqual([Path(item['file']).name for item in source['patches']], [
            '0001-libssc-select-the-delivery-and-batching-of-streams-at-run-time.patch',
            '0002-libssc-choose-the-stream-delivery-by-sensor-type.patch',
            PATCH.name,
        ])
        self.assertIn('gboolean light_discover_all;', self.text)
        self.assertIn('g_strcmp0 (priv->data_type, "ambient_light")', self.text)
        self.assertIn('!priv->light_discover_all', self.text)
        self.assertIn('msg.only_default_values = !priv->light_discover_all;', self.text)
        self.assertNotIn('SSC_MSG_REPORT_MEASUREMENT', self.text)


if __name__ == '__main__':
    unittest.main()

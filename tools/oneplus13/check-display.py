#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile the pinned kernel's real DSC PPS packer against its real structure.

Host-only, public inputs only. This checks C field names/layout and all packet
bytes independently of Python's packer. It does not validate display hardware.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from dsc import decode_pps, c_initializer
from panel import vendor_pps


def extract_function(source, signature):
    start = source.index(signature)
    brace = source.index('{', start)
    depth, end = 1, brace+1
    while depth and end < len(source):
        depth += (source[end] == '{') - (source[end] == '}')
        end += 1
    if depth:
        raise ValueError('Unterminated C function')
    return source[start:end]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kernel-source', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--sanitize', action='store_true')
    p.add_argument('--keep-source', type=Path, help='Optional host inspection C source')
    a = p.parse_args()
    repo = Path(__file__).resolve().parents[2]
    pin = json.loads((repo / 'devices/oneplus13/source.json').read_text())['kernel']['commit']
    actual = subprocess.check_output(['git', '-C', str(a.kernel_source), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != pin:
        raise ValueError('DSC reference source commit differs from the pinned kernel')
    fixture = json.loads((repo / 'devices/oneplus13/panel-aa569-120hz.json').read_text())
    pps = vendor_pps(fixture['on_packets'])
    cfg = decode_pps(pps)
    def kernel_file(name):
        return subprocess.check_output(['git', '-C', str(a.kernel_source),
                                        'show', f'{pin}:{name}']).decode('utf-8')
    header = kernel_file('include/drm/display/drm_dsc.h')
    source = kernel_file('drivers/gpu/drm/display/drm_dsc_helper.c')
    function = extract_function(source, 'void drm_dsc_pps_payload_pack(')
    # Replace only the transitive DP header. Keep the complete original DSC
    # structs/constants; a tiny DP packet definition satisfies an unused type.
    original_header_sha = hashlib.sha256(header.encode()).hexdigest()
    header = header.replace('#include <drm/display/drm_dp.h>', '')
    declarations = '''
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>
typedef uint8_t u8; typedef uint16_t u16; typedef uint32_t u32;
typedef uint16_t __be16;
#define __packed __attribute__((packed))
#define BUILD_BUG_ON(c) _Static_assert(!(c), "PPS structure layout changed")
#define DP_SDP_PPS_HEADER_PAYLOAD_BYTES_MINUS_1 127
struct dp_sdp_header { u8 bytes[4]; };
static inline uint16_t cpu_to_be16(uint16_t x) {
  const uint16_t little = 1;
  return *(const unsigned char *)&little ? (uint16_t)((x << 8) | (x >> 8)) : x;
}
'''
    main_c = '''
int main(void) {
  struct drm_dsc_picture_parameter_set pps;
  struct drm_dsc_config wire = aa569_dsc;
  /* DPU/MSM retain physical bpp; the PPS packer expects encoded group bpp. */
  wire.bits_per_pixel *= 2;
  drm_dsc_pps_payload_pack(&pps, &wire);
  const unsigned char *bytes = (const unsigned char *)&pps;
  for (unsigned int i=0;i<sizeof(pps);i++) printf("%02x",bytes[i]);
  putchar('\n');
  drm_dsc_pps_payload_pack(&pps, &aa569_dsc);
  for (unsigned int i=0;i<sizeof(pps);i++) printf("%02x",bytes[i]);
  putchar('\n');
  return 0;
}
'''.replace("putchar('\n')", "putchar('\\n')")
    with tempfile.TemporaryDirectory(prefix='oneplus13-pps-') as tmp:
        c_file, exe = Path(tmp) / 'pps.c', Path(tmp) / 'pps-test.exe'
        combined = declarations+header+function+c_initializer(cfg)+main_c
        c_file.write_text(combined, encoding='utf-8')
        if a.keep_source:
            a.keep_source.write_text(combined, encoding='utf-8')
        command = ['gcc', '-std=c11', '-Wall', '-Wextra', '-Werror']
        if sys.platform == 'win32':
            # Old MinGW defaults to MS layout, which adds tail padding even
            # to this packed Linux structure. Use the target's GCC ABI; retain
            # the real kernel's 128-byte BUILD_BUG_ON instead of bypassing it.
            command += ['-mno-ms-bitfields']
        if a.sanitize:
            command += ['-fsanitize=address,undefined', '-fno-omit-frame-pointer']
        subprocess.run(command+[str(c_file), '-o', str(exe)], check=True)
        correct, wrong = subprocess.check_output([str(exe)], text=True).splitlines()
    expected = pps.ljust(128, b'\0')
    if bytes.fromhex(correct) != expected or bytes.fromhex(wrong) == expected:
        raise ValueError('Real kernel PPS packer mismatch or ineffective bpp negative control')
    report = {'scope': 'HOST_C_PPS_ONLY', 'hardware_tested': False, 'kernel_commit': actual,
              'reference_header_sha256': original_header_sha,
              'compiled_header_sha256': hashlib.sha256(header.encode()).hexdigest(),
              'reference_function_sha256': hashlib.sha256(function.encode()).hexdigest(),
              'vendor_pps_sha256': hashlib.sha256(pps).hexdigest(),
              'matched_payload_bytes': 94, 'matched_zero_padding_bytes': 34,
              'physical_bpp_q4': 128, 'encoded_bpp_q4': 256,
              'wrong_bpp_negative_control_rejected': True, 'sanitizers': a.sanitize}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print('Real kernel C PPS packer: 94 data bytes + 34 padding bytes match; bpp negative control rejected.')


if __name__ == '__main__':
    main()

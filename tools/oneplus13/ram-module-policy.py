#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Keep unreviewed peripherals manual when matching modules are preinstalled.

This is a RAM bring-up policy, not a hardware driver allowlist or a sandbox.
Built-in drivers need separate device-tree review. Display retains its existing
explicit activation policy. No driver is loaded by this module.
"""
from pathlib import PurePosixPath
import re

PREFIXES=('kernel/sound/', 'kernel/drivers/net/wireless/',
          'kernel/drivers/power/sequencing/', 'kernel/drivers/pci/pwrctrl/',
          'kernel/drivers/media/', 'kernel/drivers/nfc/', 'kernel/net/nfc/')
EXACT={'kernel/drivers/misc/fastrpc.ko'}

def blocked_modules(paths, release):
    if not re.fullmatch(r'[A-Za-z0-9._+-]{1,128}',release):
        raise ValueError('Invalid module release')
    prefix='lib/modules/'+release+'/'
    selected=set()
    for path in paths:
        name=path.removeprefix('./')
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts:
            raise ValueError('Module archive path escapes root')
        if not name.endswith('.ko'):
            continue
        if not name.startswith(prefix):
            raise ValueError('Module from another kernel release')
        relative=name[len(prefix):]
        if relative.startswith(PREFIXES) or relative in EXACT:
            stem=PurePosixPath(relative).stem.replace('-','_')
            if not re.fullmatch(r'[A-Za-z0-9_]+',stem):
                raise ValueError('Invalid kernel module name')
            selected.add(stem)
    return sorted(selected)

def configuration(modules):
    if not modules or len(set(modules))!=len(modules):
        raise ValueError('A nonempty unique module set is required')
    lines=['# RAM staging: unreviewed peripheral probing requires separate review.',
           '# Built-in drivers are governed separately by the reviewed DT.']
    for module in sorted(modules):
        if not re.fullmatch(r'[A-Za-z0-9_]+',module):
            raise ValueError('Invalid module name')
        lines.extend(['blacklist '+module,'install '+module+' /bin/false'])
    return '\n'.join(lines)+'\n'

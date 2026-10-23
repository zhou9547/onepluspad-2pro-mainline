# Isolated phone kernel patches

Apply to the exact platform commit recorded in ../source.json, currently
7a81d184e3098624d4342d8f4eff5e23674bcc9f. build.sh checks/applies them and exports
the resulting real kernel diff in phone-kernel.patch with the phone sources.
Existing Pad builds never apply this directory.
The kernel release also carries the exported phone patch digest, so a changed
DSI/touch/board implementation cannot silently reuse the previous vermagic.

0001 selects the existing native422 DSC RC table, keeps RGB conversion disabled,
uses group bpp only for DRM RC arithmetic, and restores physical-pixel bpp for
MSM bandwidth/timing and the DPU API. The shared RGB route is unchanged. It does
not implement native420, a panel, SPR, REGDMA or physical display acceptance.

check-display.py compiles the real patched functions with the original DRM
helpers, tables and structure. It reconstructs the complete public AA569 PPS
from minimal geometry/format, compares all128 bytes, rejects the unmodified
baseline and wrong-bpp controls, preserves the RGB result and rejects invalid
native422 inputs. CI uses ASan/UBSan and builds the real ARM64 module afterward.

The patch modifies GPL-2.0-only Linux MSM DSI code from the pinned kernel;
original copyright and licensing remain with that file. Authorship of this
adaptation is Codex; there is no hardware Tested-by claim.

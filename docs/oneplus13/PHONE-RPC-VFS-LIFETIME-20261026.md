# Phone RPC VFS descriptor lifetime

The original pinned apps_std regression test avoided deinitialization because
shared directory ancestry could be freed twice. Before adding volatile file
data, reproduce and repair this ownership error in the existing read-only VFS.

Source baseline is linux-msm/hexagonrpc commit
598b591ae9da6a6cfe2ca5ea78998019ca6395ea with the unchanged five shared recipe
patches and the preceding four phone overlays. A standalone real C fixture opens
the root and its slash alias, closes the root first, then closes the alias.
ASan reports heap-use-after-free on the baseline. The same fixture exits zero
against the corrected source, including isolated leak checking.

Phone patch0005 counts file-number assignments separately from child nodes.
Closing one alias preserves the others; closing a parent preserves its children.
Final child cleanup releases unassigned ancestors once. Temporary traversal pops
release only unassigned leaf nodes. Invalid root/directory numbers are refused
before indexing the table. No host write operation is added.

Host fresh-tar build v8 passes 11 release and 11 ASan/UBSan C tests plus six
Python recipe checks. The original apps_std wire assertions remain and now call
the real deinitializer. The new test covers alias/ancestor closes, file-number
exhaustion for aliases and new children, invalid descriptors/null names,
temporary pops and failed lookup cleanup. The first unpublished generation
missed a close-counter replacement and failed the new exhaustion fixture; its
v7 output is retained and was never published or used on a phone.

The whole suite still excludes leak checking because the original root-tree
builder lacks a destructor. Only the standalone alias fixture checks leaks.
Native ARM64 CI remains required. This change adds no writable registry, DSP
mapping, sensor stream or phone retry qualification. Run73's halted acceptance
and the other peripheral gates remain in force. The shared Pad recipe is intact.

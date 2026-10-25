# Phone sensor ABI references and private data preparation

The exact phone OTA vendor image is hash-verified. Its libadsprpc.so and
sensors.qsh.so independently match both binary hashes already pinned in the
original project's packaging/sensors/sources.json. This establishes that the
existing reverse dispatcher and request ABI references are applicable to these
phone userspace binaries. It does not establish that phone DSP attach, a live
reverse-RPC exchange or a sensor stream works.

The phone ADSP image contains the original sns_reg_config, vendor/ODM config
and persist registry path strings. The narrow property shim and two distinct
json.lst/json_list mappings remain unchanged. No index rename or Pad registry
substitution is introduced.

A host-only private data package contains171 phone ROM files,744 owner registry
files, six socinfo attributes and the original importer metadata/version. Of
the171 ROM files,168 have existing RPC path mappings; the other three are kept
as reference-only data without inventing new DSP-visible locations. All923
regular-file bytes and permission modes, plus three original mapping symlinks,
are verified after archive creation. The original importer is byte-unchanged.
There are no executables, services or FastRPC control operations in this data
package, and it has not been delivered to the phone or uploaded.

All three generic ARM64 programs also pass host QEMU-user runtime link probes
against the exact run68 SquashFS. Syscall traces show no device open or attach.
hexagonrpcd rejects unsupported --help with usage/exit4, as expected; the other
two programs return0. These are link probes, not sensor tests.

`assemble-sensor-ram-runtime.py` combines the separately verified five ELF files
and private phone data into a host-only RAM runtime archive. It rejects Pad
service/udev hooks, unmanifested/traversal paths, changed permissions/bytes,
unsafe mappings and non-ARM64 ELF. It includes no mount matrix, sensor claims,
firmware, modules or activation service. In particular, the original Pad udev
rule's automatic attachment and candidate rotation matrix are not phone defaults.
Five host rejection/control tests pass; the combined private archive is built
and stays ineligible for attach or streams.

Saved Android sensorservice identifies BMI26x accelerometer/gyroscope, AK0991x
magnetometer and TCS3720 proximity through actual HAL registrations. Light is
an Oplus fusion HAL sensor. These are HAL-reported families, not raw silicon IDs
or proof that every corresponding Linux SSC path works. Do not select a driver
just because another registry template exists.

Existing actual ARM64 CI40198265425 passed eight hexagonrpc and seven libssc
tests. The phone DSP image differs from the Pad reference, even though the
host ABI-reference binaries match. First attach, dispatch/mapping behavior,
independent recovery and sensor data/axes remain gates before streams. Shared
ADSP must never be restarted as a sensor retry. Physical motion, orientation,
proximity targets and light response belong in a later combined owner session.

# LG UltraGear HDR on Linux

[Português](README.md) | **English**

I started this project after trying to use HDR on my LG UltraGear with Arch Linux,
Hyprland, and an RTX 4060 Ti. Enabling HDR initially produced a dim image and then
a frozen display. The investigation led to a missing bit in the monitor's EDID.

This repository contains read-only diagnostics, an **offline** EDID correction
for LG displays identified as **GSM 0x7766**, my monitor's original and corrected
EDIDs, and the results I have verified so far. The project is independent of LG,
NVIDIA, Mozilla, and Hyprland.

## What this version does

The tool reads an EDID and can write a **new copy** with the missing HDR Static
Metadata Type 1 capability bit enabled. It does not install that copy, enable HDR,
run `sudo`, switch display modes, or modify physical monitor firmware, drivers,
or boot configuration. Commands refuse root execution and never overwrite an
existing output file.

I have kept this version offline. It does not include a persistent installer.

## The issue

My LG GSM 0x7766 advertised PQ/ST2084 but did not advertise Static Metadata Type 1.
In NVIDIA 615.78.08, `nvDpyIsHDRCapable()` explicitly checks for that capability.
Without it, the driver can reject HDR/BT.2020 configuration.

The correction changes only the missing bit and the CTA extension checksum.
Display modes, refresh rates, primaries, luminance values, and all other EDID
bytes remain unchanged.

This is a known quirk, not a claim that I discovered it first: an earlier
[upstream patch proposal](https://www.mail-archive.com/dri-devel%40lists.freedesktop.org/msg630093.html)
describes the same missing bit for GSM 0x7766. My contribution here is documenting
my reproduction, sharing offline tools and authorized fixtures, and testing the
correction on my setup.

This is not a universal fix. The tool rejects other product IDs, missing PQ
support, invalid checksums, truncated data, and ambiguous multiple HDR blocks.

### Results and limits

On my PC with Arch Linux, RTX 4060 Ti, NVIDIA 615.78.08, Hyprland 0.56.2, and
Aquamarine 0.15.1, the corrected override allowed the compositor to configure:

- 2560×1440 at approximately 165 Hz.
- A 10-bit color format, `XBGR2101010`.
- The `hdr` color-management preset.

I did not experience the previous complete freeze in that test. I have **not
measured luminance or calibrated physical color accuracy**. The compositor state
alone does not prove that the entire display pipeline is color-correct.

I am still investigating Firefox 158/YouTube playback. Receiving PQ/BT.2020 video
from YouTube does not prove correct presentation. The experimental Aquamarine
patches used during the investigation are not included or required by this tool.

## Run without installation

Python 3.10 or newer; no external Python dependencies are needed to run these
commands. From the repository directory, as a regular user:

```bash
python3 -m lg_hdr doctor
```

The diagnostic reports connected outputs, checksums, and HDR descriptors. It
does not include serial numbers or raw EDID bytes in its JSON report. Content
hashes can identify a particular EDID and should also be reviewed before sharing.

If any output reports an error, the command preserves available results in JSON
and exits with status `2`. A diagnostic without errors exits with status `0`.

Inspect an existing EDID file:

```bash
python3 -m lg_hdr inspect /path/to/original.bin
```

Create a corrected copy without installing or activating it:

```bash
python3 -m lg_hdr patch /path/to/original.bin ./corrected.bin
```

The destination must be inside your home directory or `/tmp` and must not already
exist. The original remains unchanged. An EDID that already advertises Type 1 is
copied without further changes.

**The real EDIDs in `examples/edid/` are from my monitor, and I authorized their
publication.** They can contain serial numbers. Do not submit someone else's
EDID without permission; use synthetic fixtures for contributions instead.

Validation covers structural boundaries and checksums, not complete EDID
conformance. Valid checksums do not prove that all advertised capabilities are
correct. EDID reads are bounded to 32 KiB, the maximum base-block size plus 255
extension blocks. Oversized inputs are rejected without reading the entire file.

## Automated tests

```bash
python3 -m unittest discover -s tests -v
```

The 29 tests run offline using temporary files, synthetic EDIDs, and the two
authorized real fixtures. They cover the restricted correction, byte preservation,
idempotency, corruption, ambiguous blocks, file protections, bounded reads,
and diagnostic error reporting. No GPU, monitor, or root access is needed.
The same offline suite runs in GitHub Actions.

## Progress

- [x] EDID inspection and PQ/Type 1 detection.
- [x] Offline correction with recalculated checksums.
- [x] Synthetic and authorized real-fixture tests, plus CI.
- [ ] Compare Firefox/Hyprland playback with an independent HDR player.
- [ ] Separately document a persistent, reversible installation method.
- [ ] Validate installation and recovery before distributing an installer.

## Evidence and sharing

- [My investigation, in English](docs/investigation.en.md).
- [Original investigation, in Portuguese](docs/investigation.md).
- [Authorized real EDIDs and exact byte changes](examples/edid/README.md).
- [Bilingual post for sharing the findings](docs/announcement.md).

Full memory dumps are not published. Full logs need review before inclusion.

## Sources

- [NVIDIA 615.78.08 HDR capability check](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/615.78.08/src/nvidia-modeset/src/nvkms-dpy.c).
- [Earlier patch proposal for missing Type 1 on GSM 0x7766](https://www.mail-archive.com/dri-devel%40lists.freedesktop.org/msg630093.html).
- [Linux kernel EDID override documentation](https://www.kernel.org/doc/html/latest/admin-guide/edid.html).
- [Firefox 158/Wayland video-format investigation](https://bugzilla.mozilla.org/show_bug.cgi?id=2083037).

## License

MIT for this project's original code. External sources are references; this
repository does not include NVIDIA driver, Firefox, or other third-party library
source code.

Developed with assistance from OpenAI Codex.

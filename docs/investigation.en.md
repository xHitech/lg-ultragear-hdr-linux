# My HDR investigation

[Português](investigation.md) | **English**

My setup: Arch Linux, NVIDIA RTX 4060 Ti, nvidia-open/NVIDIA 615.78.08,
Hyprland 0.56.2, Aquamarine 0.15.1, and Firefox 158.0.1.

I collected these results while investigating my monitor with assistance from
Codex. This summary excludes network addresses, credentials, signed URLs,
cookies, and memory dumps.

## Before correcting the EDID

Driver atomic TEST_ONLY probes returned:

| Variant | Result |
| --- | --- |
| Original HDR request | EINVAL (22) |
| Without BT.2020 | EINVAL (22) |
| Without HDR metadata | EINVAL (22) |
| Without both BT.2020 and HDR metadata | Accepted |
| Without hardware cursor | EINVAL (22) |
| Without input fence | EINVAL (22) |

Kernel and backend CRTC assignments matched in that run, so a CRTC-assignment
mismatch did not explain this reproduction. These probes were used during the
investigation; they are not part of the offline CLI distributed here.

My EDID advertised PQ/ST2084 but omitted the Type 1 bit required by NVIDIA
615.78.08's `nvDpyIsHDRCapable()`.

The two authorized 384-byte files have the following SHA-256 hashes:

| File | SHA-256 |
| --- | --- |
| Original | `313f6ab5dcd9dfa9df565d58588a50a0f7bae4409c71523db32c199ff6e80223` |
| Corrected | `8755c1022186b71a36a14848c7dd00f3bfa1cdccffd73dc4bb9dea042bdd6769` |

Only two bytes differ:

- `0x9f`: `00` → `01`, the Static Metadata Type 1 capability bit.
- `0xff`: `79` → `78`, the CTA checksum.

An [earlier upstream patch proposal](https://www.mail-archive.com/dri-devel%40lists.freedesktop.org/msg630093.html)
describes the same quirk for GSM 0x7766; I am sharing a reproduction and tooling,
not claiming priority for discovering the missing bit.

## After I applied the correction manually

My test logs recorded:

- 2560×1440 at 164.95599 Hz.
- `XBGR2101010`, with 10 bits per color channel.
- `colorManagementPreset=hdr`.
- SDR brightness levels 2.0, 1.8, 1.5, and 1.2 applied in sequence.
- A return to `XRGB8888` and `srgb` after the timed trial.

I did not experience the previous complete freeze and chose to continue testing
with SDR brightness 1.5. I have not measured luminance or color accuracy. This
setting is my preference, not a universal calibration.

## Firefox/YouTube

Playback statistics showed 10-bit VP9 Profile 2, YouTube format 337,
3840×2160 at 60 fps, and `smpte2084 (PQ) / bt2020`.

That confirms the HDR content received, not its correct physical presentation.
I noticed a washed-out video after enabling HDR in Firefox. I have not completed
the comparison with an independent player, so that issue remains unresolved.

## Project status

This repository distributes read-only diagnostics and offline copy generation.
The experimental scripts used to change display modes or install the override
are not included. Persistent installation, calibration, browser behavior, and
other hardware combinations still need validation.

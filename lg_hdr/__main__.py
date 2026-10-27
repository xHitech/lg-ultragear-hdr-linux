"""CLI that only reads inputs and, when requested, writes a new regular file."""
import argparse
import json
import os
from pathlib import Path
import sys
from .edid import EdidError, inspect, patch


MAX_EDID_BYTES = 128 * 256  # Base block plus at most 255 extension blocks.


def read_edid(path: Path) -> bytes:
    with path.open('rb') as source:
        data = source.read(MAX_EDID_BYTES + 1)
    if len(data) > MAX_EDID_BYTES:
        raise EdidError(f'EDID exceeds the {MAX_EDID_BYTES}-byte size limit.')
    return data


def regular_output(path: Path, data: bytes):
    # Avoid accidental device/firmware writes, including through a symlinked parent.
    resolved = path.resolve()
    allowed = (Path.home().resolve(), Path('/tmp').resolve())
    if not any(resolved.is_relative_to(root) for root in allowed):
        raise EdidError('Output must be inside your home directory or /tmp.')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'wb') as f:
        f.write(data)


def doctor(drm_root: Path):
    result = {'read_only': True, 'displays': [], 'limitations': [
        'Does not measure colors or luminance and does not validate browser playback.',
        'Does not enable HDR, install firmware, invoke sudo, or change the system.']}
    if not drm_root.is_dir():
        raise EdidError('DRM directory is unavailable in this environment.')
    for connector in sorted(drm_root.glob('card*-*')):
        # Report connected outputs without serial numbers or raw EDID bytes.
        try:
            if (connector/'status').read_text().strip() != 'connected':
                continue
            result['displays'].append({'connector': connector.name,
                                       'edid': inspect(read_edid(connector/'edid'))})
        except (OSError, EdidError) as e:
            result['displays'].append({'connector': connector.name, 'error': str(e)})
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description='Read-only HDR diagnostics and offline LG EDID correction.')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('inspect', help='Inspect a file or sysfs EDID; no changes.')
    p.add_argument('input', type=Path)
    p = sub.add_parser('patch', help='Write a corrected copy; never installs or activates it.')
    p.add_argument('input', type=Path)
    p.add_argument('output', type=Path)
    sub.add_parser('doctor', help='Read connected displays without changing their configuration.')
    args = parser.parse_args(argv)
    try:
        exit_code = 0
        if os.geteuid() == 0:
            raise EdidError('Run without sudo. This offline tool does not need root.')
        if args.command == 'doctor':
            result = doctor(Path('/sys/class/drm'))
            if any('error' in display for display in result['displays']):
                exit_code = 2
        else:
            data = read_edid(args.input)
            if args.command == 'inspect':
                result = inspect(data)
            else:
                corrected, changes = patch(data)
                regular_output(args.output, corrected)
                result = {'output': str(args.output), 'installed': False,
                          'changes': changes, 'edid': inspect(corrected)}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return exit_code
    except (EdidError, OSError) as e:
        print(f'Error: {e}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())

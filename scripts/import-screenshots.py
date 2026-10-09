#!/usr/bin/env python3
"""Import Unity captures and their provenance after validating the entire selection."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import struct
import tempfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SHOTS = {
    'cover': ('project-cdx-junction', 'junction-remastered', 'scene-view', 4 / 3),
    'gameplay': ('project-cdx-gameplay', 'junction-remastered', 'game-view', 16 / 9),
    'overview': ('project-cdx-junction-overview', 'junction-remastered', 'scene-view', 16 / 9),
    'starlight': ('project-cdx-starlight-park', 'starlight-park', 'scene-view', 16 / 9),
}


def png_size(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    offset = 8
    size = None
    image_data = False
    while offset + 12 <= len(data):
        length = struct.unpack_from('>I', data, offset)[0]
        end = offset + 12 + length
        if end > len(data):
            raise ValueError('incomplete PNG')
        chunk = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        crc = struct.unpack_from('>I', data, offset + 8 + length)[0]
        if zlib.crc32(chunk + payload) & 0xffffffff != crc:
            raise ValueError('PNG checksum mismatch')
        if offset == 8:
            if chunk != b'IHDR' or length != 13:
                raise ValueError('missing PNG header')
            size = struct.unpack_from('>II', payload)
        image_data |= chunk == b'IDAT' and length > 0
        if chunk == b'IEND':
            if length or end != len(data) or not image_data:
                raise ValueError('invalid PNG ending')
            return size
        offset = end
    raise ValueError('missing PNG ending')


def read_capture(directory, shot):
    name, map_id, view, ratio = SHOTS[shot]
    data = (directory / f'{name}.png').read_bytes()
    info = json.loads((directory / f'{name}.json').read_text(encoding='utf-8'))
    width, height = png_size(data)
    if width < 1280 or height < 720 or abs(width / height - ratio) > .02:
        raise ValueError(f'{name}: expected at least 1280x720 and aspect ratio {ratio:.3f}')
    allowed_views = (view, 'world-camera') if view == 'scene-view' else (view,)
    if (info.get('source'), info.get('mapId'), info.get('gameModeId')) != (
            'unity-editor-play-mode', map_id, 'hardpoint') or info.get('view') not in allowed_views:
        raise ValueError(f'{name}: capture source, map, mode or view does not match this image slot')
    if (info.get('width'), info.get('height')) != (width, height):
        raise ValueError(f'{name}: dimensions do not match metadata')
    if info.get('sha256') != hashlib.sha256(data).hexdigest():
        raise ValueError(f'{name}: image does not match metadata hash')
    if not isinstance(info.get('version'), str) or not info['version'].strip():
        raise ValueError(f'{name}: missing version')
    if not isinstance(info.get('frame'), int) or info['frame'] < 2:
        raise ValueError(f'{name}: missing running frame count')
    captured = dt.datetime.fromisoformat(info['capturedUtc'].replace('Z', '+00:00'))
    if captured.tzinfo is None:
        raise ValueError(f'{name}: capture time must include a time zone')
    return name, data, info


def write_atomic(path, data):
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temporary:
        temporary.write(data)
        temporary_path = Path(temporary.name)
    try:
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path, help='fps-cdx/validation-logs/site-screenshots')
    parser.add_argument('--shot', action='append', choices=SHOTS, help='Import only this slot; may be repeated.')
    args = parser.parse_args()
    selected = list(dict.fromkeys(args.shot or SHOTS))
    # Read and validate every image before replacing any site files.
    captures = [read_capture(args.directory, shot) for shot in selected]
    if len({info['version'] for _, _, info in captures}) != 1:
        raise ValueError('selected screenshots have different versions; capture them from the same version')
    manifest_path = ROOT / 'config/screenshots.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    for name, data, info in captures:
        write_atomic(ROOT / 'public/assets' / f'{name}.png', data)
        manifest[name] = info
    write_atomic(manifest_path, (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    for name, _, info in captures:
        print(f'Imported {name}.png: {info["width"]}x{info["height"]}, version {info["version"]}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f'Screenshot import failed: {error}')

#!/usr/bin/env python3
"""Archive local work and ignored raw evidence for an offline team handoff."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import time
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {'.git', '.codex', '.agents', '__pycache__', '.pytest_cache',
             '.venv', 'venv', 'node_modules'}
SECRET_NAMES = {'.env', 'credentials', 'id_rsa', 'id_ed25519', 'id_ecdsa'}
SECRET_SUFFIXES = {'.pem', '.p12', '.pfx', '.key'}
TEXT_SUFFIXES = {'.py', '.md', '.json', '.yaml', '.yml', '.log', '.txt', '.csv',
                 '.sh', '.ps1', '.toml', '.patch', '.diff', '.cfg', '.ini',
                 '.out', '.stderr', '.stdout'}
SECRET_PATTERNS = [
    re.compile(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----'),
    re.compile(rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b'),
    re.compile(rb'\bgithub_pat_[A-Za-z0-9_]{30,}\b'),
    re.compile(rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b'),
]


def inventory():
    paths, excluded, links = [], [], []

    def keep_link(path):
        target = path.resolve(strict=False)
        if not target.is_relative_to(ROOT):
            raise ValueError('symlink target outside project: ' + path.relative_to(ROOT).as_posix())
        links.append(path)

    for base, directories, names in os.walk(ROOT, followlinks=False):
        parent = Path(base)
        keep = []
        for name in sorted(directories):
            path = parent / name
            rel = path.relative_to(ROOT).as_posix()
            if name in SKIP_DIRS or rel == 'output/handoff':
                excluded.append({'path': rel, 'reason': 'metadata, generated cache, or archive output'})
            elif path.is_symlink():
                keep_link(path)
            else:
                keep.append(name)
        directories[:] = keep
        for name in sorted(names):
            path = parent / name
            rel = path.relative_to(ROOT).as_posix()
            if path.is_symlink():
                keep_link(path)
                continue
            if (name in SECRET_NAMES or name.startswith('.env.') or
                    any(name.startswith(prefix + '_') for prefix in ['id_rsa', 'id_ed25519', 'id_ecdsa']) or
                    path.suffix.lower() in SECRET_SUFFIXES):
                raise ValueError('credential-like file requires explicit exclusion: ' + rel)
            if path.suffix.lower() in {'.pyc', '.pyo'}:
                continue
            if not path.resolve().is_relative_to(ROOT):
                raise ValueError('path outside project: ' + rel)
            paths.append(path)
    return paths, excluded, links


def zip_info(path, relative):
    metadata = path.lstat()
    date = time.localtime(metadata.st_mtime)[:6]
    if date[0] < 1980:
        date = (1980, 1, 1, 0, 0, 0)
    info = zipfile.ZipInfo(relative, date_time=date)
    info.create_system = 3
    info.external_attr = (metadata.st_mode & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    paths, excluded, links = inventory()
    scanned = 0
    for path in paths:
        if path.suffix.lower() in TEXT_SUFFIXES and path.stat().st_size <= 16 * 1024 * 1024:
            data = path.read_bytes()
            if any(pattern.search(data) for pattern in SECRET_PATTERNS):
                raise ValueError('possible secret pattern; no contents printed: ' + path.relative_to(ROOT).as_posix())
            scanned += 1
    if args.dry_run:
        print(json.dumps({'status': 'ready', 'files': len(paths),
                          'bytes': sum(path.stat().st_size for path in paths),
                          'symlinks': len(links), 'text_files_scanned': scanned,
                          'excluded_directories_or_links': len(excluded)}))
        return
    run = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    folder = ROOT / 'output/handoff'
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / ('minicpm-s2-work-' + run + '.zip')
    manifest_path = folder / ('minicpm-s2-work-' + run + '-manifest.json')
    if archive.exists() or manifest_path.exists():
        raise FileExistsError('handoff timestamp already exists')
    manifest = {'created_utc': run, 'purpose': 'offline complete-work handoff; not a Git push',
                'source_root': str(ROOT), 'excluded': excluded,
                'text_files_scanned': scanned, 'files': {}}
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for path in paths:
            before = path.stat()
            digest = hashlib.sha256()
            rel = path.relative_to(ROOT).as_posix()
            with path.open('rb') as source, bundle.open(zip_info(path, rel), 'w', force_zip64=True) as dest:
                for chunk in iter(lambda: source.read(1024 * 1024), b''):
                    digest.update(chunk)
                    dest.write(chunk)
            after = path.stat()
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise RuntimeError('file changed during archive; preserve failed archive: ' + rel)
            manifest['files'][rel] = {'kind': 'file', 'bytes': after.st_size,
                                      'sha256': digest.hexdigest(), 'mtime_ns': after.st_mtime_ns,
                                      'mode': oct(after.st_mode)}
        for path in links:
            rel = path.relative_to(ROOT).as_posix()
            target = os.readlink(path)
            encoded_target = target.encode('utf-8')
            bundle.writestr(zip_info(path, rel), encoded_target)
            manifest['files'][rel] = {'kind': 'symlink', 'target': target,
                                      'bytes': len(encoded_target),
                                      'sha256': hashlib.sha256(encoded_target).hexdigest(),
                                      'resolved_project_path': path.resolve(strict=False).relative_to(ROOT).as_posix(),
                                      'mode': oct(path.lstat().st_mode)}
        encoded = json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8')
        bundle.writestr('HANDOFF_FILE_MANIFEST.json', encoded)
    manifest_path.write_bytes(encoded)
    with zipfile.ZipFile(archive) as bundle:
        bad = bundle.testzip()
        if bad:
            raise RuntimeError('archive CRC check failed: ' + bad)
    with archive.open('rb') as handle:
        archive_sha = hashlib.file_digest(handle, 'sha256').hexdigest()
    summary = {'status': 'archived', 'archive': str(archive), 'manifest': str(manifest_path),
               'files': len(paths), 'symlinks': len(links),
               'bytes': archive.stat().st_size, 'sha256': archive_sha,
               'zip_crc_check': 'pass'}
    (folder / ('minicpm-s2-work-' + run + '-summary.json')).write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

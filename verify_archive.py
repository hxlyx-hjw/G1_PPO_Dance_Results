"""Verify every file in the complete package against FILES.sha256."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "FILES.sha256"
EXCLUDED_PARTS = {".venv", ".venv-clean", "__pycache__", ".pytest_cache"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_NAMES = {"FILES.sha256"}


def files() -> list[Path]:
    result = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED_PARTS for part in relative.parts):
            continue
        if path.suffix in EXCLUDED_SUFFIXES or path.name in EXCLUDED_NAMES:
            continue
        result.append(path)
    return sorted(result, key=lambda path: path.relative_to(ROOT).as_posix())


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def write_manifest() -> None:
    lines = [f"{digest(path)}  {path.relative_to(ROOT).as_posix()}" for path in files()]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {len(lines)} entries to {MANIFEST}")


def verify() -> int:
    if not MANIFEST.is_file():
        print(f"missing manifest: {MANIFEST}", file=sys.stderr)
        return 2
    expected = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        checksum, relative = line.split("  ", 1)
        expected[relative] = checksum
    missing = []
    mismatch = []
    for relative, checksum in expected.items():
        path = ROOT / relative
        if not path.is_file():
            missing.append(relative)
        elif digest(path) != checksum:
            mismatch.append(relative)
    extra = [
        path.relative_to(ROOT).as_posix()
        for path in files()
        if path.relative_to(ROOT).as_posix() not in expected
    ]
    print(f"manifest entries: {len(expected)}")
    print(f"missing: {len(missing)}")
    print(f"mismatch: {len(mismatch)}")
    print(f"extra (allowed): {len(extra)}")
    if missing:
        print("MISSING FILES:", *missing[:30], sep="\n  ")
    if mismatch:
        print("MISMATCH FILES:", *mismatch[:30], sep="\n  ")
    if missing or mismatch:
        print("ARCHIVE VERIFY FAIL")
        return 1
    print("ARCHIVE VERIFY PASS")
    return 0


if __name__ == "__main__":
    if "--write" in sys.argv:
        write_manifest()
    else:
        raise SystemExit(verify())

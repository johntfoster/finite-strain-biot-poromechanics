#!/usr/bin/env python3
"""Synchronize the nonlinear-Biot MOOSE closure without silent overwrites."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


MASTER_MANIFEST = Path("release_specs/nonlinear_biot_ad_sync.json")
BIOT_MANIFEST = Path("moose/sync_manifest.json")
LOCAL_MASTER_POINTER = Path(".agent-runtime/master_repository")


class SyncError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise SyncError(f"missing file: {path}") from error
    except json.JSONDecodeError as error:
        raise SyncError(f"invalid JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise SyncError(f"expected a JSON object: {path}")
    return value


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def git_root(start: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=start,
        text=True,
        capture_output=True,
        check=False,
    )
    return Path(result.stdout.strip()).resolve() if result.returncode == 0 else None


def git_commit(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True, capture_output=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else "uncommitted-repository"


def resolve_biot(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    candidate = git_root(Path.cwd())
    if candidate and (
        (candidate / BIOT_MANIFEST).is_file()
        or ((candidate / "paper/main.tex").is_file() and not (candidate / MASTER_MANIFEST).is_file())
    ):
        return candidate
    value = os.environ.get("BIOT_AD_REPOSITORY_ROOT")
    if value:
        return Path(value).resolve()
    raise SyncError("supply --biot or set BIOT_AD_REPOSITORY_ROOT")


def resolve_master(explicit: str | None, biot: Path | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    candidate = git_root(Path.cwd())
    if candidate and (candidate / MASTER_MANIFEST).is_file():
        return candidate
    value = os.environ.get("BIOT_MOOSE_MASTER_ROOT")
    if value:
        return Path(value).resolve()
    if biot and (biot / LOCAL_MASTER_POINTER).is_file():
        return Path((biot / LOCAL_MASTER_POINTER).read_text(encoding="utf-8").strip()).resolve()
    raise SyncError(
        "supply --master, set BIOT_MOOSE_MASTER_ROOT, or run pull once with --master"
    )


def validate_manifest(manifest: dict) -> list[dict[str, str]]:
    if manifest.get("version") != 1 or not isinstance(manifest.get("files"), list):
        raise SyncError("unsupported synchronization manifest")
    files = manifest["files"]
    seen_master: set[str] = set()
    seen_biot: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"master", "biot"}:
            raise SyncError("each file mapping must contain only master and biot")
        for key in ("master", "biot"):
            path = Path(entry[key])
            if path.is_absolute() or ".." in path.parts:
                raise SyncError(f"nonportable {key} path: {entry[key]}")
        if entry["master"] in seen_master or entry["biot"] in seen_biot:
            raise SyncError(f"duplicate synchronization mapping: {entry}")
        seen_master.add(entry["master"])
        seen_biot.add(entry["biot"])
    return files


def state_entries(state: dict | None) -> dict[str, dict]:
    if not state:
        return {}
    return {entry["biot"]: entry for entry in state.get("files", [])}


def write_state(master: Path, biot: Path, manifest: dict, files: list[dict[str, str]]) -> None:
    records = []
    for entry in files:
        master_path = master / entry["master"]
        biot_path = biot / entry["biot"]
        if not master_path.is_file() or not biot_path.is_file():
            raise SyncError(f"cannot record missing synchronized file: {entry}")
        master_hash = digest(master_path)
        biot_hash = digest(biot_path)
        if master_hash != biot_hash:
            raise SyncError(f"synchronized files still differ: {entry['biot']}")
        records.append({**entry, "sha256": master_hash})
    state_path = biot / manifest["state_path"]
    atomic_json(
        state_path,
        {
            "version": 1,
            "master_commit": git_commit(master),
            "manifest_sha256": digest(master / MASTER_MANIFEST),
            "synchronized_at_utc": datetime.now(timezone.utc).isoformat(),
            "files": records,
        },
    )


def pull(master: Path, biot: Path) -> None:
    manifest_path = master / MASTER_MANIFEST
    manifest = load_json(manifest_path)
    files = validate_manifest(manifest)
    state_path = biot / manifest["state_path"]
    previous = load_json(state_path) if state_path.is_file() else None
    previous_by_path = state_entries(previous)

    conflicts = []
    for entry in files:
        source = master / entry["master"]
        destination = biot / entry["biot"]
        if not source.is_file():
            raise SyncError(f"missing master source: {entry['master']}")
        old = previous_by_path.get(entry["biot"])
        if destination.is_file() and old:
            current_hash = digest(destination)
            if current_hash != old["sha256"] and current_hash != digest(source):
                conflicts.append(entry["biot"])
    if conflicts:
        raise SyncError("Biot-side changes require push before pull: " + ", ".join(conflicts))

    for entry in files:
        source = master / entry["master"]
        destination = biot / entry["biot"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    local_manifest = biot / manifest["local_manifest_path"]
    local_manifest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(manifest_path, local_manifest)
    write_state(master, biot, manifest, files)
    pointer = biot / LOCAL_MASTER_POINTER
    pointer.parent.mkdir(parents=True, exist_ok=True)
    pointer.write_text(str(master) + "\n", encoding="utf-8")
    print(f"pulled {len(files)} files from {master} into {biot}")


def push(master: Path, biot: Path) -> None:
    manifest = load_json(master / MASTER_MANIFEST)
    files = validate_manifest(manifest)
    state = load_json(biot / manifest["state_path"])
    previous_by_path = state_entries(state)
    manifest_paths = {entry["biot"] for entry in files}
    removed_paths = set(previous_by_path) - manifest_paths
    if removed_paths:
        raise SyncError(
            "current master manifest removes recorded synchronized files: "
            + ", ".join(sorted(removed_paths))
        )

    conflicts = []
    changed = []
    for entry in files:
        master_path = master / entry["master"]
        biot_path = biot / entry["biot"]
        if not biot_path.is_file():
            raise SyncError(f"missing Biot synchronized file: {entry['biot']}")
        biot_hash = digest(biot_path)
        old = previous_by_path.get(entry["biot"])
        if old is None:
            if master_path.is_file() and digest(master_path) != biot_hash:
                conflicts.append(entry["biot"])
            elif not master_path.is_file():
                changed.append(entry)
            continue
        if not master_path.is_file():
            raise SyncError(f"missing recorded master synchronized file: {entry['master']}")
        base_hash = old["sha256"]
        master_hash = digest(master_path)
        if master_hash != base_hash and master_hash != biot_hash:
            conflicts.append(entry["biot"])
        elif biot_hash != master_hash:
            changed.append(entry)
    if conflicts:
        raise SyncError("master and Biot copies diverged: " + ", ".join(conflicts))

    for entry in changed:
        destination = master / entry["master"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(biot / entry["biot"], destination)
    shutil.copy2(master / MASTER_MANIFEST, biot / manifest["local_manifest_path"])
    write_state(master, biot, manifest, files)
    print(f"pushed {len(changed)} changed files from {biot} into {master}")


def check(master: Path | None, biot: Path) -> None:
    manifest_path = master / MASTER_MANIFEST if master else biot / BIOT_MANIFEST
    manifest = load_json(manifest_path)
    files = validate_manifest(manifest)
    state = load_json(biot / manifest["state_path"])
    if digest(manifest_path) != state.get("manifest_sha256"):
        raise SyncError("synchronization manifest differs from the recorded state")
    previous_by_path = state_entries(state)
    problems = []
    for entry in files:
        biot_path = biot / entry["biot"]
        record = previous_by_path.get(entry["biot"])
        if not biot_path.is_file() or not record:
            problems.append(f"missing Biot copy or state: {entry['biot']}")
            continue
        biot_hash = digest(biot_path)
        if master:
            master_path = master / entry["master"]
            if not master_path.is_file() or digest(master_path) != biot_hash:
                problems.append(f"master/Biot drift: {entry['biot']}")
        elif biot_hash != record["sha256"]:
            problems.append(f"Biot copy differs from recorded export: {entry['biot']}")
    if problems:
        raise SyncError("; ".join(problems))
    print(f"PASS {len(files)} synchronized MOOSE files")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("pull", "push", "check"))
    parser.add_argument("--master", help="Path to the authoritative master repository")
    parser.add_argument("--biot", help="Path to the Biot AD repository")
    args = parser.parse_args()

    try:
        biot = resolve_biot(args.biot)
        master = None
        if args.command != "check" or args.master or os.environ.get("BIOT_MOOSE_MASTER_ROOT"):
            master = resolve_master(args.master, biot)
        elif (biot / LOCAL_MASTER_POINTER).is_file():
            candidate = resolve_master(None, biot)
            master = candidate if (candidate / MASTER_MANIFEST).is_file() else None

        if args.command == "pull":
            pull(master, biot)
        elif args.command == "push":
            push(master, biot)
        else:
            check(master, biot)
    except (OSError, SyncError, KeyError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

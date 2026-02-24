#!/usr/bin/env python3
"""Create ES-DE "directories interpreted as files" structures for multi-disc ROM sets.

This tool scans a ROM directory, groups files that belong to the same multi-disc game,
creates `<Game>.m3u` directories, moves the related files inside, and writes a matching
`<Game>.m3u` playlist file in that folder.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


# Extensions that are generally sidecar/support files, not primary launch files.
SIDECAR_EXTENSIONS = {
    ".ape",
    ".bin",
    ".ecm",
    ".flac",
    ".sub",
    ".wav",
}

# Extensions to ignore when selecting playlist entries.
NON_ROM_EXTENSIONS = {
    ".bak",
    ".bmp",
    ".db",
    ".gif",
    ".ini",
    ".jpeg",
    ".jpg",
    ".log",
    ".m3u",
    ".md5",
    ".nfo",
    ".pdf",
    ".png",
    ".sfv",
    ".sha1",
    ".sha256",
    ".txt",
    ".webp",
    ".xml",
}
ARCHIVE_EXTENSIONS = {".zip", ".7z"}


DISC_RE = re.compile(
    r"""(?ix)
    (?P<prefix>^|[\s._-])
    (?P<label>disc|disk|cd|dvd)
    \s*(?P<num>\d+|[ivxlcdm]+|[a-d])
    (?P<suffix>$|[\s._-]|[\)\]])
    """
)

DISC_BRACKET_RE = re.compile(
    r"""(?ix)
    [\[(]
    \s*(?:disc|disk|cd|dvd)\s*(?P<num>\d+|[ivxlcdm]+|[a-d])
    \s*[\])]
    """
)

OF_RE = re.compile(r"(?ix)(?P<prefix>^|[\s._-])(?P<num>\d+)\s*(?:of|/)\s*\d+(?P<suffix>$|[\s._-])")

WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class DiscFile:
    path: Path
    group_name: str
    disc_index: int


@dataclass
class Plan:
    group_name: str
    source_parent: Path
    members: list[DiscFile]

    @property
    def folder_name(self) -> str:
        return f"{self.group_name}.m3u"

    @property
    def folder_path(self) -> Path:
        return self.source_parent / self.folder_name

    @property
    def playlist_path(self) -> Path:
        return self.folder_path / self.folder_name


class Logger:
    def __init__(self, verbose: bool) -> None:
        self.verbose = verbose

    def info(self, message: str) -> None:
        print(message)

    def debug(self, message: str) -> None:
        if self.verbose:
            print(message)

    def warn(self, message: str) -> None:
        print(f"WARN: {message}")


@dataclass
class ProcessResult:
    groups_processed: int
    files_moved: int
    files_skipped: int
    archives_extracted: int
    archives_failed: int
    single_disc_renamed: int


def roman_to_int(text: str) -> int:
    values = {"i": 1, "v": 5, "x": 10, "l": 50, "c": 100, "d": 500, "m": 1000}
    result = 0
    previous = 0
    for char in reversed(text.lower()):
        value = values.get(char, 0)
        if value < previous:
            result -= value
        else:
            result += value
            previous = value
    return result


def disc_token_to_int(token: str) -> int | None:
    token = token.strip().lower()
    if token.isdigit():
        return int(token)
    if re.fullmatch(r"[a-d]", token):
        return ord(token) - ord("a") + 1
    if re.fullmatch(r"[ivxlcdm]+", token):
        value = roman_to_int(token)
        if value > 0:
            return value
    return None


def clean_group_name(stem: str) -> str:
    cleaned = stem.strip(" -._")
    cleaned = WHITESPACE_RE.sub(" ", cleaned).strip()
    return cleaned


def extract_group_and_disc(stem: str) -> tuple[str, int] | None:
    bracket_match = DISC_BRACKET_RE.search(stem)
    if bracket_match:
        idx = disc_token_to_int(bracket_match.group("num"))
        if idx is not None:
            group = DISC_BRACKET_RE.sub("", stem, count=1)
            group = clean_group_name(group)
            if group:
                return group, idx

    match = DISC_RE.search(stem)
    if match:
        idx = disc_token_to_int(match.group("num"))
        if idx is not None:
            start, end = match.span()
            group = f"{stem[:start]} {stem[end:]}"
            group = clean_group_name(group)
            if group:
                return group, idx

    of_match = OF_RE.search(stem)
    if of_match:
        idx = disc_token_to_int(of_match.group("num"))
        if idx is not None:
            start, end = of_match.span()
            group = f"{stem[:start]} {stem[end:]}"
            group = clean_group_name(group)
            if group:
                return group, idx

    return None


def iter_candidate_files(root: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    for path in root.glob(pattern):
        if not path.is_file():
            continue
        if path.suffix.lower() == ".m3u":
            continue
        yield path


def iter_archives(root: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    for path in root.glob(pattern):
        if path.is_file() and path.suffix.lower() in ARCHIVE_EXTENSIONS:
            yield path


def _find_7z_executable() -> str | None:
    for candidate in ("7z", "7zz", "7za", "7zr"):
        exe = shutil.which(candidate)
        if exe:
            return exe
    return None


def _maybe_suffix_single_disc_folder(folder: Path, dry_run: bool, logger: Logger) -> tuple[bool, Path]:
    """Rename single-disc folder to launcher filename (prefer .cue) for ES-DE directory-as-file support."""
    if not folder.exists() or not folder.is_dir() or folder.suffix:
        return False, folder
    try:
        entries = list(folder.iterdir())
    except OSError:
        return False, folder

    top_files = [p for p in entries if p.is_file()]
    if not top_files:
        return False, folder

    launch_exts = {
        ".cue", ".chd", ".iso", ".rvz", ".gdi", ".ccd", ".mds",
        ".pbp", ".cso", ".wbfs", ".wia", ".img", ".mdf",
    }
    launchers = [p for p in top_files if p.suffix.lower() in launch_exts]
    cues = [p for p in launchers if p.suffix.lower() == ".cue"]

    if len(cues) == 1:
        target_name = cues[0].name
    elif len(launchers) == 1:
        target_name = launchers[0].name
    else:
        return False, folder

    target = folder.with_name(target_name)
    if target.exists():
        logger.warn(f"Post-process rename skipped: {target.name} already exists")
        return False, folder
    if dry_run:
        logger.info(f"  RENAME {folder.name} -> {target.name}")
        return True, target
    try:
        folder.rename(target)
        logger.info(f"  renamed: {folder.name} -> {target.name}")
        return True, target
    except OSError as e:
        logger.warn(f"Post-process rename failed for {folder.name}: {e}")
        return False, folder


def postprocess_single_disc_folders(root: Path, recursive: bool, dry_run: bool, logger: Logger) -> int:
    """Apply single-disc directory-as-file rename convention under root."""
    renamed = 0
    if recursive:
        try:
            subdirs = [p for p in root.rglob("*") if p.is_dir()]
        except OSError:
            subdirs = []
        for subdir in sorted(subdirs, key=lambda p: len(p.parts), reverse=True):
            if subdir.name.lower().endswith(".m3u"):
                continue
            did, _ = _maybe_suffix_single_disc_folder(subdir, dry_run, logger)
            if did:
                renamed += 1
    did_root, _ = _maybe_suffix_single_disc_folder(root, dry_run, logger)
    if did_root:
        renamed += 1
    return renamed


def extract_archive(archive_path: Path, dry_run: bool, delete_archive: bool, logger: Logger) -> tuple[bool, Path | None]:
    output_dir = archive_path.parent / archive_path.stem
    if dry_run:
        logger.info(f"  EXTRACT {archive_path.name} -> {output_dir.name}/")
        if delete_archive:
            logger.info(f"  DELETE {archive_path.name} (after extract)")
        return True, output_dir

    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = archive_path.suffix.lower()
    try:
        if suffix == ".zip":
            with zipfile.ZipFile(archive_path, "r") as zf:
                zf.extractall(output_dir)
        elif suffix == ".7z":
            exe = _find_7z_executable()
            if not exe:
                logger.warn(f"Skipping {archive_path.name}: 7z executable not found")
                return False, None
            proc = subprocess.run(  # noqa: S603
                [exe, "x", "-y", f"-o{output_dir}", str(archive_path)],
                capture_output=True,
                text=True,
                timeout=1800,
                check=False,
            )
            if proc.returncode != 0:
                err = (proc.stderr or proc.stdout or "").strip() or "7z extraction failed"
                logger.warn(f"Failed extracting {archive_path.name}: {err}")
                return False, None
        else:
            return False, None

        if delete_archive:
            try:
                archive_path.unlink()
            except OSError as e:
                logger.warn(f"Extracted {archive_path.name} but failed to delete archive: {e}")
        logger.info(f"  extracted: {archive_path.name}")
        return True, output_dir
    except (OSError, zipfile.BadZipFile, subprocess.TimeoutExpired) as e:
        logger.warn(f"Failed extracting {archive_path.name}: {e}")
        return False, None


def build_plans(root: Path, recursive: bool, logger: Logger) -> list[Plan]:
    grouped: dict[tuple[Path, str], list[DiscFile]] = {}

    for path in iter_candidate_files(root, recursive):
        parsed = extract_group_and_disc(path.stem)
        if not parsed:
            continue
        group_name, disc_index = parsed
        key = (path.parent, group_name)
        grouped.setdefault(key, []).append(DiscFile(path=path, group_name=group_name, disc_index=disc_index))

    plans: list[Plan] = []
    for (parent, group_name), members in grouped.items():
        unique_discs = {m.disc_index for m in members}
        if len(unique_discs) < 2:
            logger.debug(f"Skipping single-disc or ambiguous group: {group_name}")
            continue
        members.sort(key=lambda m: (m.disc_index, m.path.name.lower()))
        plans.append(Plan(group_name=group_name, source_parent=parent, members=members))

    plans.sort(key=lambda p: (str(p.source_parent).lower(), p.group_name.lower()))
    return plans


def relative_name_for_playlist(path: Path, folder_path: Path) -> str:
    try:
        return path.relative_to(folder_path).as_posix()
    except ValueError:
        return path.name


def choose_playlist_entries(members: list[DiscFile], folder_path: Path) -> list[str]:
    by_disc: dict[int, list[Path]] = {}
    for member in members:
        moved_path = folder_path / member.path.name
        by_disc.setdefault(member.disc_index, []).append(moved_path)

    entries: list[str] = []
    for disc in sorted(by_disc):
        disc_files = sorted(by_disc[disc], key=lambda p: p.name.lower())
        cue = [p for p in disc_files if p.suffix.lower() == ".cue"]
        if cue:
            entries.append(relative_name_for_playlist(cue[0], folder_path))
            continue

        launchable = [
            p for p in disc_files
            if p.suffix.lower() not in SIDECAR_EXTENSIONS and p.suffix.lower() not in NON_ROM_EXTENSIONS
        ]
        if not launchable:
            launchable = [p for p in disc_files if p.suffix.lower() not in NON_ROM_EXTENSIONS]
        if launchable:
            entries.append(relative_name_for_playlist(launchable[0], folder_path))

    return entries


def execute_plan(plan: Plan, dry_run: bool, logger: Logger) -> tuple[int, int]:
    moved = 0
    skipped = 0

    logger.info(f"\n[{plan.group_name}] -> {plan.folder_path}")

    if not dry_run:
        plan.folder_path.mkdir(parents=True, exist_ok=True)

    for member in plan.members:
        src = member.path
        dest = plan.folder_path / src.name

        if src.resolve() == dest.resolve():
            skipped += 1
            logger.debug(f"Already in place: {src}")
            continue

        if dest.exists():
            skipped += 1
            logger.warn(f"Destination exists, skipping move: {dest}")
            continue

        if dry_run:
            logger.info(f"  MOVE {src.name} -> {plan.folder_name}/{dest.name}")
            moved += 1
        else:
            shutil.move(str(src), str(dest))
            logger.info(f"  moved: {src.name}")
            moved += 1

    entries = choose_playlist_entries(plan.members, plan.folder_path)
    if not entries:
        logger.warn("No launchable disc files found for playlist; skipping .m3u write")
        return moved, skipped

    contents = "\n".join(entries) + "\n"
    if dry_run:
        logger.info(f"  WRITE {plan.playlist_path.name} ({len(entries)} entries)")
    else:
        plan.playlist_path.write_text(contents, encoding="utf-8", newline="\n")
        logger.info(f"  wrote playlist: {plan.playlist_path.name}")

    return moved, skipped


def process_library(
    root: Path,
    recursive: bool,
    dry_run: bool,
    logger: Logger,
    extract_archives_first: bool = False,
    delete_archives_after_extract: bool = False,
    postprocess_single_disc: bool = False,
) -> ProcessResult:
    archives_extracted = 0
    archives_failed = 0
    single_disc_renamed = 0
    extracted_roots: list[Path] = []

    if extract_archives_first:
        archives = sorted(iter_archives(root, recursive), key=lambda p: str(p).lower())
        if archives:
            logger.info(f"Found {len(archives)} archive(s) to extract.")
            for archive in archives:
                ok, out_dir = extract_archive(archive, dry_run, delete_archives_after_extract, logger)
                if ok:
                    archives_extracted += 1
                    if out_dir is not None:
                        extracted_roots.append(out_dir)
                else:
                    archives_failed += 1

    if postprocess_single_disc:
        logger.info("Running single-disc post-process...")
        single_disc_renamed += postprocess_single_disc_folders(
            root=root, recursive=recursive, dry_run=dry_run, logger=logger
        )
        if extract_archives_first:
            for out_dir in extracted_roots:
                if out_dir.exists() or dry_run:
                    single_disc_renamed += postprocess_single_disc_folders(
                        root=out_dir, recursive=True, dry_run=dry_run, logger=logger
                    )

    plans = build_plans(root, recursive=recursive, logger=logger)

    # If not scanning recursively, also process freshly extracted subfolders.
    if extract_archives_first and not recursive:
        for out_dir in extracted_roots:
            if out_dir.exists() or dry_run:
                plans.extend(build_plans(out_dir, recursive=True, logger=logger))

    if not plans:
        return ProcessResult(
            groups_processed=0,
            files_moved=0,
            files_skipped=0,
            archives_extracted=archives_extracted,
            archives_failed=archives_failed,
            single_disc_renamed=single_disc_renamed,
        )

    dedup: dict[tuple[str, str], Plan] = {}
    for plan in plans:
        key = (str(plan.source_parent).lower(), plan.group_name.lower())
        dedup[key] = plan
    plans = sorted(dedup.values(), key=lambda p: (str(p.source_parent).lower(), p.group_name.lower()))

    logger.info(f"Found {len(plans)} multi-disc groups.")
    total_moved = 0
    total_skipped = 0
    for plan in plans:
        moved, skipped = execute_plan(plan, dry_run=dry_run, logger=logger)
        total_moved += moved
        total_skipped += skipped

    return ProcessResult(
        groups_processed=len(plans),
        files_moved=total_moved,
        files_skipped=total_skipped,
        archives_extracted=archives_extracted,
        archives_failed=archives_failed,
        single_disc_renamed=single_disc_renamed,
    )


def pick_folder_with_tk() -> Path | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception:
        return None

    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    selected = filedialog.askdirectory(title="Select ROM folder")
    root.destroy()
    if not selected:
        return None
    return Path(selected)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create ES-DE .m3u directory structures for multi-disc ROM sets."
    )
    parser.add_argument(
        "roms_dir",
        nargs="?",
        type=Path,
        help="ROM folder to scan. If omitted, use --pick-folder.",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Scan subfolders recursively.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without moving files.",
    )
    parser.add_argument(
        "--pick-folder",
        action="store_true",
        help="Open a folder picker dialog to choose ROM directory.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show additional debug output.",
    )
    parser.add_argument(
        "--extract-archives",
        action="store_true",
        help="Extract .zip/.7z archives before creating ES-DE structures.",
    )
    parser.add_argument(
        "--delete-archives",
        action="store_true",
        help="Delete archives after successful extraction (only with --extract-archives).",
    )
    parser.add_argument(
        "--postprocess-single-disc",
        action="store_true",
        help="Rename single-disc folders to launcher filename (e.g. Game -> Game.cue).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    logger = Logger(verbose=args.verbose)

    root = args.roms_dir
    if args.pick_folder:
        root = pick_folder_with_tk()

    if root is None:
        print("ERROR: Provide a ROM folder path or use --pick-folder.")
        return 2

    root = root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"ERROR: ROM folder does not exist or is not a directory: {root}")
        return 2

    logger.info(f"Scanning: {root}")
    logger.info(f"Recursive: {'yes' if args.recursive else 'no'}")
    logger.info(f"Mode: {'dry-run' if args.dry_run else 'apply'}")
    logger.info(f"Extract archives: {'yes' if args.extract_archives else 'no'}")
    logger.info(f"Post-process single-disc: {'yes' if args.postprocess_single_disc else 'no'}")

    result = process_library(
        root=root,
        recursive=args.recursive,
        dry_run=args.dry_run,
        logger=logger,
        extract_archives_first=args.extract_archives,
        delete_archives_after_extract=args.delete_archives,
        postprocess_single_disc=args.postprocess_single_disc,
    )
    if result.groups_processed == 0:
        logger.info("No multi-disc groups found. Nothing to do.")

    logger.info("\nDone.")
    logger.info(f"Groups processed: {result.groups_processed}")
    logger.info(f"Files moved: {result.files_moved}")
    logger.info(f"Files skipped: {result.files_skipped}")
    if args.extract_archives:
        logger.info(f"Archives extracted: {result.archives_extracted}")
        logger.info(f"Archive extraction failures: {result.archives_failed}")
    if args.postprocess_single_disc:
        logger.info(f"Single-disc folders renamed: {result.single_disc_renamed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

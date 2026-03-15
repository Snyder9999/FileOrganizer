"""File Organizer — Automated directory decluttering utility.

Scans a target directory, categorises loose files by extension,
moves them into labelled sub-folders, and removes leftover empty
directories.  Supports an optional deep-scan mode that recursively
extracts files from all sub-folders.  Only built-in standard-library
modules are used.

Usage:
    python file_organizer.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Extension → category mapping.
# Keys are lowercase extensions (with leading dot).
EXTENSION_MAP: dict[str, str] = {
    # Images
    ".jpg": "Images",
    ".jpeg": "Images",
    ".png": "Images",
    ".gif": "Images",
    ".svg": "Images",
    # Documents
    ".pdf": "Documents",
    ".docx": "Documents",
    ".txt": "Documents",
    ".xlsx": "Documents",
    ".pptx": "Documents",
    # Media
    ".mp4": "Media",
    ".mp3": "Media",
    ".wav": "Media",
    ".mkv": "Media",
    # Archives
    ".zip": "Archives",
    ".rar": "Archives",
    # .tar.gz is handled as a special case in get_category()
    # Code
    ".py": "Code",
    ".html": "Code",
    ".css": "Code",
    ".js": "Code",
}

DEFAULT_CATEGORY: str = "Others"

# Names of category folders created by this script.
# Used to exclude them from deep-scan traversal.
CATEGORY_NAMES: frozenset[str] = frozenset(
    set(EXTENSION_MAP.values()) | {DEFAULT_CATEGORY}
)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def get_default_desktop() -> Path:
    """Return the platform-independent path to the current user's Desktop.

    Returns:
        Path to the Desktop directory.

    Raises:
        FileNotFoundError: If the Desktop directory does not exist.
    """
    desktop = Path.home() / "Desktop"
    if not desktop.exists():
        raise FileNotFoundError(
            f"Default Desktop directory not found at '{desktop}'. "
            "Please provide a valid directory path."
        )
    return desktop


def get_target_directory() -> Path:
    """Prompt the user for a target directory and validate it.

    If the user presses Enter without typing anything, the system's
    Desktop directory is used as the default.

    Returns:
        A validated Path object pointing to an existing directory.

    Raises:
        SystemExit: If the supplied path is invalid or inaccessible.
    """
    raw_path: str = input(
        "Enter the target directory path (press Enter for Desktop): "
    ).strip()

    if not raw_path:
        try:
            directory = get_default_desktop()
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
            sys.exit(1)
    else:
        directory = Path(raw_path)

    # Validate that the path exists and is a directory.
    if not directory.exists():
        print(f"Error: The path '{directory}' does not exist.")
        sys.exit(1)
    if not directory.is_dir():
        print(f"Error: The path '{directory}' is not a directory.")
        sys.exit(1)

    return directory


def scan_files(directory: Path) -> list[Path]:
    """Return a list of files in the root of *directory* (non-recursive).

    Sub-directories are intentionally ignored so that already-organised
    files are not disturbed.

    Args:
        directory: The directory to scan.

    Returns:
        A list of Path objects representing loose files.
    """
    return [entry for entry in directory.iterdir() if entry.is_file()]


def prompt_deep_scan() -> bool:
    """Ask the user whether to enable recursive deep-scan mode.

    Returns:
        ``True`` if the user opts in (``Y`` / ``y``),
        ``False`` on ``N``, ``n``, or blank Enter (default).
    """
    response: str = input(
        "Do you want to extract and organise files from all "
        "sub-folders as well? (Y/N): "
    ).strip().lower()
    return response == "y"


def deep_scan_files(directory: Path) -> list[Path]:
    """Recursively find every file nested inside *directory*'s sub-folders.

    Uses ``os.walk()`` to traverse all levels.  Files that already
    reside directly inside a known category folder at the root level
    are skipped so they are not re-processed.

    Args:
        directory: The root target directory.

    Returns:
        A list of Path objects for every nested file discovered,
        excluding files that sit directly in the root.
    """
    nested_files: list[Path] = []

    for dirpath_str, _dirnames, filenames in os.walk(directory):
        dirpath = Path(dirpath_str)

        # Skip the root directory itself — those files are handled
        # by the normal (shallow) scan_files() call.
        if dirpath == directory:
            continue

        for filename in filenames:
            nested_files.append(dirpath / filename)

    return nested_files


def get_category(file_path: Path) -> str:
    """Determine the category folder name for a given file.

    Handles the special `.tar.gz` compound extension before falling
    back to the standard single-dot suffix lookup.

    Args:
        file_path: Path to the file whose category is needed.

    Returns:
        A category string such as ``"Images"`` or ``"Others"``.
    """
    # Special case: compound extension .tar.gz
    if file_path.name.lower().endswith(".tar.gz"):
        return "Archives"

    extension: str = file_path.suffix.lower()
    return EXTENSION_MAP.get(extension, DEFAULT_CATEGORY)


def resolve_collision(dest_path: Path) -> Path:
    """Return a non-colliding destination path.

    If *dest_path* already exists, a numeric suffix (``_1``, ``_2``, …)
    is appended to the file stem until a free name is found.

    Args:
        dest_path: The initially desired destination path.

    Returns:
        A Path that does not yet exist on disk.
    """
    if not dest_path.exists():
        return dest_path

    stem: str = dest_path.stem
    suffix: str = dest_path.suffix
    parent: Path = dest_path.parent
    counter: int = 1

    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def move_files(
    directory: Path,
    files: list[Path],
    *,
    show_source_path: bool = False,
) -> int:
    """Move *files* into categorised sub-folders under *directory*.

    Category folders are created on demand.  Filename collisions are
    resolved by appending a numeric suffix.

    Args:
        directory: The root directory that will contain category folders.
        files: The list of file paths to organise.
        show_source_path: If ``True``, print the full original path
            of each file (useful for deep-scan audit trails).

    Returns:
        The number of files successfully moved.
    """
    moved_count: int = 0

    for file_path in files:
        category: str = get_category(file_path)
        category_dir: Path = directory / category

        # Create the category folder if it does not exist yet.
        category_dir.mkdir(exist_ok=True)

        dest_path: Path = category_dir / file_path.name

        # Handle potential filename collisions.
        dest_path = resolve_collision(dest_path)

        try:
            shutil.move(str(file_path), str(dest_path))
            moved_count += 1
            if show_source_path:
                print(
                    f"  Extracted: {file_path}"
                    f"  →  {category}/{dest_path.name}"
                )
            else:
                print(
                    f"  Moved: {file_path.name}"
                    f"  →  {category}/{dest_path.name}"
                )
        except OSError as exc:
            print(f"  Warning: Could not move '{file_path.name}': {exc}")

    return moved_count


def cleanup_empty_folders(directory: Path) -> int:
    """Recursively delete all empty sub-folders inside *directory*.

    Walks the tree **bottom-up** so that deeply nested directories
    emptied by a prior deep-scan extraction are cleaned first,
    allowing their parent directories to become empty in turn and
    be removed in the same pass.

    **Important:** This function never deletes files — only truly
    empty directories are removed, using ``os.rmdir()``.

    Args:
        directory: The root directory to inspect.

    Returns:
        The number of empty folders that were removed.
    """
    removed_count: int = 0

    # os.walk with topdown=False visits the deepest leaves first.
    for dirpath_str, dirnames, filenames in os.walk(
        directory, topdown=False
    ):
        dirpath = Path(dirpath_str)

        # Never attempt to remove the root target directory itself.
        if dirpath == directory:
            continue

        # A folder is empty when it has no files and no sub-dirs.
        try:
            remaining = list(dirpath.iterdir())
        except PermissionError:
            print(
                f"  Warning: Cannot access '{dirpath.name}', skipping."
            )
            continue

        if len(remaining) == 0:
            try:
                os.rmdir(str(dirpath))
                removed_count += 1
                print(f"  Removed empty folder: {dirpath.name}")
            except OSError as exc:
                print(
                    f"  Warning: Could not remove '{dirpath.name}': {exc}"
                )

    return removed_count


# ---------------------------------------------------------------------------
# Main entry-point
# ---------------------------------------------------------------------------


def main() -> None:
    """Orchestrate the full file-organisation workflow.

    1. Get and validate the target directory.
    2. Ask whether to enable deep-scan mode.
    3. Scan for loose files (and nested files if deep scan is on).
    4. Move files into category folders.
    5. Clean up empty directories (bottom-up).
    6. Print a summary.
    """
    print("=" * 55)
    print("  File Organizer — Automated Directory Cleanup")
    print("=" * 55)
    print()

    # Step 1 — Target directory
    directory: Path = get_target_directory()
    print(f"\nTarget directory: {directory}\n")

    # Step 2 — Deep-scan prompt (before any file moves)
    deep_scan: bool = prompt_deep_scan()
    print()

    # Step 3 — Collect files to organise
    files: list[Path] = scan_files(directory)
    moved_count: int = 0
    extracted_count: int = 0

    # If deep scan is enabled, collect nested files NOW — before any
    # root-level moves create new category folders whose contents
    # would otherwise be re-discovered by os.walk().
    nested_files: list[Path] = []
    if deep_scan:
        nested_files = deep_scan_files(directory)

    # Step 4a — Move root-level files
    if files:
        print(f"Found {len(files)} root-level file(s) to organise.\n")
        print("Moving root-level files …")
        moved_count = move_files(directory, files)
    else:
        print("No loose root-level files found.")

    # Step 4b — Extract nested files if deep scan is on
    if deep_scan:
        if nested_files:
            print(
                f"\nDeep scan found {len(nested_files)} nested file(s). "
                "Extracting …"
            )
            extracted_count = move_files(
                directory, nested_files, show_source_path=True
            )
        else:
            print("\nDeep scan: no nested files found.")

    total_moved: int = moved_count + extracted_count

    if total_moved == 0:
        print("\nNothing to organise — the directory is already tidy!")
        return

    # Step 5 — Clean up empty folders (bottom-up recursive)
    print("\nCleaning up empty folders …")
    removed_count: int = cleanup_empty_folders(directory)

    # Step 6 — Summary
    print("\n" + "-" * 55)
    print("  Summary")
    print("-" * 55)
    print(f"  Root files moved     : {moved_count}")
    if deep_scan:
        print(f"  Nested files extracted: {extracted_count}")
    print(f"  Empty folders removed: {removed_count}")
    print("-" * 55)
    print("Done! Your directory is now organised. ✓")


if __name__ == "__main__":
    main()

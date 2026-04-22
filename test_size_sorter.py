from __future__ import annotations

import os
from pathlib import Path

import pytest

from size_sorter import (
    get_size_category,
    get_file_type_category,
    move_files,
    deep_scan_files,
)


def test_get_size_category():
    # 0 to 100KB: < 102400
    assert get_size_category(0) == "0-100KB"
    assert get_size_category(100 * 1024 - 1) == "0-100KB"
    
    # 100KB to 500KB: 102400 to 511999
    assert get_size_category(100 * 1024) == "100KB-500KB"
    assert get_size_category(500 * 1024 - 1) == "100KB-500KB"

    # 500KB to 1MB
    assert get_size_category(500 * 1024) == "500KB-1MB"
    assert get_size_category(1 * 1024 * 1024 - 1) == "500KB-1MB"

    # 1MB to 10MB
    assert get_size_category(1 * 1024 * 1024) == "1MB-10MB"
    assert get_size_category(10 * 1024 * 1024 - 1) == "1MB-10MB"

    # 10MB to 100MB
    assert get_size_category(10 * 1024 * 1024) == "10MB-100MB"
    assert get_size_category(100 * 1024 * 1024) == "10MB-100MB"

    # Over 100MB
    assert get_size_category(100 * 1024 * 1024 + 1) == "Over_100MB"


def test_get_file_type_category():
    img_path = Path("test.jpg")
    vid_path = Path("test.mp4")
    other_path = Path("test.txt")

    # Images only
    assert get_file_type_category(img_path, True, False) == "Images"
    assert get_file_type_category(vid_path, True, False) is None

    # Videos only
    assert get_file_type_category(img_path, False, True) is None
    assert get_file_type_category(vid_path, False, True) == "Videos"

    # Both
    assert get_file_type_category(img_path, True, True) == "Images"
    assert get_file_type_category(vid_path, True, True) == "Videos"
    
    # Neither / Unknown
    assert get_file_type_category(other_path, True, True) is None


def test_move_files_sorting(tmp_path: Path):
    # Create two files with distinct sizes
    file1 = tmp_path / "tiny.jpg"
    file1.write_bytes(b"x" * (50 * 1024))  # 50KB -> 0-100KB
    
    file2 = tmp_path / "medium.mp4"
    file2.write_bytes(b"y" * (600 * 1024)) # 600KB -> 500KB-1MB

    # Sort turning on BOTH flags
    moved = move_files(tmp_path, [file1, file2], True, True)

    assert moved == 2
    assert (tmp_path / "Images" / "0-100KB" / "tiny.jpg").exists()
    assert (tmp_path / "Videos" / "500KB-1MB" / "medium.mp4").exists()


def test_move_files_skips_unselected(tmp_path: Path):
    file1 = tmp_path / "img.png"
    file1.write_bytes(b"x" * 100)
    
    file2 = tmp_path / "vid.mp4"
    file2.write_bytes(b"x" * 100)
    
    # Sort ONLY videos
    moved = move_files(tmp_path, [file1, file2], False, True)
    assert moved == 1
    
    assert (tmp_path / "Videos" / "0-100KB" / "vid.mp4").exists()
    assert file1.exists()  # img.png was ignored, still stays in root.
    

def test_deep_scan_size_sort(tmp_path: Path):
    nested_dir = tmp_path / "HiddenFolder"
    nested_dir.mkdir()
    
    img = nested_dir / "secret.heic"
    img.write_bytes(b"z" * (110 * 1024)) # 110KB -> 100KB-500KB

    nested_files = deep_scan_files(tmp_path)
    # The scan should find the file
    assert len(nested_files) == 1
    
    # Move
    moved = move_files(tmp_path, nested_files, True, True)
    assert moved == 1
    
    # Check
    assert (tmp_path / "Images" / "100KB-500KB" / "secret.heic").exists()
    assert not img.exists()  # Extracted

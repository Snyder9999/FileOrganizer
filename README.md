# File Organizer

A lightweight, automated Python utility designed to effortlessly declutter directories (such as your Desktop or Downloads folder). The File Organizer scans a target directory, categorizes loose files based on their extensions, moves them into designated subfolders, and safely deletes any leftover empty folders to ensure a perfectly clean workspace.

It also features an **Optional Deep Scan** mode to recursively extract and organize files buried within nested subdirectories.

## Features

- **Automated Organization:** Groups files logically by type into clear category folders (`Images/`, `Documents/`, `Media/`, `Archives/`, `Code/`, and `Others/`).
- **Collision Handling:** Safely renames duplicate files (e.g., appending `_1`, `_2`) so you never accidentally overwrite or lose data.
- **Empty Folder Cleanup:** Removes leftover empty directories from your workspace automatically (files are **never** deleted).
- **Deep Scan Mode:** Prompts to optionally traverse all nested subdirectories, extracting hidden files into the root-level category folders.
- **Platform Agnostic:** Runs flawlessly on Windows, macOS, and Linux using built-in standard-library modules (`os`, `shutil`, `pathlib`).

## Technologies Used

- **Language:** Python 3.x
- **Core Libraries:** `os`, `shutil`, `pathlib`, `sys`
- **Testing:** `pytest`

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone <your-repository-url>
   cd FileOrganizer
   ```

2. (Optional but recommended) Ensure you are running Python 3.7 or higher. No external dependencies are required for the main script, but `pytest` is required to run the test suite.
   ```bash
   python -m pip install pytest
   ```

## Usage

Simply run the script from your terminal:

```bash
python file_organizer.py
```

### Flow of Execution:
1. **Target Directory:** You will be prompted to enter the directory you want to organize. Pressing `Enter` without typing anything defaults to your system's `Desktop`.
2. **Deep Scan Prompt:** The script asks: *"Do you want to extract and organise files from all sub-folders as well? (Y/N)"*.
   - **No (Default):** Organizes only root-level loose files.
   - **Yes:** Recursively finds deeply nested files and extracts them into root category folders.
3. **Execution & Cleanup:** Files are moved safely. Empty directories are recursively removed from the bottom up.
4. **Summary:** A summary report is printed to your console, confirming what actions were taken.

## Running Tests

To run the full test suite (41 tests including deep scan integration and collision edge cases):

```bash
python -m pytest test_file_organizer.py -v
```

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature-name`).
3. Make your changes and write additional tests if applicable.
4. Commit your changes (`git commit -m "Add some feature"`).
5. Push to the branch (`git push origin feature/your-feature-name`).
6. Open a Pull Request.

Please ensure all tests pass (`python -m pytest`) before submitting.

## License

This project is licensed under the MIT License - see the [License](LICENSE) file for details.

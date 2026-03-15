# PRD: Python PC Automation Toolkit – File Organizer

**Document Status:** Draft  
**Target Release:** v1.0 (Command Line Interface Version)  
**Tech Stack:** Python 3.x (Built-in libraries: `os`, `shutil`, `pathlib`)  

---

## 1. Product Overview
The File Organizer is a lightweight, automated Python utility designed to declutter directories (such as the Desktop or Downloads folder). It scans a target directory, categorizes loose files based on their extensions, moves them into designated subfolders, and safely deletes any leftover empty folders to ensure a perfectly clean workspace.

## 2. Target Audience
* **The Cluttered User:** Individuals who frequently download or save files to a single location, resulting in a disorganized and overwhelming digital workspace.
* **The Productivity Enthusiast:** Users who want to save time on manual file management through automated, reliable scripts.

## 3. User Stories
* As a user, I want to input a specific folder path so that I can choose exactly which directory gets organized.
* As a user, I want my files automatically grouped by type (e.g., all `.jpg` files go to an "Images" folder) so I can find them easily later.
* As a user, I want the script to automatically delete any folders that are completely empty so my directory doesn't look cluttered with unused folders.
* As a user, I want the script to warn me or safely handle duplicate file names so I don't accidentally overwrite important data.

---

## 4. Functional Requirements

### 4.1. Directory Input and Validation
* The script must prompt the user to enter a target directory path.
* The script must validate that the entered path exists and is accessible.
* If the user presses "Enter" without typing a path, the script should default to the system's Desktop.

### 4.2. File Scanning and Categorization
* The script must read all files in the root of the target directory.
* It must ignore existing subdirectories during the initial file scan (non-recursive) to avoid moving files that are already organized.
* It must map file extensions to predefined category folders. 

> **Category Mapping Examples:**
> * **Images:** `.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`
> * **Documents:** `.pdf`, `.docx`, `.txt`, `.xlsx`, `.pptx`
> * **Media:** `.mp4`, `.mp3`, `.wav`, `.mkv`
> * **Archives:** `.zip`, `.rar`, `.tar.gz`
> * **Code:** `.py`, `.html`, `.css`, `.js`
> * **Others:** Any extension not explicitly mapped.

### 4.3. File Relocation
* The script must dynamically create the category folder if it does not already exist in the target directory.
* The script must physically move the file from the root directory into the corresponding category folder.
* **Collision Handling:** If a file with the exact same name already exists in the destination folder, the script must append a timestamp or a number to the file being moved to prevent data loss.

### 4.4. Empty Folder Cleanup
* After all files are moved, the script must perform a pass over all folders in the target directory.
* It must evaluate the contents of each folder.
* If a folder contains zero items (no files, no hidden files, no subfolders), the script must permanently delete it using the `os.rmdir()` command.

### 4.5. Optional Deep Scan (Recursive File Extraction)
* Before executing the file move operations, the script must explicitly prompt the user: "Do you want to extract and organise files from all sub-folders as well? (Y/N)".
* **If the user selects 'No' (or defaults):** The script will only organize files located in the root of the target directory, leaving subfolders completely untouched.
* **If the user selects 'Yes':** The script must perform a recursive scan (e.g., using `os.walk()`) to locate every single file nested within any subdirectory.
* It must extract these deeply nested files and move them into the main top-level category folders (e.g., pulling a `.jpg` from a nested folder directly into the root `Images/` folder).
* This step must execute *before* the Empty Folder Cleanup (Section 4.4), ensuring that any subfolders emptied by this deep scan are subsequently deleted.
---

## 5. Non-Functional Requirements
* **Performance:** The script must process a directory containing up to 1,000 files in under 5 seconds.
* **Safety:** The script must **never** delete a file. Deletion permissions are strictly limited to empty directories.
* **Platform Agnostic:** The code must execute flawlessly on Windows, macOS, and Linux by utilizing OS-independent path formatting (e.g., using `os.path.join` or `pathlib`).
* **Feedback/Logging:** The console must output a brief summary upon completion, detailing how many files were moved and how many empty folders were removed.

## 6. Future Enhancements (Out of Scope for v1.0)
* Graphical User Interface (GUI) using Tkinter or PyQt.
* A scheduling feature to run the organizer silently in the background every day or week.
* Custom user-defined extension mapping via a settings file.
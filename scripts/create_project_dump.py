import os
import glob
import shutil
from pathlib import Path
import re
import argparse
from typing import Set, List

# Define file extensions to include
INCLUDE_EXTENSIONS = {
    '.py', '.js', '.html', '.css', '.json', '.md', '.yaml', '.yml', '.txt', '.xml',
    '.cpp', '.h', '.rs', '.java', '.c', '.ts', '.tsx', '.go', '.php', '.sql', '.sh', '.bash'
}

# Default dump file
DUMP_FILE = 'dump.txt'


def read_gitignore(project_root: Path) -> tuple[Set[str], Set[str]]:
    gitignore_path = project_root / '.gitignore'
    if not gitignore_path.exists():
        return set(), set()

    with open(gitignore_path, 'r', encoding='utf-8') as f:
        patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    ignored_files = set()
    ignored_directories = set()

    for pattern in patterns:
        pattern = pattern.strip()
        if not pattern:
            continue

        # Handle absolute path
        if pattern.startswith('/'):
            ignored_files.add(pattern[1:])
        # Handle **/folder/*
        elif pattern.startswith('**/'):
            ignored_files.add(pattern[3:])
        # Handle folder pattern (ends with /)
        elif pattern.endswith('/'):
            ignored_directories.add(pattern.rstrip('/'))
        else:
            ignored_files.add(pattern)

        # Expand glob patterns
        try:
            matches = glob.glob(os.path.join('**', pattern), recursive=True)
            for match in matches:
                if os.path.isfile(match):
                    ignored_files.add(match)
        except Exception:
            pass

    return ignored_files, ignored_directories


def is_ignored(filepath: str, ignored_files: Set[str], ignored_directories: Set[str]) -> bool:
    filepath = os.path.normpath(filepath)
    if filepath in ignored_files:
        return True
    for dir_path in Path(filepath).parents:
        if str(dir_path) in ignored_directories:
            return True
    return False


def get_project_files(project_root: Path, ignored_files: Set[str], ignored_directories: Set[str]) -> List[str]:
    files = []
    for root, dirs, filenames in os.walk(project_root):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if not is_ignored(os.path.join(root, d), ignored_files, ignored_directories)]
        for filename in filenames:
            if filename.startswith('.'):
                continue
            file_path = os.path.join(root, filename)
            if is_ignored(file_path, ignored_files, ignored_directories):
                continue
            if any(filename.endswith(ext) for ext in INCLUDE_EXTENSIONS):
                files.append(file_path)
    return sorted(files)


def create_dump(project_root: Path):
    ignored_files, ignored_directories = read_gitignore(project_root)
    project_files = get_project_files(project_root, ignored_files, ignored_directories)
    dump_file = project_root / DUMP_FILE

    with open(dump_file, 'w', encoding='utf-8') as f:
        # Write project structure
        f.write("=== PROJECT STRUCTURE ===\n")
        for root, dirs, files in os.walk(project_root):
            # Only show directories that are not ignored
            if is_ignored(root, ignored_files, ignored_directories):
                continue

            level = root.replace(str(project_root), '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                if file.startswith('.') or is_ignored(os.path.join(root, file), ignored_files, ignored_directories):
                    continue
                f.write(f"{subindent}{file}\n")

        f.write("\n=== CODE FILES ===\n")
        for file_path in project_files:
            f.write(f"\n--- {file_path} ---\n")
            try:
                with open(file_path, 'r', encoding='utf-8') as f2:
                    content = f2.read()
                    f.write(content)
                    f.write("\n\n")
            except Exception as e:
                f.write(f"// Could not read file: {e}\n")

    print(f"✅ Dump created: {dump_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a dump of a project directory, respecting .gitignore.")
    parser.add_argument(
        'path', nargs='?', default=Path.cwd(), help="Path to the project directory (default: current directory)"
    )
    args = parser.parse_args()

    project_root = Path(args.path).resolve()

    if not project_root.exists():
        print(f"❌ Error: Path '{project_root}' does not exist.")
        exit(1)

    if not project_root.is_dir():
        print(f"❌ Error: '{project_root}' is not a directory.")
        exit(1)

    create_dump(project_root)

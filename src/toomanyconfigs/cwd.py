from loguru import logger as log
from pathlib import Path
from typing import Union

class CWDNamespace:
    """A namespace object for nested file access"""
    def __init__(self, name=""):
        self._name = name
        self._files = {}

    def _add_file(self, path_parts, file_path):
        """Recursively add a file to the nested namespace structure"""
        if len(path_parts) == 1:
            # This is a file, set it directly
            attr_name = self._clean_name(path_parts[0])
            setattr(self, attr_name, file_path)
            self._files[attr_name] = file_path
        else:
            # This is a directory, create/get namespace and recurse
            dir_name = self._clean_name(path_parts[0])
            if not hasattr(self, dir_name):
                setattr(self, dir_name, CWDNamespace(dir_name))
            getattr(self, dir_name)._add_file(path_parts[1:], file_path)

    def _clean_name(self, name):
        """Clean a name to be a valid Python identifier"""
        # Remove file extension for cleaner access
        if '.' in name:
            name = name.rsplit('.', 1)[0]

        # Replace invalid chars with underscores
        name = name.replace('-', '_').replace(' ', '_')

        # Ensure it starts with a letter or underscore
        if name and not (name[0].isalpha() or name[0] == '_'):
            name = f"_{name}"

        return name

    def __repr__(self):
        return f"<CWDNamespace {self._name}>"

class CWD:
    def __init__(self, ensure: bool = True, *args: Union[str, dict, Path]):
        self.base_path = Path(__file__).parent
        self.file_structure = []

        for arg in args:
            self._process_arg(arg, self.base_path)

        # Create nested namespace structure
        self._create_nested_namespaces()

        if ensure: self.ensure_files()

    def _process_arg(self, arg: Union[str, dict, Path, list], base_path: Path):
        """Recursively process arguments to build file structure"""
        if isinstance(arg, str):
            file_path = base_path / arg
            self.file_structure.append(file_path)

        elif isinstance(arg, list):
            # Handle list of items
            for item in arg:
                self._process_arg(item, base_path)

        elif isinstance(arg, dict):
            # Handle dict - recursively process nested structure
            for key, value in arg.items():
                folder_path = base_path / key

                if isinstance(value, str):
                    # key is folder, value is file
                    file_path = folder_path / value
                    self.file_structure.append(file_path)

                elif isinstance(value, list):
                    # key is folder, value is list of items
                    for item in value:
                        self._process_arg(item, folder_path)

                elif isinstance(value, dict):
                    # key is folder, value is nested dict - recurse
                    self._process_arg(value, folder_path)

        elif isinstance(arg, Path):
            # If it's already a Path, add it relative to base_path if not absolute
            if arg.is_absolute():
                self.file_structure.append(arg)
            else:
                self.file_structure.append(base_path / arg)

    def _create_nested_namespaces(self):
        """Create nested namespace structure for file access"""
        for file_path in self.file_structure:
            # Get relative path from base_path
            rel_path = file_path.relative_to(self.base_path)
            path_parts = rel_path.parts

            if len(path_parts) == 1:
                # Root level file
                attr_name = self._clean_name(path_parts[0])
                setattr(self, attr_name, file_path)
                log.debug(f"Created root namespace: self.{attr_name} -> {file_path}")
            else:
                # Nested file - create/get the namespace structure
                current_ns = self
                for i, part in enumerate(path_parts[:-1]):
                    dir_name = self._clean_name(part)
                    if not hasattr(current_ns, dir_name):
                        setattr(current_ns, dir_name, CWDNamespace(dir_name))
                        log.debug(f"Created namespace: {dir_name}")
                    current_ns = getattr(current_ns, dir_name)

                # Set the final file
                file_name = self._clean_name(path_parts[-1])
                setattr(current_ns, file_name, file_path)
                namespace_path = '.'.join([self._clean_name(p) for p in path_parts[:-1]])
                log.debug(f"Created nested namespace: self.{namespace_path}.{file_name} -> {file_path}")

    def _clean_name(self, name):
        """Clean a name to be a valid Python identifier"""
        # Remove file extension for cleaner access
        if '.' in name:
            name = name.rsplit('.', 1)[0]

        # Replace invalid chars with underscores
        name = name.replace('-', '_').replace(' ', '_')

        # Ensure it starts with a letter or underscore
        if name and not (name[0].isalpha() or name[0] == '_'):
            name = f"_{name}"

        return name

    def ensure_files(self):
        """Create all files and directories in the file structure"""
        for file_path in self.file_structure:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.touch()

        log.debug(f"Created file structure:\n{self.tree_structure}")

    @property
    def tree_structure(self):
        """Return the file structure as a tree-formatted string"""
        if not self.file_structure:
            return "Empty file structure"

        # Group files by directory for better tree display
        dirs = {}
        for file_path in self.file_structure:
            rel_path = file_path.relative_to(self.base_path)
            parent = rel_path.parent
            if parent not in dirs:
                dirs[parent] = []
            dirs[parent].append(rel_path.name)

        lines = []
        sorted_dirs = sorted(dirs.keys())

        for i, dir_path in enumerate(sorted_dirs):
            is_last_dir = i == len(sorted_dirs) - 1

            if str(dir_path) == '.':
                # Root files
                for j, file_name in enumerate(sorted(dirs[dir_path])):
                    is_last_file = j == len(dirs[dir_path]) - 1 and is_last_dir
                    prefix = "└── " if is_last_file else "├── "
                    lines.append(f"{prefix}{file_name}")
            else:
                # Directory
                dir_prefix = "└── " if is_last_dir else "├── "
                lines.append(f"{dir_prefix}{dir_path}/")

                # Files in directory
                for j, file_name in enumerate(sorted(dirs[dir_path])):
                    is_last_file = j == len(dirs[dir_path]) - 1
                    if is_last_dir:
                        file_prefix = "    └── " if is_last_file else "    ├── "
                    else:
                        file_prefix = "│   └── " if is_last_file else "│   ├── "
                    lines.append(f"{file_prefix}{file_name}")

        return "\n".join(lines)

    def list_structure(self):
        """List all files in the structure"""
        for file_path in self.file_structure:
            log.debug(f"File: {file_path}")

    def __str__(self):
        return str(self.base_path)

    def __repr__(self):
        return f"CWD({self.base_path})"

if __name__ == "__main__":
    # Example usage with recursive nested structure
    c = CWD(
        "test.txt",                          # Simple file
        {"src": {                           # Nested folder structure
            "main.py": None,                # File in src/
            "utils": {                      # Nested folder src/utils/
                "helpers.py": None,
                "config": {                 # Deeply nested src/utils/config/
                    "settings.toml": None,
                    "database.toml": None
                }
            },
            "tests": ["test_main.py", "test_utils.py"]  # List of files in src/tests/
        }},
        {"docs": ["readme.md", "changelog.md"]},  # Multiple files in docs/
        Path("logs/app.log")                # Path object
    )

    log.debug(f"CWD: {c}")
    log.debug(f"File structure count: {len(c.file_structure)}")
    c.list_structure()

    # Optionally create the files
    # c.ensure_files()
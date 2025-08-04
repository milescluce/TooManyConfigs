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
        return f"[CWDNamespace.{self._name}]"

class CWD:
    def __init__(self, *args: Union[str, dict, Path], ensure: bool = True):
        self.cwd = Path.cwd()
        self.file_structure = []
        self.folder_structure = []
        self.file_content = {}

        for arg in args:
            self._process_arg(arg, self.cwd)

        # Create nested namespace structure
        self._create_nested_namespaces()

        if ensure: self.ensure_files()

    def _process_arg(self, arg: Union[str, dict, Path, list], base_path: Path):
        """Recursively process arguments to build file structure"""
        if isinstance(arg, str):
            if arg.endswith('/'):
                # It's a folder
                folder_path = base_path / arg.rstrip('/')
                self.folder_structure.append(folder_path)
                log.debug(f"{self.__repr__()}: Added folder: {folder_path}")
            else:
                # It's a file
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
                    # key is filename, value is default content
                    file_path = folder_path
                    self.file_structure.append(file_path)
                    self.file_content[file_path] = value
                    log.debug(f"{self.__repr__()}: Added file with content: {file_path}")

                elif value is None:
                    # key is filename, no default content
                    file_path = folder_path
                    self.file_structure.append(file_path)

                elif isinstance(value, list):
                    # key is folder, value is list of items
                    for item in value:
                        self._process_arg(item, folder_path)

                elif isinstance(value, dict):
                    # key is folder, value is nested dict - recurse
                    self._process_arg(value, folder_path)

        elif isinstance(arg, Path):
            # If it's already a Path, add it relative to cwd if not absolute
            if arg.is_absolute():
                self.file_structure.append(arg)
            else:
                self.file_structure.append(base_path / arg)

    def _create_nested_namespaces(self):
        """Create nested namespace structure for file access"""
        for file_path in self.file_structure:
            # Get relative path from cwd
            rel_path = file_path.relative_to(self.cwd)
            path_parts = rel_path.parts

            if len(path_parts) == 1:
                # Root level file
                attr_name = self._clean_name(path_parts[0])
                setattr(self, attr_name, file_path)
                log.debug(f"{self.__repr__()}: Created root namespace: self.{attr_name} -> {file_path}")
            else:
                # Nested file - create/get the namespace structure
                current_ns = self
                for i, part in enumerate(path_parts[:-1]):
                    dir_name = self._clean_name(part)
                    if not hasattr(current_ns, dir_name):
                        setattr(current_ns, dir_name, CWDNamespace(dir_name))
                        log.debug(f"{self.__repr__()}: Created namespace: {dir_name}")
                    current_ns = getattr(current_ns, dir_name)

                # Set the final file
                file_name = self._clean_name(path_parts[-1])
                setattr(current_ns, file_name, file_path)
                namespace_path = '.'.join([self._clean_name(p) for p in path_parts[:-1]])
                log.debug(f"{self.__repr__()}: Created nested namespace: self.{namespace_path}.{file_name} -> {file_path}")

        # Also create namespaces for standalone folders
        for folder_path in self.folder_structure:
            rel_path = folder_path.relative_to(self.cwd)
            path_parts = rel_path.parts

            if len(path_parts) == 1:
                # Root level folder
                attr_name = self._clean_name(path_parts[0])
                if not hasattr(self, attr_name):
                    setattr(self, attr_name, CWDNamespace(attr_name))
                    log.debug(f"{self.__repr__()}: Created root folder namespace: self.{attr_name}")
            else:
                # Nested folder
                current_ns = self
                for part in path_parts:
                    dir_name = self._clean_name(part)
                    if not hasattr(current_ns, dir_name):
                        setattr(current_ns, dir_name, CWDNamespace(dir_name))
                        log.debug(f"{self.__repr__()}: Created nested folder namespace: {dir_name}")
                    current_ns = getattr(current_ns, dir_name)

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
        # Create standalone folders first
        for folder_path in self.folder_structure:
            folder_path.mkdir(parents=True, exist_ok=True)
            log.debug(f"{self.__repr__()}: Created folder: {folder_path}")

        # Then create files
        for file_path in self.file_structure:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                if file_path in self.file_content:
                    # Write default content
                    file_path.write_text(self.file_content[file_path])
                    log.debug(f"{self.__repr__()}: Created file with content: {file_path}")
                else:
                    # Create empty file
                    file_path.touch()
                    log.debug(f"{self.__repr__()}: Created empty file: {file_path}")

        log.info(f"{self.__repr__()}: Ensured file structure:\n{self.tree_structure}")

    @property
    def tree_structure(self):
        """Return the file structure as a tree-formatted string"""
        if not self.file_structure and not self.folder_structure:
            return "Empty file structure"

        # Group files by directory for better tree display
        dirs = {}
        all_paths = self.file_structure + self.folder_structure

        for path in all_paths:
            rel_path = path.relative_to(self.cwd)
            parent = rel_path.parent
            if parent not in dirs:
                dirs[parent] = {'files': [], 'folders': []}

            if path in self.folder_structure:
                dirs[parent]['folders'].append(rel_path.name)
            else:
                dirs[parent]['files'].append(rel_path.name)

        lines = [self.__str__()]
        sorted_dirs = sorted(dirs.keys())

        for i, dir_path in enumerate(sorted_dirs):
            is_last_dir = i == len(sorted_dirs) - 1

            if str(dir_path) == '.':
                # Root items
                all_items = [(name, 'folder') for name in sorted(dirs[dir_path]['folders'])] + \
                           [(name, 'file') for name in sorted(dirs[dir_path]['files'])]

                for j, (item_name, item_type) in enumerate(all_items):
                    is_last_item = j == len(all_items) - 1 and is_last_dir
                    prefix = "└── " if is_last_item else "├── "
                    suffix = "/" if item_type == 'folder' else ""
                    lines.append(f"{prefix}{item_name}{suffix}")
            else:
                # Directory
                dir_prefix = "└── " if is_last_dir else "├── "
                lines.append(f"{dir_prefix}{dir_path}/")

                # Items in directory
                all_items = [(name, 'folder') for name in sorted(dirs[dir_path]['folders'])] + \
                           [(name, 'file') for name in sorted(dirs[dir_path]['files'])]

                for j, (item_name, item_type) in enumerate(all_items):
                    is_last_item = j == len(all_items) - 1
                    if is_last_dir:
                        item_prefix = "    └── " if is_last_item else "    ├── "
                    else:
                        item_prefix = "│   └── " if is_last_item else "│   ├── "
                    suffix = "/" if item_type == 'folder' else ""
                    lines.append(f"{item_prefix}{item_name}{suffix}")

        return "\n".join(lines)

    def list_structure(self):
        """List all files in the structure"""
        for folder_path in self.folder_structure:
            log.debug(f"{self.__repr__()}: Folder: {folder_path}")
        for file_path in self.file_structure:
            content_info = " (with content)" if file_path in self.file_content else ""
            log.debug(f"{self.__repr__()}: File: {file_path}{content_info}")

    def __str__(self):
        return str(self.cwd)

    def __repr__(self):
        return f"[{self.__class__.__name__}]"
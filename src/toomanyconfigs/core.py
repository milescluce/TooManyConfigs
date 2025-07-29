import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyperclip
import toml
from loguru import logger as log
from . import ACTIVE_CFGS, REPR

class TOMLSubConfig:
    @classmethod
    def create(cls, source: Path = None, name: str = None, **kwargs):
        SCREPR = f"[{cls.__name__}]"
        hit = None
        if source:
            if not name: name = cls.__name__.lower()
            log.debug(f"{REPR}: Building subconfig named {name}, from {source}")
            with source.open('r') as f:
                raw_data = toml.load(f)
                hit = raw_data.get(name)

        if hit: kwargs = {**hit, **kwargs}

        annotations = getattr(cls, '__annotations__', {})
        # Get field info and sort
        fields_with_defaults = []
        fields_without_defaults = []

        for name, annotation in annotations.items():
            if not name.startswith('_'):
                has_default = hasattr(cls, name) or name in kwargs
                if has_default:
                    fields_with_defaults.append((name, annotation))
                else:
                    fields_without_defaults.append((name, annotation))

        log.debug(f'{SCREPR}: Fields without defaults: {fields_without_defaults}')
        log.debug(f'{SCREPR}: Fields with defaults: {fields_with_defaults}')
        # Create new class with sorted fields
        sorted_annotations = {}
        for name, annotation in fields_without_defaults + fields_with_defaults:
            sorted_annotations[name] = annotation

        # Temporarily replace annotations
        original_annotations = cls.__annotations__
        cls.__annotations__ = sorted_annotations

        try:
            # Add missing kwargs as annotations dynamically
            current_annotations = getattr(cls, '__annotations__', {}).copy()

            for key, value in kwargs.items():
                if key not in current_annotations:
                    # Infer type from value, default to Any
                    inferred_type = type(value) if value is not None else Any
                    current_annotations[key] = inferred_type
                    # Set as class attribute with default value
                    setattr(cls, key, value if value is not None else None)

            # Update annotations
            cls.__annotations__ = current_annotations

            # Apply dataclass with updated fields
            dataclass_type = dataclass(cls)
            log.debug(f"{SCREPR}: Annotations: {dataclass_type.__annotations__}")
            inst = dataclass_type(**kwargs)
        finally:
            # Restore original annotations
            cls.__annotations__ = original_annotations

        missing_fields = [name for name in inst.__dataclass_fields__
                         if not name.startswith('_') and getattr(inst, name) is None]

        if missing_fields:
            log.info(f"{inst}: Missing fields detected: {missing_fields}")
            for field_name in missing_fields:
                inst._prompt_field(field_name)

        return inst

    def _prompt_field(self, field_name):
        time.sleep(1)
        prompt = f"{self}: Enter value for '{field_name}' (or press Enter to paste from clipboard): "
        user_input = input(prompt).strip() or pyperclip.paste()
        if not user_input.strip():
            log.debug(f"{self}: Using clipboard value for {field_name}")
        setattr(self, field_name, user_input)
        time.sleep(1)
        log.success(f"{self}: Set {field_name}")

    def as_dict(self):
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
            if not field.name.startswith('_')
        }

    def as_list(self):
        return [name for name in self.__dataclass_fields__ if not name.startswith('_')]

class TOMLConfig:
    @classmethod
    def create(cls, source: Path = None, **kwargs):
        # Set up paths first
        if source:
            path = Path(source)
            cwd = path.parent
        else:
            cwd = Path.cwd()
            name = cls.__name__.lower()
            path = Path.cwd() / (name + ".toml")

        if path.exists():
            log.debug(f"{REPR}: Building config from {path}")
            with path.open('r') as f:
                raw_data = toml.load(f)

            # Process subconfigs in the raw data
            file_data = {}
            for name, value in raw_data.items():
                if isinstance(value, dict):
                    # Get field type from annotations
                    field_type = getattr(cls, '__annotations__', {}).get(name)
                    if field_type and hasattr(field_type, 'create'):
                        # Pass the source path to subconfig creation
                        file_data[name] = field_type.create(source=path, name=name, **value)
                    else:
                        file_data[name] = value
                else:
                    file_data[name] = value

            # Merge file data with kwargs
            kwargs = {**file_data, **kwargs}
        else:
            log.warning(f"{REPR}: Config file not found at {path}, creating new one")
            path.touch(exist_ok=True)

        # NOW apply dataclass with all the data
        dataclass_cls = dataclass(cls)
        inst = dataclass_cls(**kwargs)

        # Set private attributes
        inst._cwd = cwd
        inst._path = path

        missing_fields = [name for name in inst.as_dict() if getattr(inst, name) is None]
        if missing_fields:
            log.info(f"{inst}: Missing fields detected: {missing_fields}")
            for field_name in missing_fields:
                inst._prompt_field(field_name)

        inst.write(verbose=False)

        return inst


    def as_dict(self):
        return {
            field.name: getattr(self, field.name)
            for field in self.__dataclass_fields__.values()
            if not field.name.startswith('_')
        }

    def as_list(self):
        return [name for name in self.__dataclass_fields__ if not name.startswith('_')]

    def _prompt_field(self, field_name):
        time.sleep(1)
        prompt = f"{self}: Enter value for '{field_name}' (or press Enter to paste from clipboard): "
        user_input = input(prompt).strip() or pyperclip.paste()
        if not user_input.strip():
            log.debug(f"{self}: Using clipboard value for {field_name}")
        setattr(self, field_name, user_input)
        time.sleep(1)
        log.success(f"{self}: Set {field_name}")

    def write(self, verbose: bool = True):
        if not self._path:
            raise ValueError("No path set for configuration file")

        config_data = {}
        for name in self.as_dict():
            value = getattr(self, name)
            if value is not None:
                # Check if value has as_dict method (nested config object)
                if hasattr(value, 'as_dict') and callable(getattr(value, 'as_dict')):
                    config_data[name] = value.as_dict()
                else:
                    config_data[name] = value

        if verbose: log.debug(f"{REPR}: Writing config to {self._path}")
        with self._path.open('w') as f:
            toml.dump(config_data, f)

    def read(self):
        if not self._path or not self._path.exists():
            return {}
        log.debug(f"{REPR}: Reading config from {self._path}")
        with self._path.open('r') as f:
            data = toml.load(f)

        # Process data to reconstruct subclass objects AND update self
        for name, value in data.items():
            if isinstance(value, dict) and hasattr(self, name):
                field_type = self.__dataclass_fields__[name].type
                processed_value = field_type.create(**value)
                setattr(self, name, processed_value)
                log.debug(f"{self}: Overrode '{name}' from file!")
            elif hasattr(self, name):
                setattr(self, name, value)
                log.debug(f"{self}: Overrode '{name}' from file!")

        return data  # Still return the raw data if needed
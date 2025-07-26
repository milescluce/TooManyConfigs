import time
from dataclasses import dataclass

import pyperclip
import toml
from loguru import logger as log
from pathlib import Path

REPR = "[TooManyConfigs]"

@dataclass
class TOMLConfig:
    """Base class for TOML-based configuration with interactive setup"""

    def __post_init__(self):
        self._cwd = None
        self._path = None

    @classmethod
    def from_toml(cls, path: Path = None, **kwargs):
        """Load configuration from TOML file, prompting for missing values"""
        inst = cls()
        for kwarg in kwargs:
            setattr(inst, kwarg, kwargs.get(kwarg))

        if path:
            inst._cwd = path.parent
            inst._path = path
            path = inst._path
        else:
            inst._cwd = Path.cwd()
            name = inst.__repr__().split("(")[0].lower()
            inst._path = Path.cwd() / (name + ".toml")
            path = inst._path

        if not inst._path.exists():
            log.warning(f"{REPR}: Config file not found at {path}, creating new one")
            path.touch(exist_ok=True)
            inst._prompt_all_fields()
            inst.write()
            return inst

        data = inst.read()
        inst._load_from_data(data)

        missing_fields = inst._get_missing_fields()
        if missing_fields:
            log.info(f"{inst}: Missing fields detected: {missing_fields}")
            inst._prompt_missing_fields(missing_fields)
            inst.write()

        return inst

    def _load_from_data(self, data):
        """Load data into instance fields"""
        for field_name in self._get_config_fields():
            if field_name in data:
                setattr(self, field_name, data[field_name])
                log.debug(f"{self}: Loaded {field_name} from config")

    def _get_config_fields(self):
        """Get all non-private fields from dataclass"""
        return [name for name in self.__dataclass_fields__ if not name.startswith('_')]

    def _get_missing_fields(self):
        """Get fields that are None or empty"""
        return [name for name in self._get_config_fields()
                if not getattr(self, name)]

    def _prompt_all_fields(self):
        """Prompt for all configuration fields"""
        for field_name in self._get_config_fields():
            if (getattr(self, field_name)) is not None: continue
            self._prompt_field(field_name)

    def _prompt_missing_fields(self, missing_fields):
        """Prompt for specific missing fields"""
        for field_name in missing_fields:
            self._prompt_field(field_name)

    def _prompt_field(self, field_name):
        """Prompt user for a single field value"""
        time.sleep(0.01)
        prompt = f"{self}: Enter value for '{field_name}' (or press Enter to paste from clipboard): "
        user_input = input(prompt).strip()

        if not user_input:
            user_input = pyperclip.paste()
            log.debug(f"{self}: Using clipboard value for {field_name}")

        setattr(self, field_name, user_input)
        log.success(f"{self}: Set {field_name}")

    def write(self):
        """Write configuration to TOML file"""
        if not self._path:
            raise ValueError("No path set for configuration file")

        config_data = {name: getattr(self, name)
                      for name in self._get_config_fields()}

        log.debug(f"{REPR}: Writing config to {self._path}")
        with self._path.open('w') as f:
            toml.dump(config_data, f)

    def read(self):
        """Read configuration from TOML file"""
        if not self._path or not self._path.exists():
            return {}

        log.debug(f"{REPR} Reading config from {self._path}")
        with self._path.open('r') as f:
            return toml.load(f)
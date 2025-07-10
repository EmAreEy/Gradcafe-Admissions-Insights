import os

import yaml
from box import Box


def config_loader(config_filename: str = "config.yaml") -> Box:
    project_path = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    config_path = os.path.join(project_path, "config.yaml")
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
            return Box(config)
    except Exception as e:
        raise Exception(
            f"Failed to load config from {config_path}\n"
            f"Hint: make sure config.yaml exists and is valid YAML.\n"
            f"Error: {e}"
        ) from e

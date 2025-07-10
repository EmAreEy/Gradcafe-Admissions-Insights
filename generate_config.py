import os

import yaml


def make_config():
    print("start config file generation...")
    project_directory = os.getcwd()
    print(f"project root identified as : \n {project_directory}")
    RAW_DATA_DIR = os.path.join(project_directory, "data", "raw")
    PROCESSED_DATA_DIR = os.path.join(project_directory, "data", "processed")
    REFERENCE_DATA_DIR = os.path.join(project_directory, "data", "reference")
    LOGS_DIR = os.path.join(project_directory, "logs")

    directories = [RAW_DATA_DIR, PROCESSED_DATA_DIR, REFERENCE_DATA_DIR, LOGS_DIR]

    print("check for directories (make of not exist)...")
    for dir in directories:
        os.makedirs(dir, exist_ok=True)
    config_data = {
        "data directories": {
            "raw_data_dir": RAW_DATA_DIR,
            "processed_data_dir": PROCESSED_DATA_DIR,
            "reference_data_dir": REFERENCE_DATA_DIR,
        },
        "universities_api": {
            "openalex_autocompelete_api": "https://api.openalex.org/autocomplete/institutions?q=",
            "openalex_search_api": "https://api.openalex.org/institutions?search=",
            "openalex_specific_search_api": "https://api.openalex.org/institutions?filter=display_name.search:",
        },
        "log directory": LOGS_DIR,
    }

    config_data_path = os.path.join(project_directory, "config.yaml")
    try:
        with open(config_data_path, "w", encoding="utf-8") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
            print("config.yaml generated successfully.")
    except Exception as e:
        raise RuntimeError(f"error while making config.yaml : \n {e}") from e


if __name__ == "__main__":
    make_config()

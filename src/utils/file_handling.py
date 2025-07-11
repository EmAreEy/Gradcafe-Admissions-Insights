import json
from collections.abc import Generator

from tqdm import tqdm

from utils.logger import get_logger

logging = get_logger("File_handler")


def save_jsonl(file_path: str, data: dict, mode: str = "w") -> None:
    logging.info(f"saving data to {file_path} ")
    try:
        with open(file_path, mode) as f:
            for key, value in tqdm(data.items(), desc="writing file...", delay=5):
                json.dump({key: value}, f, ensure_ascii=False)
                f.write("\n")
    except (TypeError, OSError) as e:
        logging.error(f"Failed to write file!\n{e}")


def stream_jsonl(file_path: str) -> Generator | None:
    logging.info(f"stream {file_path}")
    try:
        with open(file_path) as f:
            try:
                for line in f:
                    yield json.loads(line)
            except (json.JSONDecodeError, StopIteration) as e:
                logging.warning(f"WARNING : Skipping invalid line! {e}")
            except Exception as e:
                logging.error(f"failed to read {file_path} : {e}")
    except FileNotFoundError:
        try:
            with open(file_path, "w") as f:
                logging.info(f"{file_path} created!")
                return None
        except OSError as e:
            logging.error(f"Error while making this file :{file_path} {e}")
    except OSError as e:
        logging.error(f"failed to read  {file_path} Error : {e}")


def load_profiles(file_path: str) -> dict:
    profiles = {}
    data = stream_jsonl(file_path)
    if data:
        for dict_line in data:
            key = list(dict_line.keys())[0]
            profiles[key] = dict_line.get(key)
    else:
        logging.error(f"{file_path} is empty!")
    return profiles

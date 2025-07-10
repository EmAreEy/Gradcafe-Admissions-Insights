import json
import os
import re
import time
from collections import Counter
from collections.abc import Generator

import requests
from rapidfuzz import fuzz, process
from tqdm import tqdm

from utils.load_config import config_loader
from utils.logger import get_logger

config = config_loader()
RAW_DATA_DIR = config.data_directories.raw_data_dir
REFERENCE_DATA_DIR = config.data_directories.reference_data_dir
AUTO_SEARCH = config.universities_api.openalex_autocompelete_api
SEARCH = config.universities_api.openalex_search_api
SPECIFIC_SEARCH = config.universities_api.openalex_specific_search_api


def collect_universities_raw_names(
    path_to_raw_file: str, path_to_freq_file: str
) -> None:
    raw_names_counter = Counter()
    logging.info(f"opening {path_to_raw_file} to extract universities")
    raw_names_itr = _stream_jsonl(path_to_raw_file)
    if raw_names_itr:
        for data in raw_names_itr:
            if data["university"]:
                raw_names_counter.update(data["university"])
    else:
        logging.error(
            f"raw file is empty ! or there is a problem to load it : {path_to_raw_file}"
        )

    logging.info(f"{len(raw_names_counter)} raw names collected ")
    freq_data = dict(raw_names_counter.most_common())
    _save_jsonl(path_to_freq_file, freq_data)


def _save_jsonl(file_path: str, data: dict, mode: str = "w") -> None:
    logging.info(f"saving data to {file_path} ")
    try:
        with open(file_path, mode) as f:
            for key, value in tqdm(data.items(), desc="writing file...", delay=5):
                json.dump({key: value}, f, ensure_ascii=False)
                f.write("\n")
    except (TypeError, OSError) as e:
        logging.error(f"Failed to write file!\n{e}")


def _stream_jsonl(file_path: str) -> Generator | None:
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


def _call_api(url: str, max_retries: int = 4, timeout: int = 10) -> dict | None:
    logging.info(f"calling API : {url}")
    for attempt in range(max_retries + 1):
        try:
            time.sleep(0.1)
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return dict(response.json())
        except requests.exceptions.HTTPError as e:
            logging.warning(f"HTTP error on attempt {attempt + 1}:{e} for {url}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Network error on attempt {attempt + 1}:{e} for {url}")

        if attempt == max_retries:
            break
        delay = 2**attempt
        logging.warning(f"retrying in {delay} seconds")
        time.sleep(delay)
    logging.error(f"api call failed in {max_retries} attempts for {url}")
    return None


def _get_university_info(university_name: str) -> dict | None:
    for endpoint in (SEARCH, SPECIFIC_SEARCH):
        response = _call_api(endpoint + university_name)
        if response:
            results = response.get("results")
            if isinstance(results, list) and results:
                return results[0]
    return None


def _load_profiles(file_path: str) -> dict:
    profiles = {}
    data = _stream_jsonl(file_path)
    if data:
        for dict_line in data:
            key = list(dict_line.keys())[0]
            profiles[key] = dict_line.get(key)
    else:
        logging.error(f"{file_path} is empty!")
    return profiles


def _search_university(name: str, data, score_cutoff: int, scorer_method) -> str:
    result = process.extract(
        name, data, score_cutoff=score_cutoff, scorer=scorer_method, limit=1
    )
    return result[0] if result else ""


def _make_profile(data: dict) -> dict:
    keys = [
        "id",
        "display_name",
        "works_count",
        "cited_by_count",
        "summary_stats",
        "geo",
    ]
    info = {}
    info["data"] = {k: data.get(k) for k in keys}
    return info


def _find_acronym(name: str) -> str:
    pattern = (
        r"\b(?:[A-Z0-9]{3,}|[A-Z0-9]+(?:[&\.\/-][A-Z0-9]+)+)\b|\(\b[A-Za-z0-9-.]+\b\)"
    )
    match = re.search(pattern, name)
    return match.group(0) if match else ""


def _should_skip(name: str) -> bool:
    name = name.lower()
    SKIP_STARTS_WITH = ("#", "*")
    SKIP_CONTAINS = (
        "ignore",
        "everywhere",
        "every",
        "other",
        "test",
        "prison",
        "reject",
        "file",
        "torture",
        "anyone ",
        "interview",
        "?",
        'hogwarts'
    )
    SKIP_EXACT = (
        "any",
        "college",
        "university",
        "the",
        "no",
        "at",
        "in",
        "a university",
        "university of",
        "general",
        "generic",
    )
    starts_with_bool = name.startswith(SKIP_STARTS_WITH)
    exact_bool = name in SKIP_EXACT
    contains_bool = any(sub in name for sub in SKIP_CONTAINS)
    return starts_with_bool or exact_bool or contains_bool


def collect_universities_info(
    raw_names_path: str,
    universities_profiles_path: str,
    universities_map_path: str,
    failed_path: str,
) -> None:
    raw_names: list[str] = list(_load_profiles(raw_names_path).keys())
    universities_profiles: dict[str, dict] = _load_profiles(universities_profiles_path)
    universities_profiles_keys = universities_profiles.keys()
    universities_map: dict[str, str] = _load_profiles(universities_map_path)
    universities_map_keys = universities_map.keys()
    failed: dict[str, int] = {}

    for i in tqdm(range(len(raw_names)), desc="updating universities info: "):
        '''if (i + 1) % 50 == 0:
            _save_jsonl(universities_map_path, universities_map)
            _save_jsonl(universities_profiles_path, universities_profiles)
            _save_jsonl(failed_path, failed)'''

        name = raw_names[i]
        if _should_skip(name):
            logging.info(f"SKIPPED {name}")
            universities_map[name] = 'skipped'
            continue

        acronym = _find_acronym(name)
        search_result = _search_university(name, universities_map_keys, 90, fuzz.ratio)

        if search_result:
            universities_map[name] = universities_map[search_result[0]]
            logging.info(f"{name} -> {search_result} with MAP")

        elif profile_search := _search_university(
            name, universities_profiles_keys, 95, fuzz.partial_ratio
        ):
            keys_list=list(universities_profiles_keys)
            universities_map[name] = keys_list[keys_list.index(profile_search[0])]
            logging.info(f"{name} -> {profile_search} with PROFILES")

        elif acronym:
            acronym_search_result = _search_university(
                name, universities_map_keys, 95, fuzz.token_set_ratio
            )
            if acronym_search_result:
                universities_map[name] = universities_map[acronym_search_result[0]]
                logging.info(f"{name} -> {acronym_search_result} with ACRONYM")

        else:
            data = _get_university_info(name)
            if not data and acronym:
                data = _get_university_info(acronym)
            if data:
                university_name = (data["display_name"] + " " + acronym).strip()
                info = _make_profile(data)
                universities_profiles.setdefault(university_name, {}).update(info)
                universities_map[name] = university_name
            else:
                failed.setdefault(name, 0)
                failed[name] += 1
                logging.warning(f"failed to find {name} for {failed[name]} times")


if __name__ == "__main__":
    logging = get_logger("universities")
    raw_file_name = "initial_run.jsonl"
    raw_file_universities_name = "universities_raw_name.jsonl"
    path_to_raw_file_universities_name = os.path.join(
        REFERENCE_DATA_DIR, raw_file_universities_name
    )
    path_to_raw_file = os.path.join(RAW_DATA_DIR, raw_file_name)

    map_path = os.path.join(REFERENCE_DATA_DIR, "universities_map.jsonl")
    profile_path = os.path.join(REFERENCE_DATA_DIR, "universities_lookup.jsonl")
    failed_path = os.path.join(REFERENCE_DATA_DIR, "failed.jsonl")

    collect_universities_info(
        path_to_raw_file_universities_name, profile_path, map_path, failed_path
    )

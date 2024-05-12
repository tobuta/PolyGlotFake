import os
import json


def get_all_file_paths(directory):
    """Return a list of absolute paths of all .mp4 files in the given directory and its subdirectories."""
    file_paths = []

    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".mp4"):
                file_paths.append(os.path.abspath(os.path.join(dirpath, filename)))

    return file_paths


"""
find mp4 file path according to json file 
"""


def yield_file_paths_from_json(
    json_filepath, directory, status_filename="./utils/status.json"
):
    """Yield file paths that match filenames specified in the JSON file."""

    last_processed_file = ""
    with open(status_filename, "a+") as f:
        f.seek(0)
        last_processed_file = f.read()

    file_paths = get_all_file_paths(directory)
    with open(json_filepath, "r") as json_file:
        try:
            data = json.load(json_file)
            filenames = data.get("videos")

            start_processing = False if last_processed_file else True
            for file_dict in filenames:
                filename = file_dict.get("filename")

                if not start_processing:
                    if filename == last_processed_file:
                        start_processing = True
                    continue

                for path in file_paths:
                    if os.path.basename(path) == filename:
                        yield path, filename, filename.split("_")[0]

                        with open(status_filename, "w") as sf:
                            sf.write(filename)
        except json.JSONDecodeError:
            print(f"Error decoding JSON in {json_filepath}")

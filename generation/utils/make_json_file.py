import json
import os


def initialize_json_file(language:str, file_dir:str):

    filename = 'to_' + language + '.json'
    file_path = os.path.join(file_dir,filename)

    if not os.path.exists(file_path):
        data = {"language":language,"video": []}
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    return file_path


def append_video_info(video_info:dict, file_path:str):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    data["video"].append(video_info)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    json_path = initialize_json_file("en","./")

    # append video info when finished a video processing
    video_info_tamplate = {
        "name": "",
        "raw_video_name": "",
        "tts_techniqu": "",
        "duration": "",
    }
    append_video_info(video_info_tamplate,json_path)

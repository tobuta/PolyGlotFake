from utils.read_file import yield_file_paths_from_json
from utils.load_model import PreloadModel
from preprocessing.speech_to_text import STT
from preprocessing.micro_trans import translate
from time import sleep
from utils.separation_merging import merge_audio_video, get_duration

from tqdm import tqdm
from utils.make_json_file import initialize_json_file, append_video_info
import os


supported_lang = {
    "Xtts": ["en", "ru", "fr", "es", "zh", "ar"],
    "Bark": ["es", "en", "ja", "ru", "zh", "fr"],
    "Tacotron": ["es", "fr", "en", "zh", "ja"],
    "Vall": ["en", "zh", "ja"],
    "MicroTts": ["en", "ru", "fr", "es", "zh", "ar", "ja"],
}


stt = STT(device="cuda:1")

model_manager = PreloadModel(device = "cuda:1")
preload_model_dict = model_manager.load

video_info_tamplate = {
    "name": "",
    "raw_video_name": "",
    "tts_techniqu": "",
    "duration": "",
}


def get_to_lang(input_lang: str):
    lang_list = ["en", "ru", "fr", "es", "zh", "ar", "ja"]
    lang_list.remove(input_lang)
    return lang_list


def get_trans_dict(input_lang, video_path):
    get_text, _, _, _ = stt.transcribe(video_path)
    lang_list = get_to_lang(input_lang)
    trans_text_w_lang = translate(get_text, lang_list)
    trans_dict = {}
    for text_w_lang in trans_text_w_lang[0]["translations"]:  
        if text_w_lang["to"] == "zh-Hans":
            lang = "zh"
        else:
            lang = text_w_lang["to"]
        text = text_w_lang["text"]
        trans_dict[lang] = text
    return trans_dict


def tts_and_merge(
    file_name,
    input_lang,
    trans_dict,
    model_name,
    video_path,
    output_dir="./data",
):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for key in trans_dict.keys():
        if (key in supported_lang[model_name]) and (
            input_lang in supported_lang[model_name]
        ):
            text = trans_dict[key]

            output_path = os.path.join(output_dir, "to_" + key)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                print(f"Folder '{output_path}' created.")

            output_filename = file_name.split(".")[0] + "_to_" + key + "_" + model_name + ".mp4"
            output_file_path = os.path.join(output_path, output_filename)

            json_file_path = initialize_json_file(key, output_path)

            if not os.path.exists(output_file_path):
                tts_audio = preload_model_dict[model_name].tts(
                    text=text, language=key, prompt=video_path
                )
                audio_duration = get_duration(tts_audio.name)
                formatted_audio_duration = f"{audio_duration:.2f}"

                video_info_tamplate["name"] = output_filename
                video_info_tamplate["raw_video_name"] = file_name
                video_info_tamplate["tts_techniqu"] = model_name
                video_info_tamplate["duration"] = formatted_audio_duration

                merge_audio_video(
                    video_path=file_path,
                    audio_path=tts_audio.name,
                    output_path=output_file_path,
                )
                append_video_info(
                    video_info=video_info_tamplate, file_path=json_file_path
                )
            else:
                print(f"file '{output_filename}' exists, to proccess next one...")



if __name__ == "__main__":
    model_names = [key for key in preload_model_dict.keys()]

    for file_path, file_name, lang in yield_file_paths_from_json(
            "/houyang/ns235x/program/DataSet/raw_video/all_video.json",
            "/houyang/ns235x/program/DataSet/raw_video",
        ):
        print(f"*****************trans:{file_name}************************")
        #trans_dict = get_trans_dict(input_lang=lang, video_path=file_path)
        trans_dict = get_trans_dict(input_lang=lang, 
                                    video_path=file_path)
        for model_name in model_names:
            tts_and_merge(
                file_name=file_name,
                input_lang=lang,
                trans_dict=trans_dict,
                model_name=model_name,
                video_path=file_path,
            )

    print("All files done!")
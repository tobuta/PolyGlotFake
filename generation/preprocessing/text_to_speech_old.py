
import tempfile
from TTS.api import TTS
import os
from utils.separation_merging import extract_audio, get_duration

from TTS.vall_e_x.utils_e_x.prompt_making import make_prompt_save
from TTS.vall_e_x.utils_e_x.generation import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
from .speech_to_text import STT
import atexit

import json
import azure.cognitiveservices.speech as speechsdk
import tempfile

from TTS.tts.layers.bark.hubert.kmeans_hubert import CustomHubert
from TTS.tts.layers.bark.hubert.tokenizer import HubertTokenizer
from encodec.utils import convert_audio
from tqdm import tqdm
from utils.load_codec_model import _load_codec_model

import torchaudio
import torch

import numpy as np




with open(
    "./preprocessing/config.json", "r"
) as file:
    config = json.load(file)


class Xtts:
    def __init__(self, language: str, device: str) -> None:
        super().__init__()

        if language == "zh":
            self.language = "zh-cn"
        else:
            self.language = language
        self.tts_x = TTS("tts_models/multilingual/multi-dataset/xtts_v1").to(device)
        #self.transcritor = STT()
        self.shot_prompt = None
        self.prompt_before = None
        atexit.register(self.cleanup)

    def tts(self, text: str, 
            prompt: str, 
            delete_file: bool = True):
        
        if self.prompt_before != prompt:
                #text_all, langu, text_1, first_end_time = self.transcritor.transcribe(prompt)

            if self.shot_prompt != None:
                os.remove(self.shot_prompt)

            audio_duration = get_duration(prompt)

            if audio_duration > 11:
                self.shot_prompt = extract_audio(
                    prompt, output_mode="temp", slice_time=11
                )
            else:
                self.shot_prompt = extract_audio(
                    prompt, output_mode="temp"
                )
            
            self.prompt_before = prompt
        
        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(delete=delete_file, suffix=".wav")
        self.tts_x.tts_to_file(
            text=text,
            file_path=temp_file.name,
            speaker_wav=self.shot_prompt,
            language=self.language,
        )
        return temp_file
    
    def cleanup(self):
        if self.shot_prompt != None:
            if os.path.exists(self.shot_prompt):
                os.remove(self.shot_prompt)


class Tacotron:
    def __init__(self, language: str, device: str) -> None:
        """Load model according the language

        Args:
            language (str): Support language: "en", "ja", "es", "zh", "fr"
            device (str): Specify the deployment device
        """ 
        if language == "en":
            self.tts_tac = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        if language == "ja":
            self.tts_tac = TTS("tts_models/ja/kokoro/tacotron2-DDC").to(device)
        if language == "es":
            self.tts_tac = TTS("tts_models/es/mai/tacotron2-DDC").to(device)
        if language == "zh":
            self.tts_tac = TTS("tts_models/zh-CN/baker/tacotron2-DDC-GST").to(device)
        if language == "fr":
            self.tts_tac = TTS("tts_models/fr/mai/tacotron2-DDC").to(device)
        #self.transcritor = STT()
        self.shot_prompt = None
        self.prompt_before = None
        atexit.register(self.cleanup)
        

    def tts(self, text: str, 
            prompt: str, 
            delete_file: bool = True):
        
        if self.prompt_before != prompt:
                

            if self.shot_prompt != None:
                os.remove(self.shot_prompt)

            audio_duration = get_duration(prompt)
            
            if audio_duration > 10:
                self.shot_prompt = extract_audio(
                    prompt, output_mode="temp", slice_time=10
                )
            else:
                self.shot_prompt = extract_audio(
                    prompt, output_mode="temp"
                )

        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(delete=delete_file, suffix=".wav")
        self.tts_tac.tts_with_vc_to_file(
                                            text=text, 
                                            file_path=temp_file.name, 
                                            speaker_wav=self.shot_prompt
                                        )
        return temp_file

    def cleanup(self):
        if self.shot_prompt != None:
            if os.path.exists(self.shot_prompt):
                os.remove(self.shot_prompt)

"""
Note: According our experiment, bark with hubert model do not have multilingual voice coversion ability (e.g. it can not transfer english voice using spanish prompt), 
Instead of using hubert  we use bark generate voice and use FreeVC for voice conversion (easy and quick way) 
The public accessable bark hurbet models only support english japanese and spanish, you can use the script blow to create prompts in corresponding languages to try voice clone.
"""
class MakeBarkPrompt():
    def __init__(self, language, device: str) -> None:
        hubert = "./tts_model/" \
                 "tts_models--multilingual--multi-dataset--bark/hubert.pt"
        if language == "en":
            tokenizer = "./tts_model/" \
                         "tts_models--multilingual--multi-dataset--bark/tokenizer_en.pth"

        if language == "es":
            tokenizer = "./tts_model/" \
                         "tts_models--multilingual--multi-dataset--bark/tokenizer_es.pth"

        if language == "ja":
            tokenizer = "./tts_model/" \
                         "tts_models--multilingual--multi-dataset--bark/tokenizer_ja.pth"
        
        if not  os.path.isfile(tokenizer):
            raise FileNotFoundError("tokenizer file do not exist.")
        else:
            print("tokenizer file exist.")

        self.hubert_model = CustomHubert(checkpoint_path=hubert).to(device )
        self.tokenizer = HubertTokenizer.load_from_checkpoint(tokenizer).to(device)   
        self.en_model = _load_codec_model(device)    
        self.device = device

    @staticmethod
    def make_prompt_from_wav(audio_filepath, output_path, en_model, hubert_model,tokenizer,device):
        wav, sr = torchaudio.load(audio_filepath)
        wav = convert_audio(wav, sr, en_model.sample_rate, en_model.channels)
        wav = wav.to(device)
        semantic_vectors = hubert_model.forward(wav, input_sample_hz=en_model.sample_rate)
        semantic_tokens = tokenizer.get_token(semantic_vectors)
        # Extract discrete codes from EnCodec
        with torch.no_grad():
            encoded_frames = en_model.encode(wav.unsqueeze(0))
        codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()
        # move codes to cpu
        codes = codes.cpu().numpy()
        # move semantic tokens to cpu
        semantic_tokens = semantic_tokens.cpu().numpy()
        np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)

    def generate_prompt(self, video_dir_path: str, # .mp4 file dir path
                    prompt_file_path: str = "./prompt/bark_short_prompts"):

        print("making prompt...")
        mp4_files = [file for root, _, files in os.walk(video_dir_path) for file in files if file.endswith(".mp4")]
        for mp4_file in tqdm(mp4_files, desc="extract audio"):
            mp4_path = os.path.join(video_dir_path, mp4_file)
            
            folder_name = os.path.splitext(mp4_file)[0]
            folder_path = os.path.join(prompt_file_path, folder_name)

            if not os.path.isdir(folder_path):
                os.makedirs(folder_path)
                
                audio_path = os.path.join(folder_path, f"{folder_name}.wav")
                prompt_path =  os.path.join(folder_path, f"{folder_name}.npz")

                audio_duration = get_duration(mp4_path)
                if audio_duration > 11:
                    extract_audio(mp4_path, output_mode="wav", slice_time = 11, output_path=audio_path)
                else:
                    extract_audio(mp4_path, output_mode="wav",  output_path=audio_path)
                

                MakeBarkPrompt.make_prompt_from_wav(  audio_path,
                                            prompt_path,
                                            self.en_model,
                                            self.hubert_model,
                                            self.tokenizer,
                                            self.device
                                            )
                os.remove(audio_path)
        print("making prompt done!")



class Bark:
    def __init__(self, language, device: str) -> None:
        super().__init__()
        print("language:",language)
        self.tts_bark = TTS("tts_models/multilingual/multi-dataset/bark").to(device)
        self.shot_prompt = None
        self.prompt_before = None
        atexit.register(self.cleanup)
                
    def tts(
        self, text: str, 
        prompt: str, 
        #prompt_directory: str = './prompt/bark_short_prompts',  # find corresbonding voive prompt according to you .mp4 file name 
        delete_file: bool = True
    ) -> tempfile.NamedTemporaryFile:
        # filename_without_ext, ext = os.path.splitext(os.path.basename(prompt))
        # if ext == ".mp4":
        #     video_filename_without_ext = filename_without_ext
            
        #     prompt_list = [os.path.basename(filename) for filename in os.listdir(prompt_directory)]
        
        #     if video_filename_without_ext in prompt_list:
        #         prompt_file_name = video_filename_without_ext
        #     else:
        #         raise ValueError(
        #             f"No matching file found for '{video_filename_without_ext}' in the directory."
        #         )
        #     print("In progress:",prompt_file_name)

        #     tempfile.tempdir = "./prompt/temp_file"
        #     temp_file = tempfile.NamedTemporaryFile(delete=delete_file, suffix=".wav")
        #     self.tts_bark.tts_to_file(
        #         text=text,
        #         file_path=temp_file.name,
        #         voice_dir=prompt_directory,
        #         speaker=prompt_file_name
                
        #     )
        #     return temp_file
        if self.prompt_before != prompt:
                

            if self.shot_prompt != None:
                os.remove(self.shot_prompt)

            audio_duration = get_duration(prompt)
            
            if audio_duration > 10:
                self.shot_prompt = extract_audio(
                    prompt, output_mode="temp", slice_time=10
                )
            else:
                self.shot_prompt = extract_audio(
                    prompt, output_mode="temp"
                )

        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(delete=delete_file, suffix=".wav")
        self.tts_bark.tts_with_vc_to_file(
                                            text=text, 
                                            file_path=temp_file.name, 
                                            speaker_wav=self.shot_prompt
                                        )
        return temp_file

    def cleanup(self):
        if self.shot_prompt != None:
            if os.path.exists(self.shot_prompt):
                os.remove(self.shot_prompt)



class Vall:
    def __init__(
        self,
        language: str,
        device: str,
    ) -> None:
        self.transcritor = STT('large')
        preload_models(device)
        print("language:",language)
    

    def generate_prompt(
        self,
        video_dir_path: str, # .mp4 video dir path
        save_dir="./prompt/vall_short_prompts",
        use_stt: bool = True
    ):  

        mp4_files = [file for root, _, files in os.walk(video_dir_path) for file in files if file.endswith(".mp4")]
        for mp4_file in tqdm(mp4_files, desc="extract audio"):
            
            name_without_ext = os.path.splitext(mp4_file)[0]
            check_npz_file_name = name_without_ext + ".npz"
            check_npz_file_path = os.path.join(save_dir,check_npz_file_name)

            if not os.path.exists(check_npz_file_path): # if .npz do not exist
                video_file_path = os.path.join(video_dir_path,mp4_file)
                print("-----In progress-----:",mp4_file)
                audio_duration = get_duration(video_file_path)

                if audio_duration > 10:
                    shot_prompt = extract_audio(
                        video_file_path, output_mode="temp", slice_time=10
                    )
                else:
                    shot_prompt = extract_audio(
                        video_file_path, output_mode="temp"
                    )
                if use_stt:
                    text, lang, _, _ = self.transcritor.transcribe(shot_prompt)
                    print("text:",text)
                    print("language:",lang)

                else: 
                    text = None
                
                make_prompt_save(
                    name_without_ext,
                    audio_prompt_path=shot_prompt,
                    save_dir=save_dir,
                    transcript=text
                )
                os.remove(shot_prompt)

    def tts(
        self,
        text: str,
        prompt: str,  # find corresbonding voive prompt according to you .mp4 file name 
        prompt_directory: str = "./prompt/vall_short_prompts",
        delete_file: bool = True,
    ):
       
        filename_without_ext, ext = os.path.splitext(os.path.basename(prompt))
        if ext == ".mp4":
            video_filename_without_ext = filename_without_ext

            prompt_list = [os.path.splitext(os.path.basename(filename))[0] for filename in os.listdir(prompt_directory)]
        
            if video_filename_without_ext in prompt_list:
                prompt_file_path = os.path.join(prompt_directory, video_filename_without_ext) + ".npz"
            else:
                raise ValueError(
                    f"No matching file found for '{video_filename_without_ext}' in the directory."
                )
            print("In progress:",video_filename_without_ext)

            
            audio_array = generate_audio(text, prompt_file_path)
            
            # tempfile.tempdir = "./prompt/temp_file"
            temp_file = tempfile.NamedTemporaryFile(delete=delete_file, suffix=".wav")
            write_wav(temp_file.name, SAMPLE_RATE, audio_array)

            return temp_file


class MicroTts:
    """
    Chinese: zh-CN (Chinese Mandarin, Simplified)
    Arabic: ar-SA (Arabic, Saudi Arabia)
    Spanish: es-ES (Spanish, Spain)
    English: en-US (English, United States)
    Japanese: ja-JP (Japanese, Japan)
    Russian: ru-RU (Russian, Russia)
    """

    def __init__(self, language: str,  device: str ,gender: str = "Male" ):
        ann_dict = {
            "zh": {"Female": "zh-CN-XiaoxiaoNeural", "Male": "zh-CN-YunjianNeural"},
            "ar": {"Female": "ar-SA-ZariyahNeural", "Male": "ar-SA-HamedNeural"},
            "es": {"Female": "es-ES-ElviraNeural", "Male": "es-ES-AlvaroNeural"},
            "en": {"Female": "es-US-PalomaNeural", "Male": "es-US-AlonsoNeural"},
            "ja": {"Female": "ja-JP-NanamiNeural", "Male": "ja-JP-KeitaNeural"},
            "ru": {"Female": "ru-RU-SvetlanaNeural", "Male": "ru-RU-DmitryNeural"},
            "fr": {"Female": "fr-FR-DeniseNeural", "Male": "fr-FR-HenriNeural"}
        }

        announcer = ann_dict[language][gender]
        key = config["AzureTts"]["subscription_key"]
        location = config["AzureTts"]["region"]
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=location)
        self.speech_config.speech_synthesis_voice_name = announcer
        self.voice_conver = TTS(
            model_name="voice_conversion_models/multilingual/vctk/freevc24",
            progress_bar=False,
        ).to(device)
        
        self.prompt_before = None
        self.shot_prompt = None
        atexit.register(self.cleanup)

    def tts(
        self,
        text: str,
        prompt: str, # Using .mp4 file to make shot prompt.
        conver: bool = True,  # True for using FreeVC
        delete_file: bool = True,
    ):
        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(delete=delete_file, suffix=".wav")
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)


        speechSynthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config, audio_config=audio_config
        )
        
        try:
            result = speechSynthesizer.speak_text_async(text).get()
        except Exception as e:
            print(f"Error occurred in MicroAPI: {e}")
            return None
        if conver:
            if self.prompt_before != prompt:

                if self.shot_prompt != None:
                    os.remove(self.shot_prompt)

                audio_duration = get_duration(prompt)
                
                if audio_duration > 10:
                    self.shot_prompt = extract_audio(
                        prompt, output_mode="temp", slice_time=10
                    )
                else:
                    self.shot_prompt = extract_audio(
                        prompt, output_mode="temp"
                    )
                self.prompt_before = prompt
                    

                self.voice_conver.voice_conversion_to_file(
                    source_wav=temp_file.name,
                    target_wav=self.shot_prompt,
                    file_path=temp_file.name,
                )
        return temp_file
    
    def cleanup(self):
        if self.shot_prompt != None:
            if os.path.exists(self.shot_prompt):
                os.remove(self.shot_prompt)


if __name__ == "__main__":
    micro_tts = MicroTts()
    result = micro_tts.tts("This is a test, can you hear me?")
    print(result.name)
    result.close()

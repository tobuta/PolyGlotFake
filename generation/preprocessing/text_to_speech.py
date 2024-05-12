
import tempfile
from TTS.api import TTS
import os
from utils.separation_merging import extract_audio, get_duration
from TTS.vall_e_x.utils_e_x.generation import SAMPLE_RATE, generate_audio, preload_models
from scipy.io.wavfile import write as write_wav
import atexit
import json
import azure.cognitiveservices.speech as speechsdk
import tempfile

with open(
    "./preprocessing/config.json", "r"
) as file:
    config = json.load(file)


class Xtts:
    def __init__(self,device: str) -> None:
        
        self.tts_x = TTS("tts_models/multilingual/multi-dataset/xtts_v1").to(device)
        self.shot_prompt = None
        self.prompt_before = None
        atexit.register(self.cleanup)

    def tts(self, text: str, 
            language:str,
            prompt: str, 
            delete_file: bool = True):
        
        if language not in ["en", "ru", "fr", "es", "zh", "ar"]:
            raise ValueError(f"{self.__class__.__name__} does not support'{language}'!")
        
        if language == "zh":
            language = "zh-cn"
        else:
            language = language        
        if self.prompt_before != prompt:
                #text_all, langu, text_1, first_end_time = self.transcritor.transcribe(prompt)

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
        
        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(prefix='Xtts_',delete=delete_file, suffix=".wav")
        self.tts_x.tts_to_file(
            text=text,
            file_path=temp_file.name,
            speaker_wav=self.shot_prompt,
            language=language,
        )
        return temp_file
    
    def cleanup(self):
        if self.shot_prompt != None:
            if os.path.exists(self.shot_prompt):
                os.remove(self.shot_prompt)


class Tacotron:
    def __init__(self, device: str) -> None:

        self.tts_tac_en = TTS("tts_models/en/ljspeech/tacotron2-DDC").to(device)
        self.tts_tac_ja = TTS("tts_models/ja/kokoro/tacotron2-DDC").to(device)
        self.tts_tac_es = TTS("tts_models/es/mai/tacotron2-DDC").to(device)
        self.tts_tac_zh = TTS("tts_models/zh-CN/baker/tacotron2-DDC-GST").to(device)
        self.tts_tac_fr = TTS("tts_models/fr/mai/tacotron2-DDC").to(device)

        self.shot_prompt = None
        self.prompt_before = None
        atexit.register(self.cleanup)
        

    def tts(self, text: str, 
            language:str,
            prompt: str, 
            delete_file: bool = True):
        
        if language not in ["es", "fr", "en", "zh", "ja"]:
            raise ValueError(f"{self.__class__.__name__} does not support'{language}'!")
        
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

        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(prefix='Traco_',delete=delete_file, suffix=".wav")
        
        if language == "en":
            tts_tac = self.tts_tac_en
        if language == "ja":
            tts_tac = self.tts_tac_ja
        if language == "es":
            tts_tac = self.tts_tac_es
        if language == "zh":
            tts_tac = self.tts_tac_zh
        if language == "fr":
            tts_tac = self.tts_tac_fr

        tts_tac.tts_with_vc_to_file(
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


class Bark:
    def __init__(self,device: str) -> None:
        super().__init__()
        
        self.tts_bark = TTS("tts_models/multilingual/multi-dataset/bark").to(device)
        self.shot_prompt = None
        self.prompt_before = None
        atexit.register(self.cleanup)
                
    def tts(
        self, text: str, 
        language: str,
        prompt: str, 
        delete_file: bool = True
    ) -> tempfile.NamedTemporaryFile: 
        
        if language not in ["es", "en", "ja", "ru", "zh", "fr"]:
            raise ValueError(f"{self.__class__.__name__} does not support'{language}'!")
        
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

        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(prefix='Bark_',delete=delete_file, suffix=".wav")
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
        device: str,
    ) -> None:
        preload_models(device)
        self.device = device

    def tts(
        self,
        text: str,
        language:str,
        prompt: str,  # find corresbonding voive prompt according to you .mp4 file name 
        prompt_directory: str = "./prompt/vall_short_prompts",
        delete_file: bool = True,
    ):  
        if language not in ["en","zh","ja"]:
            raise ValueError(f"{self.__class__.__name__} does not support'{language}'!")

       
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

            
            audio_array = generate_audio(text=text, device=self.device,prompt=prompt_file_path)
            
            #tempfile.tempdir = "./prompt/temp_file"
            temp_file = tempfile.NamedTemporaryFile(prefix='vall_',delete=delete_file, suffix=".wav")
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

    def __init__(self, device: str ):

        self.voice_conver = TTS(
            model_name="voice_conversion_models/multilingual/vctk/freevc24",
            progress_bar=False,
        ).to("cuda:0")
        
        self.prompt_before = None
        self.shot_prompt = None
        atexit.register(self.cleanup)

    def tts(
        self,
        text: str,
        language:str,
        prompt: str, # Using .mp4 file to make shot prompt.        
        conver: bool = True,  # True for using FreeVC
        delete_file: bool = True,
    ):
        if language not in ["en", "ru", "fr", "es", "zh", "ar", "ja"]:
            raise ValueError(f"{self.__class__.__name__} does not support'{language}'!")
        ann_dict = {
            "zh": {"Female": "zh-CN-XiaoxiaoNeural", "Male": "zh-CN-YunjianNeural"},
            "ar": {"Female": "ar-SA-ZariyahNeural", "Male": "ar-SA-HamedNeural"},
            "es": {"Female": "es-ES-ElviraNeural", "Male": "es-ES-AlvaroNeural"},
            "en": {"Female": "es-US-PalomaNeural", "Male": "es-US-AlonsoNeural"},
            "ja": {"Female": "ja-JP-NanamiNeural", "Male": "ja-JP-KeitaNeural"},
            "ru": {"Female": "ru-RU-SvetlanaNeural", "Male": "ru-RU-DmitryNeural"},
            "fr": {"Female": "fr-FR-DeniseNeural", "Male": "fr-FR-HenriNeural"}
        }

        announcer = ann_dict[language]["Male"]
        key = config["AzureTts"]["subscription_key"]
        location = config["AzureTts"]["region"]
        speech_config = speechsdk.SpeechConfig(subscription=key, region=location)
        speech_config.speech_synthesis_voice_name = announcer
        #tempfile.tempdir = "./prompt/temp_file"
        temp_file = tempfile.NamedTemporaryFile(prefix='Micro_',delete=delete_file, suffix=".wav")
        audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_file.name)


        speechSynthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
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




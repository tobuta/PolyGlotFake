
import whisper
import torch
import os
class STT:
    def __init__(self,model_name="large",device:str = "cuda:0") -> None:
        self.model = whisper.load_model(model_name, 
                                        device=device,
                                        download_root=os.path.join(os.getcwd(), "whisper"))
    

    def transcribe(self, audio_path)->tuple:
        
        result = self.model.transcribe(audio_path)
        return result["text"], result["language"], result["segments"][0]["text"], result["segments"][0]["end"]



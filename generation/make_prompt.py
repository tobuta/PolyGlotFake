"""
make prompt for Bark and vall-e-x
"""
from preprocessing.text_to_speech import Vall, MakeBarkPrompt
import argparse


parser = argparse.ArgumentParser(description='generate prompt for vall and bark')
parser.add_argument('-f', '--file_dir', type=str, default="/houyang/ns235x/program/DataSet/raw_video/es", help='The mp4 video dir path')
parser.add_argument('-l', '--language', type=str, default="es", help='Input language for prompt making')
parser.add_argument('-d', '--device', type=str, default="cuda", help='Input device')




if __name__ == "__main__":

    args = parser.parse_args()
    
    if args.language == "en" or args.language == "zh" or args.language == "ja":
        vall_prompt = Vall(language=args.language, device=args.device)
        vall_prompt.generate_prompt(args.file_dir)
    
    if args.language == "es" or args.language == "en" or args.language == "ja":
        bark_prompt = MakeBarkPrompt(language=args.language, device=args.device)
        bark_prompt.generate_prompt(args.file_dir)
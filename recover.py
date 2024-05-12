import json
import shutil
from tqdm import tqdm

def reset_files(move_log_file):
    # Read the move log
    with open(move_log_file, 'r') as log_file:
        move_log = json.load(log_file)

    # Move each file back to its original location
    for dest_path, src_path in tqdm(move_log.items(), desc="Resetting files"):
        shutil.move(dest_path, src_path)
        
    print("Files have been reset to their original locations.")

if __name__ == "__main__":
    reset_files('move_log.json')

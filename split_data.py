import json
import os
import shutil
import argparse
from collections import defaultdict
import random
from tqdm import tqdm


def collect_mp4_files(root_dir):
    mp4_files = []
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.mp4'):
                mp4_files.append(os.path.join(root, file))
    return mp4_files

def move_files(file_list, all_files, dest_dir, move_log):
    for filename in tqdm(file_list, desc="Moving files"):
        # Find the full path from the list of all files
        src_path = next((f for f in all_files if os.path.basename(f) == filename), None)
        if src_path is None:
            continue  # Skip if file not found

        dest_path = os.path.join(dest_dir, filename)
        #shutil.move(src_path, dest_path)
        move_log[dest_path] = src_path

def process_video_json(file_path, train_ratio, valid_ratio):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Assuming the key for videos is 'videos'
    videos = data.get("videos") or data.get("video")

    # Count the number of videos for each combination of features
    feature_combinations = defaultdict(list)
    for video in videos:
        # For real videos, use 'lang'; for fake videos, use combination of features
        if 'lang' in video:
            key = video['lang']
        else:
            key = (video.get("tts_technique"), video.get("target_lang"), video.get("sync_tech"))

        feature_combinations[key].append(video)

    # Split into training, validation, and testing sets
    train_filenames = []
    valid_filenames = []
    test_filenames = []
    for key, video_list in feature_combinations.items():
        random.shuffle(video_list)  # Shuffle the order
        total_videos = len(video_list)
        train_end = int(total_videos * train_ratio)
        valid_end = train_end + int(total_videos * valid_ratio)

        train_set = video_list[:train_end]
        valid_set = video_list[train_end:valid_end] if valid_ratio > 0 else []
        test_set = video_list[valid_end:]

        # Append filenames to respective lists
        train_filenames.extend([video["filename"] for video in train_set])
        valid_filenames.extend([video["filename"] for video in valid_set])
        test_filenames.extend([video["filename"] for video in test_set])

        # Output the number of videos for each key in training, validation, and testing sets
        print(f"Key: {key}, Training set videos: {len(train_set)}, Validation set videos: {len(valid_set)}, Testing set videos: {len(test_set)}")

    return train_filenames, valid_filenames, test_filenames


def main():
    parser = argparse.ArgumentParser(description='Split videos into train, validation, and test sets.')
    parser.add_argument('--train_ratio', type=float,default=1, help='Ratio of training set')
    parser.add_argument('--valid_ratio', type=float, default=0, help='Ratio of validation set')
    args = parser.parse_args()

    # Calculate test_ratio
    test_ratio = 1 - args.train_ratio - args.valid_ratio
    if test_ratio < 0:
        raise ValueError("Sum of train_ratio and valid_ratio should be less than 1.")

    # Check and create necessary directories
    raw_folder_fake = 'raw_dataset/fake'
    raw_folder_real = 'raw_dataset/real'
    folder_path = 'json_file'
    split_folder = 'split_dataset'
    subfolders = ['train', 'test', 'val' if args.valid_ratio > 0 else None]
    categories = ['real', 'fake']

    for subfolder in subfolders:
        if subfolder:
            for category in categories:
                os.makedirs(os.path.join(split_folder, subfolder, category), exist_ok=True)

    # Traverse the folder to find json files
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file == 'all_real_video.json':
                full_path = os.path.join(root, file)
                train_real, valid_real, test_real = process_video_json(full_path, args.train_ratio, args.valid_ratio)
                print(f"Processed {file}:")
                print(f"Train set: {len(train_real)}, Validation set: {len(valid_real)}, Test set: {len(test_real)}")

            if file == 'all_fake_video.json':
                full_path = os.path.join(root, file)
                train_fake, valid_fake, test_fake = process_video_json(full_path, args.train_ratio, args.valid_ratio)
                print(f"Processed {file}:")
                print(f"Train set: {len(train_fake)}, Validation set: {len(valid_fake)}, Test set: {len(test_fake)}")

    # Move files and log their original and new locations



    all_fake_mp4_files = collect_mp4_files(raw_folder_fake)
    all_real_mp4_files = collect_mp4_files(raw_folder_real)

    move_log = {}
    move_files(train_real, all_real_mp4_files, os.path.join(split_folder, 'train', 'real'), move_log)
    move_files(test_real, all_real_mp4_files, os.path.join(split_folder, 'test', 'real'), move_log)
    if args.valid_ratio > 0:
        move_files(valid_real, all_real_mp4_files, os.path.join(split_folder, 'val', 'real'), move_log)
    
    move_files(train_fake, all_fake_mp4_files, os.path.join(split_folder, 'train', 'fake'), move_log)
    move_files(test_fake, all_fake_mp4_files, os.path.join(split_folder, 'test', 'fake'), move_log)
    if args.valid_ratio > 0:
        move_files(valid_fake, all_fake_mp4_files, os.path.join(split_folder, 'val', 'fake'), move_log)

        
    # Save the move log to a JSON file
    with open('move_log.json', 'w') as log_file:
        json.dump(move_log, log_file, indent=4)

    print("Files have been moved and move log saved.")


if __name__ == "__main__":
    main()

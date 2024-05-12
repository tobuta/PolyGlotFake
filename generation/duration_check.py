import json

def find_long_videos(json_file_path):
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    long_video_names = []


    for video in data.get('video', []):

        if float(video.get('duration', '0')) > 20:
            long_video_names.append(video.get('name'))

    return long_video_names

json_file_path = '/houyang/ns235x/program/syclip_dataset_creation/data/to_ar/to_ar.json'
result = find_long_videos(json_file_path)
print(result)

import json


def calculate_average_duration(json_path):
    with open(json_path, 'r') as file:
        data = json.load(file)

    total_duration = 0
    count = 0

    for video in data["video"]:
        total_duration += float(video["duration"])
        count += 1

    
    average_duration = total_duration / count if count > 0 else 0
    return average_duration


def analyze_json_videos(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Count the total number of video dictionaries
        total_videos = len(data['videos'])

        # Count videos by language
        lang_count = {}
        for video in data['videos']:
            lang = video['lang']
            lang_count[lang] = lang_count.get(lang, 0) + 1

        return total_videos, lang_count
    except FileNotFoundError:
        return "File not found."
    except json.JSONDecodeError:
        return "Invalid JSON format."
    except KeyError:
        return "Expected keys not found in JSON."
    except Exception as e:
        return f"An error occurred: {e}"



def analyze_json_videos_v2(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Count the total number of video dictionaries
        total_videos = len(data['video'])

        # Count videos by target language
        target_lang_count = {}
        for video in data['video']:
            target_lang = video['target_lang']
            target_lang_count[target_lang] = target_lang_count.get(target_lang, 0) + 1

        return total_videos, target_lang_count
    except FileNotFoundError:
        return "File not found."
    except json.JSONDecodeError:
        return "Invalid JSON format."
    except KeyError:
        return "Expected keys not found in JSON."
    except Exception as e:
        return f"An error occurred: {e}"
    

def analyze_json_videos_by_technique(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Count videos by the combination of 'tts_technique' and 'sync_tech'
        technique_combo_count = {}
        for video in data['video']:
            combo = video['tts_technique'] + "_" + video['sync_tech']
            technique_combo_count[combo] = technique_combo_count.get(combo, 0) + 1

        return technique_combo_count
    except FileNotFoundError:
        return "File not found."
    except json.JSONDecodeError:
        return "Invalid JSON format."
    except KeyError:
        return "Expected keys not found in JSON."
    except Exception as e:
        return f"An error occurred: {e}"
    
def analyze_json_videos_by_age_and_sex_with_percentage(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Define age groups
        age_groups = {
            '0-18': 0,
            '19-35': 0,
            '36-55': 0,
            '56+': 0
        }
        
        # Initialize sex count
        sex_count = {'male': 0, 'female': 0}

        total_characters = 0

        for video in data['videos']:
            for character in video['characters']:
                total_characters += 1

                # Count by age group
                age = character['age']
                if age <= 18:
                    age_groups['0-20'] += 1
                elif 19 <= age <= 35:
                    age_groups['19-35'] += 1
                elif 36 <= age <= 55:
                    age_groups['36-55'] += 1
                else:
                    age_groups['56+'] += 1

                # Count by sex
                sex = character['sex']
                if sex in sex_count:
                    sex_count[sex] += 1

        # Calculate percentages
        age_groups_percentages = {k: v / total_characters * 100 for k, v in age_groups.items()}

        return age_groups, age_groups_percentages, sex_count
    except FileNotFoundError:
        return "File not found."
    except json.JSONDecodeError:
        return "Invalid JSON format."
    except KeyError:
        return "Expected keys not found in JSON."
    except Exception as e:
        return f"An error occurred: {e}"





json_path = '/houyang/ns235x/program/PolyGlotFake/json_file/fake_Json_file/all_fake_video.json' 
average_duration = calculate_average_duration(json_path)
print(f"The average duration is: {average_duration} seconds")


import subprocess
import tempfile
import os
import uuid



def extract_audio(
    video_path: str, 
    output_mode: str = "wav", 
    slice_time=None, 
    output_path=None
):
    """
    Extract audio from a video according to the specified slice time and output mode.

    Args:
        video_path (str): Path to the video file from which audio should be extracted.
        output_mode (str, optional): The desired output mode. If set to 'temp', the function
                                     will return the path of a temporary file. If set to 'wav',
                                     the function will output a .wav file. Defaults to "wav".
        slice_time (int or float, optional): Duration in seconds to extract from the beginning of
                                             the video. If not specified, the entire audio will
                                             be extracted. Defaults to None.
        output_path (str, optional): Path where the extracted audio should be saved when
                                     output_mode is 'wav'. If not specified when output_mode
                                     is 'wav', an error is raised. Defaults to None.

    Raises:
        ValueError: If an invalid output mode is specified or if output path is not provided
                    for 'wav' mode.

    Returns:
        str: Path to the extracted audio file. If output_mode is 'temp', this will be a temporary file path.
    """
    if output_mode == "temp":
        #
        unique_id = str(uuid.uuid4())
        dir_path = './prompt/temp_file'
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        target_path = os.path.join(dir_path, f'{unique_id}.wav')
        
    elif output_mode == "wav" and output_path:
        target_path = output_path
    else:
        raise ValueError("Invalid output mode or path not provided for 'wav' mode")

    cmd = ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a"]
    if slice_time:
        cmd.extend(["-t", str(slice_time)])
    cmd.append(target_path)
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if output_mode == "temp":
        return target_path



def get_duration(file_path):
# First, try to get duration from video stream
    cmd_video = [
        "ffprobe", 
        "-v", "error", 
        "-select_streams", "v:0", 
        "-show_entries", "stream=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]
    
    # Then, try to get duration from audio stream
    cmd_audio = [
        "ffprobe", 
        "-v", "error", 
        "-select_streams", "a:0", 
        "-show_entries", "stream=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", 
        file_path
    ]

    try:
        # Try video first
        duration = subprocess.check_output(cmd_video, universal_newlines=True, stderr=subprocess.STDOUT).strip()
        if not duration:  # If no video duration, try audio
            duration = subprocess.check_output(cmd_audio, universal_newlines=True, stderr=subprocess.STDOUT).strip()
        return float(duration)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e.output}")
        return None



def merge_audio_video(video_path, audio_path, output_path):
    """
    Merge a video file with an audio file, adjusting their durations to match each other.

    If the video is longer than the audio:
    - The video is trimmed to match the audio duration, and then they are merged.

    If the audio is longer than the video:
    - A segment is extracted from the end of the video, which has a duration equal to
      the difference between the audio and video durations.
    - This segment is reversed (both video and audio) and appended to the original video.
    - The extended video is then merged with the original audio.

    Parameters:
    - video_path (str): Path to the video file.
    - audio_path (str): Path to the audio file.
    - output_path (str): Path to save the merged output file.

    Intermediate files are stored in a temporary directory "./prompt/temp_file_prompt" and are 
    removed after processing.

    Note:
    - The function uses FFmpeg for video and audio processing, so FFmpeg should be installed 
      and accessible from the command line.
    - The `get_duration` function is required to fetch the duration of media files.

    Example:
    merge_audio_video("sample_video.mp4", "sample_audio.wav", "output_video.mp4")
    """
    video_duration = get_duration(video_path)
    audio_duration = get_duration(audio_path)

    # if audio_duration > 2 * video_duration:
    #     raise ValueError("Error: The audio duration is more than twice the video duration. Audio is too long.")

    temp_dir = os.path.join("./prompt", str(uuid.uuid4()))
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    def temp_file_path(filename):
        return os.path.join(temp_dir, filename)

    # Case where video is longer than audio
    if video_duration > audio_duration:
        # Trim video to match the audio duration

        trimmed_video = str(uuid.uuid4()) + ".mp4"
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-t", str(audio_duration),
            "-an",  # Disable audio
            temp_file_path(trimmed_video),
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        video_path_to_merge = temp_file_path(trimmed_video)

    # Case where audio is longer than video
    elif video_duration < audio_duration:
        if audio_duration > 2 * video_duration:
            # Trim audio to match the video duration

            trimmed_audio = str(uuid.uuid4()) + ".wav"
            cmd = [
                "ffmpeg",
                "-i", audio_path,
                "-t", str(video_duration),
                temp_file_path(trimmed_audio),
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            audio_path = temp_file_path(trimmed_audio)  # Use trimmed audio for merge
            video_path_to_merge = video_path

        else:
            trim_duration = audio_duration - video_duration
            # Trim the video from the end

            tail_clip = str(uuid.uuid4()) + ".mp4"
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-ss", str(video_duration - trim_duration),
                "-t", str(trim_duration),
                "-an",  # Disable audio
                temp_file_path(tail_clip),
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Reverse the trimmed clip
            reversed_tail_clip = str(uuid.uuid4()) + ".mp4"
            cmd = [
                "ffmpeg",
                "-i", temp_file_path(tail_clip),
                "-vf", "reverse",
                "-af", "areverse",
                temp_file_path(reversed_tail_clip),
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Concatenate the reversed clip with the original video
            concat_video = str(uuid.uuid4()) + ".mp4"
            cmd = [
                "ffmpeg",
                "-i", video_path,
                "-i", temp_file_path(reversed_tail_clip),
                "-filter_complex",
                "[0:v][1:v]concat=n=2:v=1:a=0",
                "-an",  # Disable audio
                temp_file_path(concat_video),
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            video_path_to_merge = temp_file_path(concat_video)

    else:  # When video and audio have the same duration
        video_path_to_merge = video_path

    # Merge video and audio
    cmd = [
        "ffmpeg",
        "-i", video_path_to_merge,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-strict", "experimental",
        "-map", "0:v",   
        "-map", "1:a",  
        output_path,
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # result = subprocess.run(cmd, capture_output=True, text=True)
    # print(result.stdout)
    # print(result.stderr)

    # Remove the temp directory and its contents
    for item in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, item))
    os.rmdir(temp_dir)



if __name__ == "__main__":
    pass
import subprocess

def separate_audio(input_path, output_dir="output/"):
    """
    Use Spleeter to separate audio tracks without showing its output.

    Parameters:
    - input_path: Path to the input audio file.
    - output_dir: Directory where the separated tracks will be saved.
    """
    
    # Define the spleeter command
    cmd = ["spleeter", "separate", "-o", output_dir, input_path]
    
    # Execute the command without showing its output
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Usage example
if __name__ == "__main__":
    input_audio = "audio_example.mp3"
    separate_audio(input_audio)

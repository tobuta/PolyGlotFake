# PolyGlotFake Dataset

## Overview
PolyGlotFake is a novel multilingual and multimodal deepfake dataset meticulously designed to address the challenges and demands of deepfake detection technologies. It consists of videos with manipulated audio and visual components across seven languages, employing advanced Text-to-Speech, voice cloning, and lip-sync technologies. This dataset not only enhances the rigor of multimodal deepfake detection research but also contributes to understanding the nuances of linguistic diversity in deepfake generation.

![Overview of Dataset](path/to/dataset_overview_image.png)

## Dataset Details
### Composition
- **Total Videos**: 15,238
  - **Real Videos**: 766
  - **Fake Videos**: 14,472
- **Resolution**: 1280x720
- **Average Video Duration**: 11.79 seconds

### Languages Covered
- English
- French
- Spanish
- Russian
- Chinese
- Arabic
- Japanese

![Language Distribution](path/to/language_distribution_image.png)

### Video Examples
Below are some examples from the dataset showing the diversity and complexity of the videos included.
![Video Samples](path/to/video_samples_image.png)

## Generation Process
1. **Separation of Video and Audio**: Initially, videos are dissected into separate audio and visual tracks.
2. **Audio Transcription**: Audio tracks are transcribed to text using advanced AI-based tools like Whisper.
3. **Text Translation**: The transcribed texts are then translated into the other six languages included in the dataset.
4. **Text-to-Speech (TTS)**: These translated texts are transformed back into spoken audio using various TTS technologies.
5. **Lip Syncing**: The newly generated audio is synchronized with the video tracks using state-of-the-art lip-sync technologies.

![Generation Pipeline](path/to/generation_pipeline_image.png)

## Key Technologies Employed
- **Text-to-Speech Engines**: XTTS, Microsoft TTS + FreeVC, Tacotron + FreeVC
- **Lip Sync Technologies**: Wav2Lip + GANs, VideoRetalking

## How to Use
To access the PolyGlotFake dataset, please visit our [GitHub repository](https://github.com/tobuta/PolyGlotFake). Detailed instructions for downloading and using the dataset are provided there.

## Citation
Please cite the following paper if you use the PolyGlotFake dataset in your research:


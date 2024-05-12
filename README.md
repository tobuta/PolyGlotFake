# PolyGlotFake Dataset

## Description
PolyGlotFake is an innovative multilingual and multimodal deepfake dataset designed to advance the research and development in deepfake detection technologies. This dataset includes content in seven languages, created using cutting-edge Text-to-Speech, voice cloning, and lip-sync technologies, presenting significant challenges and practical value for research in multimodal deepfake detection.

## Dataset Composition
- **Total Videos**: 15,238
  - **Real Videos**: 766
  - **Fake Videos**: 14,472
- **Resolution**: 1280x720
- **Average Duration**: 11.79 seconds
- **Languages**: English, French, Spanish, Russian, Chinese, Arabic, Japanese

## Generation Pipeline
1. **Video and Audio Separation**: Original videos are separated into video and audio components.
2. **Audio Transcription**: Audio is transcribed to text using Whisper.
3. **Text Translation**: Transcribed texts are translated into multiple languages.
4. **Text-to-Speech**: Translated texts are converted back into audio using various TTS models.
5. **Lip Syncing**: The generated audios are synchronized with the original video using lip-sync models.

## Key Technologies
- **Text-to-Speech**: XTTS, Microsoft TTS + FreeVC, Tacotron + FreeVC
- **Lip Syncing**: Wav2Lip + GANs, VideoRetalking

## Usage
Please visit the [PolyGlotFake GitHub page](https://github.com/tobuta/PolyGlotFake) to download the dataset and associated code.

## Citation
If you use the PolyGlotFake dataset in your research, please cite our paper:

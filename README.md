# PolyGlotFake Dataset

## Overview
PolyGlotFake is a novel multilingual and multimodal deepfake dataset meticulously designed to address the challenges and demands of deepfake detection technologies. It consists of videos with manipulated audio and visual components across seven languages, employing advanced Text-to-Speech, voice cloning, and lip-sync technologies. 

![Overview of Dataset](./images/visualization.jpg)

## Dataset Details
### Composition
- **Total Videos**: 15,238
  - **Real Videos**: 766
  - **Fake Videos**: 14,472
- **Resolution**: 1280x720
- **Average Video Duration**: 11.79 seconds

### Languages and Synthesis Methods Distribution
- Language: English; French; Spanish; Russian; Chinese; Arabic; Japanese
- Synthesis methods:
  Audio manipulation: Bark+FreeVC; MicroTTS+FreeVC; XTTS; Tacotron+FreeVC; Vall-E-X
  Video manipulation: VideoRetalking; Wav2Lip

<p float="left">
  <img src="./images/lang_new.jpg" width="45%" />
  <img src="./images/tech.jpg" width="45%" /> 
</p>

## Generation Pipeline
![Generation Pipeline](./images/pipeline.jpg)

## Key Technologies Employed
- **Text-to-Speech Engines**: XTTS, Microsoft TTS + FreeVC, Tacotron + FreeVC
- **Lip Sync Technologies**: Wav2Lip + GANs, VideoRetalking

## Deepfake Detection Benchmark


## Citation
Please cite the following paper if you use the PolyGlotFake dataset in your research:


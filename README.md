<div align="center">

<img src="https://raw.githubusercontent.com/AppSolves/captametropolis/master/assets/captametropolis_readme.png" alt="readmepic" width="640" height="320" style="border-radius: 25px;">

-----

Check out these examples with captions added using **Captametropolis** (by [CurioBurstz](https://www.youtube.com/@curioburstz?sub_confirmation=1)):

<a href="http://www.youtube.com/watch?v=C1nqHA2-YIk" title="Why Flamingos Are Pink: The Fascinating Reason Behind Their Color!">
  <img src="http://img.youtube.com/vi/C1nqHA2-YIk/0.jpg" alt="CurioBurstz No. 1" width="300" height="225" hspace="25">
</a>
<a href="http://www.youtube.com/watch?v=1Wik3XewG40" title="Why You Get Dizzy After Spinning: The Science Explained!">
  <img src="http://img.youtube.com/vi/1Wik3XewG40/0.jpg" alt="CurioBurstz No. 2" width="300" height="225">
</a>

-----

# `Captametropolis`

![GitHub issues](https://img.shields.io/github/issues/AppSolves/captametropolis)
![GitHub pull requests](https://img.shields.io/github/issues-pr/AppSolves/captametropolis)

[![Stargazers repo roster for @AppSolves/captametropolis](https://reporoster.com/stars/dark/AppSolves/captametropolis)](https://github.com/AppSolves/captametropolis/stargazers)
[![Forkers repo roster for @AppSolves/captametropolis](https://reporoster.com/forks/dark/AppSolves/captametropolis)](https://github.com/AppSolves/captametropolis/network/members)

<h4><code>Captametropolis</code> brings next-level automated captions to your YouTube Shorts and other videos using Whisper and MoviePy.</h4>

[Introduction](#introduction-) • [Features](#features-) • [Installation](#installation-%EF%B8%8F) • [Usage](#usage-) • [Customization](#customization-) • [License](#license-)

</div>

<br />

> 👋 Welcome to **Captametropolis**, a tool designed to make your videos even more engaging with stunning automatic captions! The process is seamless, fast, and adds flair to your content.

# Captametropolis ✨

## Introduction 📖
> Forked from [unconv/captacity](https://github.com/unconv/captacity)
>
> Just like captacity, but **BIGGER**!

**Captametropolis** takes video captioning to a new level! Whether you're making YouTube Shorts, TikToks, or any other type of video content, Captametropolis helps you effortlessly add beautiful, dynamic captions with precision using **Whisper** for speech recognition and **MoviePy** for video editing.

## Features 🚀
- **Automatic Captions**: Powered by Whisper, Captametropolis transcribes your video and adds captions with ease.
- **Custom Fonts & Styles**: Customize your captions with unique fonts, colors, sizes, shadows, and more.
- **Highlight Words**: Focus attention on important parts by highlighting specific words in real-time.
- **Local & API Whisper Support**: Use OpenAI's Whisper locally or via API for transcription.
- **Programmatic Integration**: Easily integrate Captametropolis into your Python projects.
  
## Installation 🛠️

### Prerequisites 📦
Make sure to install the following:
1. **FFmpeg**: Download the latest version from [here](https://ffmpeg.org/download.html) and ensure it’s added to your `PATH`.
2. **ImageMagick**: Download from [here](https://imagemagick.org/script/download.php), making sure to select:
    - Install legacy utilities (e.g. `convert`)
    - Add application directory to your system `PATH`.

### Install Captametropolis ⚙️

To install the latest version of Captametropolis, run the following command:

```bash
pip install captametropolis -U
```

Once installed, you can add captions to a video by running:

```bash
captametropolis <video_file> <output_file>
```

## Font Registration 🎨

To use custom fonts in your captions, register them with ImageMagick. Run the following in **admin mode**:

```bash
captametropolis register_font "path/to/your/font.ttf" -qr
```

Alternatively, register fonts programmatically in Python:

```python
from captametropolis.utils import register_font

register_font("path/to/your/font.ttf", quiet_run=True)  # Will also ask for admin rights
```

## Programmatic Use 💻

Easily add captions to your videos programmatically using Captametropolis:

```python
import captametropolis

captametropolis.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
    font_path="path/to/your/font.ttf",  # Use your custom font here
)
```

## Customization 🎨

Customize your captions with full control over fonts, colors, effects, and more! Check out the customizable parameters:

```python
captametropolis.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",

    font_path = "/path/to/your/font.ttf",
    font_size = 130,
    font_color = "yellow",

    stroke_width = 3,
    stroke_color = "black",

    shadow_strength = 1.0,
    shadow_blur = 0.1,

    highlight_current_word = True,
    highlight_color = "red",

    line_count=1,
    rel_width = 0.8,  # Relative width of the text box
)
```

## Using Whisper Locally vs API 🧠

By default, Captametropolis uses OpenAI’s Whisper locally if the `openai-whisper` package is installed. If you want to use the OpenAI Whisper API instead, you can force this behavior:

```python
captametropolis.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
    use_local_whisper=False,  # Use the OpenAI Whisper API
)
```

To install Whisper locally, run:

```bash
pip install captametropolis[local] -U
```

## Conclusion 🎉
**Captametropolis** makes adding captions to your videos as simple as it is powerful! Enhance your videos and reach a wider audience with engaging captions. 🚀

## License 📜
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.
# Captametropolis

> **INFO**: This is forked from [Captacity](https://github.com/unconv/captacity).
> 
> Just like Captacity but BIGGER! 

Add automatic captions to YouTube Shorts (and other videos) using Whisper and MoviePy!

## Requirements

- Install [FFmpeg](https://ffmpeg.org/download.html) (make sure it's in your `PATH`)
- Install [ImageMagick](https://imagemagick.org/script/download.php). Make sure to tick both boxes during installation:

    - Install legacy utilities (e.g. convert)
    - Add application directory to your system path


## Quick start

After installing the requirements, make sure to enter your terminal in **administrator mode** and run the following commands:

```bash
$ pip install captametropolis -U
$ captametropolis <video_file> <output_file>
```

> **INFO**: You need to run `Captametropolis` in administrator mode because it has to inject your fonts into the ImageMagick font directory.

## Programmatic use

```python
import captametropolis

captametropolis.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
)
```

## Custom configuration

```python
import captametropolis

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

    rel_width = 0.8,
)
```

## Using Whisper locally

By default, OpenAI Whisper is used locally if the `openai-whisper` package is installed. Otherwise, the OpenAI Whisper API is used. If you want to force the use of the API, you can specify `use_local_whisper=False` in the arguments to `captametropolis.add_captions`:

```python
import captametropolis

captametropolis.add_captions(
    video_file="my_short.mp4",
    output_file="my_short_with_captions.mp4",
    use_local_whisper=False,
)
```

You can install Captametropolis with `pip install captametropolis[local]` to install Whisper locally as well.

import os
import tempfile
import time

import ffmpeg
from moviepy.config import change_settings
from moviepy.editor import CompositeVideoClip, VideoFileClip

from . import segment_parser, transcriber
from .__version__ import __version__
from .errors import UtilityNotFoundError
from .text_drawer import Word, create_shadow, create_text_ex, get_text_size_ex
from .utils import (
    _get_font_path,
    ffmpeg_binary,
    ffmpeg_installed,
    imagemagick_binary,
    is_local_transcription_available,
)

__all__ = [
    "__version__",
    "add_captions",
    "ffmpeg_installed",
    "imagemagick_binary",
    "is_local_transcription_available",
]

lines_cache = {}

if not ffmpeg_installed():
    raise UtilityNotFoundError("FFmpeg")
else:
    change_settings({"FFMPEG_BINARY": ffmpeg_binary()})
    os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_binary()

if imagemagick_binary() == "unset":
    raise UtilityNotFoundError("ImageMagick")
elif not os.path.exists(imagemagick_binary()):
    raise FileNotFoundError(f"ImageMagick binary '{imagemagick_binary()}' not found")
else:
    change_settings({"IMAGEMAGICK_BINARY": imagemagick_binary()})


def fits_frame(line_count, font: tuple[str, str], font_size, stroke_width, frame_width):
    def fit_function(text):
        lines = calculate_lines(text, font, font_size, stroke_width, frame_width)
        return len(lines["lines"]) <= line_count

    return fit_function


def calculate_lines(
    text,
    font: tuple[str, str],
    font_size,
    stroke_width,
    frame_width,
    verbose: bool = False,
):
    global lines_cache

    arg_hash = hash((text, font, font_size, stroke_width, frame_width))

    if arg_hash in lines_cache:
        return lines_cache[arg_hash]

    lines = []

    line_to_draw = None
    line = ""
    words = text.split()
    word_index = 0
    total_height = 0
    while word_index < len(words):
        word = words[word_index]
        line += word + " "
        text_size = get_text_size_ex(line.strip(), font, font_size, stroke_width)
        text_width = text_size[0]
        line_height = text_size[1]

        if text_width < frame_width:
            line_to_draw = {
                "text": line.strip(),
                "height": line_height,
            }
            word_index += 1
        else:
            if not line_to_draw:
                if verbose:
                    print(f"NOTICE: Word '{line.strip()}' is too long for the frame!")
                line_to_draw = {
                    "text": line.strip(),
                    "height": line_height,
                }
                word_index += 1

            lines.append(line_to_draw)
            total_height += line_height
            line_to_draw = None
            line = ""

    if line_to_draw:
        lines.append(line_to_draw)
        total_height += line_height

    data = {
        "lines": lines,
        "height": total_height,
    }

    lines_cache[arg_hash] = data

    return data


def add_captions(
    video_file: str,
    output_file: str = "with_transcript.mp4",
    font_path: str = "Bangers-Regular.ttf",
    font_size: int = 100,
    font_color: str = "white",
    stroke_width: int = 3,
    stroke_color: str = "black",
    highlight_current_word: bool = True,
    highlight_color: str = "yellow",
    line_count: int = 2,
    fit_function=None,
    rel_width: float = 0.6,
    rel_height_pos: float = 0.5,  # TODO: Implement this
    shadow_strength: float = 1.0,
    shadow_blur: float = 0.1,
    verbose: bool = False,
    initial_prompt: str | None = None,
    segments=None,
    model_name: str = "base",
    use_local_whisper: str | bool = "auto",
    temp_audiofile: str | None = None,
):
    _start_time = time.time()

    font_path, injected_font_name = _get_font_path(font_path)

    if verbose:
        print("Extracting audio...")

    temp_audiofile = temp_audiofile or tempfile.NamedTemporaryFile(suffix=".wav").name
    ffmpeg.input(video_file).output(
        temp_audiofile, loglevel="info" if verbose else "quiet"
    ).run(overwrite_output=True)

    if segments is None:
        if verbose:
            print("Transcribing audio...")

        if use_local_whisper == "auto":
            use_local_whisper = is_local_transcription_available(verbose)

        if use_local_whisper:
            segments = transcriber.transcribe_locally(
                audio_file=temp_audiofile, prompt=initial_prompt, model_name=model_name
            )
        else:
            segments = transcriber.transcribe_with_api(
                audio_file=temp_audiofile, prompt=initial_prompt
            )

    if verbose:
        print("Generating video elements...")

    # Open the video file
    video = VideoFileClip(video_file)
    text_bbox_width = video.w * rel_width
    clips = [video]

    captions = segment_parser.parse(
        segments=segments,
        fit_function=(
            fit_function
            if fit_function
            else fits_frame(
                line_count,
                (injected_font_name, font_path),
                font_size,
                stroke_width,
                text_bbox_width,
            )
        ),
    )

    for caption in captions:
        captions_to_draw = []
        if highlight_current_word:
            for i, word in enumerate(caption["words"]):
                if i + 1 < len(caption["words"]):
                    end = caption["words"][i + 1]["start"]
                else:
                    end = word["end"]

                captions_to_draw.append(
                    {
                        "text": caption["text"],
                        "start": word["start"],
                        "end": end,
                    }
                )
        else:
            captions_to_draw.append(caption)

        for current_index, caption in enumerate(captions_to_draw):
            line_data = calculate_lines(
                caption["text"],
                (injected_font_name, font_path),
                font_size,
                stroke_width,
                text_bbox_width,
                verbose=verbose,
            )

            text_y_offset = video.h * (1 - rel_height_pos) - line_data["height"] // 2
            index = 0
            for line in line_data["lines"]:
                pos = ("center", text_y_offset)

                words = line["text"].split()
                word_list = []
                for w in words:
                    word_obj = Word(w)
                    if highlight_current_word and index == current_index:
                        word_obj.set_color(highlight_color)
                    index += 1
                    word_list.append(word_obj)

                # Create shadow
                shadow_left = shadow_strength
                while shadow_left >= 1:
                    shadow_left -= 1
                    shadow = create_shadow(
                        line["text"],
                        font_size,
                        (injected_font_name, font_path),
                        shadow_blur,
                        opacity=1,
                    )
                    shadow = shadow.set_start(caption["start"])
                    shadow = shadow.set_duration(caption["end"] - caption["start"])
                    shadow = shadow.set_position(pos)
                    clips.append(shadow)

                if shadow_left > 0:
                    shadow = create_shadow(
                        line["text"],
                        font_size,
                        (injected_font_name, font_path),
                        shadow_blur,
                        opacity=shadow_left,
                    )
                    shadow = shadow.set_start(caption["start"])
                    shadow = shadow.set_duration(caption["end"] - caption["start"])
                    shadow = shadow.set_position(pos)
                    clips.append(shadow)

                # Create text
                text = create_text_ex(
                    word_list,
                    font_size,
                    font_color,
                    (injected_font_name, font_path),
                    stroke_color=stroke_color,
                    stroke_width=stroke_width,
                )
                text = text.set_start(caption["start"])
                text = text.set_duration(caption["end"] - caption["start"])
                text = text.set_position(pos)
                clips.append(text)

                text_y_offset += line["height"]

    end_time = time.time()
    generation_time = end_time - _start_time

    if verbose:
        print(
            f"Generated in {generation_time//60:02.0f}:{generation_time%60:02.0f} ({len(clips)} clips)"
        )

    if verbose:
        print("Rendering video...")

    video_with_text = CompositeVideoClip(clips)

    video_with_text.write_videofile(
        filename=output_file,
        codec="libx264",
        fps=video.fps,
        logger="bar" if verbose else None,
        temp_audiofile=temp_audiofile,
    )

    end_time = time.time()
    total_time = end_time - _start_time
    render_time = total_time - generation_time

    if verbose:
        print(f"Generated in {generation_time//60:02.0f}:{generation_time%60:02.0f}")
        print(f"Rendered in {render_time//60:02.0f}:{render_time%60:02.0f}")
        print(f"Done in {total_time//60:02.0f}:{total_time%60:02.0f}")

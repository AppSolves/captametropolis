import os
import tempfile
import time

import ffmpeg
from moviepy.editor import CompositeVideoClip, VideoFileClip

from . import segment_parser, transcriber
from .text_drawer import Word, blur_text_clip, create_text_ex, get_text_size_ex

shadow_cache = {}
lines_cache = {}


def fits_frame(line_count, font, font_size, stroke_width, frame_width):
    def fit_function(text):
        lines = calculate_lines(text, font, font_size, stroke_width, frame_width)
        return len(lines["lines"]) <= line_count

    return fit_function


def calculate_lines(
    text,
    font,
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


def create_shadow(
    text: str, font_size: int, font: str, blur_radius: float, opacity: float = 1.0
):
    global shadow_cache

    arg_hash = hash((text, font_size, font, blur_radius, opacity))

    if arg_hash in shadow_cache:
        return shadow_cache[arg_hash].copy()

    shadow = create_text_ex(text, font_size, "black", font, opacity=opacity)
    shadow = blur_text_clip(shadow, int(font_size * blur_radius))

    shadow_cache[arg_hash] = shadow.copy()

    return shadow


def get_font_path(font):
    if os.path.exists(font):
        return font

    dirname = os.path.dirname(__file__)
    font = os.path.join(dirname, "assets", "fonts", font)

    if not os.path.exists(font):
        raise FileNotFoundError(f"Font '{font}' not found")

    return font


def detect_local_whisper(print_info):
    try:
        import whisper

        use_local_whisper = True
        if print_info:
            print("Using local whisper model...")
    except ImportError:
        use_local_whisper = False
        if print_info:
            print("Using OpenAI Whisper API...")

    return use_local_whisper


def add_captions(
    video_file: str,
    output_file: str = "with_transcript.mp4",
    font: str = "Bangers-Regular.ttf",
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

    font = get_font_path(font)

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
            use_local_whisper = detect_local_whisper(verbose)

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
                font,
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
                font,
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
                        font,
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
                        font,
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
                    font,
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

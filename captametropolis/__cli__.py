#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Annotated, Literal, Optional

import typer
import typer.core

from captametropolis import add_captions


class AliasGroup(typer.core.TyperGroup):
    _CMD_SPLIT_P = r"[,| ?\/]"

    def get_command(self, ctx, cmd_name):
        cmd_name = self._group_cmd_name(cmd_name)
        return super().get_command(ctx, cmd_name)

    def _group_cmd_name(self, default_name):
        for cmd in self.commands.values():
            if cmd.name and default_name in re.split(self._CMD_SPLIT_P, cmd.name):
                return cmd.name
        return default_name


set_password: Optional[str] = None
app: typer.Typer = typer.Typer(
    name="Captametropolis",
    help=":sparkles: An [italic]awesome[/italic] [orange1]CLI tool[/orange1] to add captions to your videos. :movie_camera: :closed_caption: :rocket:",
    rich_markup_mode="rich",
    epilog="Made with [red]:red_heart:[/red]  and :muscle: by [cyan]AppSolves[/cyan] | [blue link=https://github.com/AppSolves/captametropolis]GitHub[/blue link]",
    cls=AliasGroup,
    context_settings={
        "help_option_names": ["-h", "--help", "-?"],
    },
)


@app.command(
    name="add_caption",
    help="Add captions to a video file.",
)
def create(
    video_file: Annotated[
        Path,
        typer.Argument(
            ...,
            help="The path to the video file to which captions will be added.",
            show_default=False,
        ),
    ],
    output_file: Annotated[
        Path,
        typer.Argument(
            ...,
            help="The path to the output video file with captions added.",
            show_default=False,
        ),
    ],
    font_path: Annotated[
        Optional[Path],
        typer.Option(
            ...,
            "--font-path",
            "-fp",
            help="The path to the font file to be used for the captions.",
        ),
    ] = "Bangers-Regular.ttf",
    font_size: Annotated[
        Optional[int],
        typer.Option(
            ...,
            "--font-size",
            "-fs",
            help="The size of the font to be used for the captions.",
        ),
    ] = 100,
    font_color: Annotated[
        Optional[str],
        typer.Option(
            ...,
            "--font-color",
            "-fc",
            help="The color of the font to be used for the captions.",
        ),
    ] = "white",
    stroke_width: Annotated[
        Optional[int],
        typer.Option(
            ...,
            "--stroke-width",
            "-sw",
            help="The width of the stroke to be used for the captions.",
        ),
    ] = 3,
    stroke_color: Annotated[
        Optional[str],
        typer.Option(
            ...,
            "--stroke-color",
            "-sc",
            help="The color of the stroke to be used for the captions.",
        ),
    ] = "black",
    highlight_current_word: Annotated[
        Optional[bool],
        typer.Option(
            ...,
            "--highlight-current-word",
            "-hcw",
            help="Highlight the current word being spoken in the captions.",
        ),
    ] = True,
    highlight_color: Annotated[
        Optional[str],
        typer.Option(
            ...,
            "--highlight-color",
            "-hc",
            help="The color of the highlight to be used for the current word.",
        ),
    ] = "yellow",
    line_count: Annotated[
        Optional[int],
        typer.Option(
            ...,
            "--line-count",
            "-lc",
            help="The number of lines to be displayed in the captions.",
        ),
    ] = 2,
    rel_width: Annotated[
        Optional[float],
        typer.Option(
            ...,
            "--rel-width",
            "-rw",
            help="The relative width of the captions to the video frame.",
        ),
    ] = 0.6,
    rel_height_pos: Annotated[
        Optional[float],
        typer.Option(
            ...,
            "--rel-height-pos",
            "-rhp",
            help="The relative height position of the captions in the video frame.",
        ),
    ] = 0.5,
    shadow_strength: Annotated[
        Optional[float],
        typer.Option(
            ...,
            "--shadow-strength",
            "-ss",
            help="The strength of the shadow to be used for the captions.",
        ),
    ] = 1.0,
    shadow_blur: Annotated[
        Optional[float],
        typer.Option(
            ...,
            "--shadow-blur",
            "-sb",
            help="The blur of the shadow to be used for the captions.",
        ),
    ] = 0.1,
    verbose: Annotated[
        Optional[bool],
        typer.Option(
            ...,
            "--verbose",
            "-v",
            help="Show verbose output.",
        ),
    ] = False,
    initial_prompt: Annotated[
        Optional[str],
        typer.Option(
            ...,
            "--initial-prompt",
            "-ip",
            help="The initial prompt to be passed to Whisper.",
        ),
    ] = None,
    model_name: Annotated[
        Optional[str],
        typer.Option(
            ...,
            "--model-name",
            "-mn",
            help="The name of the model to be used for Whisper.",
        ),
    ] = "base",
    use_local_whisper: Annotated[
        Optional[Literal["auto"] | bool],
        typer.Option(
            ...,
            "--use-local-whisper",
            "-ulw",
            help="Use the local Whisper model if available.",
        ),
    ] = "auto",
    temp_audiofile: Annotated[
        Optional[Path],
        typer.Option(
            ...,
            "--temp-audiofile",
            "-ta",
            help="The path to the temporary audio file to be used for Whisper.",
        ),
    ] = None,
):
    add_captions(
        video_file=video_file,
        output_file=output_file,
        font_path=font_path,
        font_size=font_size,
        font_color=font_color,
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        highlight_current_word=highlight_current_word,
        highlight_color=highlight_color,
        line_count=line_count,
        rel_width=rel_width,
        rel_height_pos=rel_height_pos,
        shadow_strength=shadow_strength,
        shadow_blur=shadow_blur,
        verbose=verbose,
        initial_prompt=initial_prompt,
        model_name=model_name,
        use_local_whisper=use_local_whisper,
        temp_audiofile=temp_audiofile,
    )

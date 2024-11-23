#!/usr/bin/env python3

import re
from pathlib import Path
from typing import Annotated, Optional

import typer
import typer.core

from captametropolis import add_captions
from captametropolis.__version__ import __version__
from captametropolis.utils import is_font_registered, register_font, unregister_font


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


app: typer.Typer = typer.Typer(
    name="Captametropolis",
    help=":sparkles: An [italic]awesome[/italic] [orange1]CLI tool[/orange1] to add captions to your videos. :movie_camera: :rocket:",
    rich_markup_mode="rich",
    epilog=f"Made with [red]:red_heart:[/red]  and :muscle: by [cyan link=https://github.com/AppSolves]AppSolves[/cyan link] | [blue link=https://github.com/AppSolves/captametropolis]GitHub[/blue link] | [green]v{__version__}[/green] from [yellow link=https://pypi.org/project/captametropolis/]PyPI[/yellow link]",
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
            show_default=False,
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
        Optional[bool],
        typer.Option(
            ...,
            "--use-local-whisper",
            "-ulw",
            help="Use the local Whisper model if available.",
        ),
    ] = True,
    temp_audiofile: Annotated[
        Optional[Path],
        typer.Option(
            ...,
            "--temp-audiofile",
            "-ta",
            help="The path to the temporary audio file to be used for Whisper.",
            show_default=False,
        ),
    ] = None,
):
    add_captions(
        video_file=str(video_file.resolve()),
        output_file=str(output_file.resolve()),
        font_path=str(font_path.resolve()),
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
        temp_audiofile=str(temp_audiofile.resolve()) if temp_audiofile else None,
    )


@app.command(
    name="register_font",
    help="Register a font file to be used for captions.",
)
def register_font_cmd(
    font_path: Annotated[
        Path,
        typer.Argument(
            ...,
            help="The path to the font file to be registered.",
            show_default=False,
        ),
    ],
    quiet_run: Annotated[
        Optional[bool],
        typer.Option(
            ...,
            "--quiet-run",
            "-qr",
            help="Run the command quietly without any output or console.",
        ),
    ] = False,
    verbose: Annotated[
        Optional[bool],
        typer.Option(
            ...,
            "--verbose",
            "-v",
            help="Show verbose output.",
        ),
    ] = False,
):
    registered_font_name = register_font(
        str(font_path.resolve()),
        quiet_run=quiet_run,
        verbose=verbose,
    )
    typer.echo(f"Registered font: {registered_font_name}")


@app.command(
    name="unregister_font",
    help="Unregister a font file from being used for captions.",
)
def unregister_font_cmd(
    font_path_or_name: Annotated[
        str,
        typer.Argument(
            ...,
            help="The path of the font file or the font's name to be unregistered.",
            show_default=False,
        ),
    ],
    quiet_run: Annotated[
        Optional[bool],
        typer.Option(
            ...,
            "--quiet-run",
            "-qr",
            help="Run the command quietly without any output or console.",
        ),
    ] = False,
    verbose: Annotated[
        Optional[bool],
        typer.Option(
            ...,
            "--verbose",
            "-v",
            help="Show verbose output.",
        ),
    ] = False,
):
    result = unregister_font(
        font_path_or_name,
        quiet_run=quiet_run,
        verbose=verbose,
    )
    if result:
        typer.echo(f"Unregistered font: {font_path_or_name}")
    else:
        typer.echo(f"Font is NOT registered: {font_path_or_name}")


@app.command(
    name="is_font_registered",
    help="Check if a font file is registered to be used for captions.",
)
def is_font_registered_cmd(
    font_path_or_name: Annotated[
        str,
        typer.Argument(
            ...,
            help="The path of the font file or the font's name to be checked.",
            show_default=False,
        ),
    ],
):
    font_name = is_font_registered(font_path_or_name)
    if font_name:
        typer.echo(f"Font is registered: {font_name}")
    else:
        typer.echo(f"Font is NOT registered: {font_path_or_name}")


@app.command(
    name="version",
    help="Show the version of Captametropolis.",
)
def version_cmd():
    typer.echo(f"Captametropolis v{__version__}")


def main():
    app()


if __name__ == "__main__":
    main()

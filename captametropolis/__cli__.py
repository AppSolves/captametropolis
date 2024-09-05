#!/usr/bin/env python3

import sys

from captametropolis import add_captions


def main():
    if len(sys.argv) < 3:
        print(f"Usage: captametropolis <video_file> <output_file>")
        sys.exit(1)

    video_file = sys.argv[1]
    output_file = sys.argv[2]

    add_captions(video_file, output_file, verbose=True)

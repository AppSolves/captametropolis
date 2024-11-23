#!/usr/bin/env python3

import os

from setuptools import find_packages, setup


def get_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(requirements_path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


def get_version():
    version_path = os.path.join(
        os.path.dirname(__file__), "captametropolis", "__version__.py"
    )
    with open(version_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    return "1.0.0"


setup(
    name="captametropolis",
    version=get_version(),
    packages=find_packages(),
    install_requires=get_requirements(),
    extras_require={
        "local": ["openai-whisper"],
    },
    package_data={
        "captametropolis": ["assets/**/*"],
    },
    include_package_data=True,
    url="https://github.com/AppSolves/captametropolis",
    license="MIT",
    author="Original: Unconventional Coding | This Fork: AppSolves",
    maintainer="AppSolves",
    maintainer_email="contact@appsolves.dev",
    author_email="unconventionalcoding@gmail.com",
    description="Add Automatic Captions to YouTube Shorts with AI",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "captametropolis=captametropolis.__cli__:main",
        ],
    },
)

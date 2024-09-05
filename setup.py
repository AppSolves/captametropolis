#!/usr/bin/env python3

from setuptools import find_packages, setup


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name="captametropolis",
    version="1.0.0",
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
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "captametropolis=captametropolis.__cli__:main",
        ],
    },
)

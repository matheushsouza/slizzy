#!/usr/bin/env python3

from setuptools import setup, find_packages


with open('README.md') as readme:
  long_description = readme.read()

setup(
  name = "slizzy",
  description = "Slizzy is a program and a library to search for tracks and download "
                "slider.kz and zippyshare.com objects.",
  long_description = long_description,
  long_description_content_type = "text/markdown",
  
  version = "1.1.9",
  
  author = "gahag",
  author_email = "gabriel.s.b@live.com",
  
  url = "https://www.github.com/gahag/slizzy",
  
  packages = find_packages("src"),
  package_dir = { "" : "src" },
  
  install_requires = [
    "beautifulsoup4",
    "colorama",
    "hsaudiotag3k",
    "fuzzywuzzy",
    "requests",
    "python-Levenshtein"
  ],
  
  entry_points = {
    "console_scripts": [
      "slizzy=slizzy:cli"
    ],
  },
  
  classifiers = [
    "License :: OSI Approved :: BSD License",
    "Environment :: Console",
    "Programming Language :: Python :: 3",
    "Topic :: Utilities"
  ]
)

# Rubicon 3
### The latest installment of your insane silicon friend.
Comes in 3 variants: Discord, in-game (Brick Rigs, Steam game), and terminal.

## Notable Changes
First off, Rubicon 3 is the first that might be open source. Given you are reading this, it likely is.

Second off, there are other notable changes such as:
- Rubicon now uses .json files for memory, instead of text files with a custom format. This is more robust and user-friendly.
- The code-base is split into a few files and directories.
- All of the desired variants (discord, ingame, terminal) are now in one singular project, one singular directory.
- The code base makes an attempt to be cleaner and more understandable.
- The code checks that your Python installation is what it was developed with.

## Environmental Variables
The following environmental keys are required:

DT: Discord token.

GK: GroqCloud API key.

## Installation
You already have Rubicon 3 installed.

What you need is Python 3.12.3 or higher, if not present already.

Find Python 3.12.5 (current Python version Rubicon is developed with) [here](https://www.python.org/downloads/release/python-3125/).

## Running
Given that you have Python, and the environment variables Rubicon needs to function, you can open a terminal/command prompt and run `python3 main.py`, or, if Python is set up properly,
`py main.py`.

Before running these two, however, make sure you have `cd`'d into the correct directory. For example, if you wish to run the discord version, `cd` into the discord directory, in the
directory this README is in.
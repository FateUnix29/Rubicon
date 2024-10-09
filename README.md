# Rubicon 4
Your friendly, nuts Discord bot, and ingame companion.


## Information
Rubicon 4.x is designed to be cleaner, faster, better in most aspects than Rubicon 3.x.<br>
It is also designed to be much more configurable, with emphasis on real-time configuration updates.<br>
Rubicon also has a vast amount of new features and tweaks, to make it the *best* rubicon.<br>

### What are these new features?
A few include:
- Changing status
- Aforementioned configuration system
- Better, cleaner functionalized code
- A network of files that work together
- More commands, with more options. Rubicon will even do your math!
- Modularity: Add a source file, interface with a brand new entire __API__ to allow Rubicon to use your custom ability!!

### Do you have any ideas for other features?
Yes, here are some that would be awesome, but ambitious and low-priority:
- Cutting out the 3rd party and allowing the model to be ran locally
- Steam accounts and support
- Rubicon self-configuration (Not too ambitious, but still questionable when Rubicon can't get function calls right)
- Outsourcing to other models

### How do I install it?
For the packages, you can use `pip install -r requirements.txt`.<br>
However, Rubicon does use external services - These will require keys and tokens.<br>

To enter your tokens, go to `tokens.json` in the root directory. Enter the names of the environment variables containing your tokens into each field.<br>
Note, however, that if you aren't using Rubicon as a Discord bot, you won't need a Discord bot token.<br>
(Note 2: Rubicon may gain support for being ran locally in the future. In that case, you do not need ANY tokens.)

# Tutorials:

## Windows:

### Rubicon Setup Guide for Discord Bot

### Requirements:

    Git Installed: Ensure you have Git installed on your system.
    Discord Bot Created: Have your Discord bot already created.
    GroqCloud API Token: Make sure you have copied your GroqCloud API token.

Step-by-Step Instructions:
1. Create a Directory for Rubicon

    Choose a location on your computer where you would like to download the Rubicon files.

2. Download Rubicon

    Open the Command Prompt:
        Press the Windows key, type cmd, and hit Enter.

    Navigate to your chosen directory by typing the following command:

    bash

cd "C:\path\to\your\directory"

(Replace C:\path\to\your\directory with the actual path you chose.)

Now, download Rubicon by running:

    git clone https://github.com/FateUnix29/Rubicon.git

    Wait for the download to complete.

3. Navigate to the Discord Directory

    Once the download is finished, change to the Discord directory with:

    cd Rubicon\discord

4. Install Required Dependencies

    Install the necessary Python packages by typing:

    pip install -r requirements.txt

5. Set Up Environment Variables

    Open Edit the System Environment Variables:
        Press the Windows key, type Environment Variables, and select Edit the system environment variables.

    In the System Properties window, click on the Environment Variables button.

    Under System Variables, click New and enter the following:
        Variable name: DT
        Variable value: (Your Discord bot token)
        Click OK.

    Add another variable by clicking New again and entering:
        Variable name: GK
        Variable value: (Your GroqCloud token)
        Click OK.

6. Final Steps

    Ensure all variables are set correctly and close the Environment Variables window.
    You are now ready to run your Rubicon setup with your Discord bot!

### Is there a community?
Yes! Join the [Discord](https://discord.gg/AnxGWymKbA) for information on Rubicon and all of my other projects.

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
For the packages, you can use `pip install -r requirements.txt` in any of the directories, such as `discord`.<br>
However, Rubicon does use external services - These will require keys and tokens.<br><br>

To enter your tokens, go to `keynames.json` in the root directory. Enter the names of the environment variables containing your tokens into each field.<br>
Note, however, that if you aren't using Rubicon as a Discord bot, you won't need a Discord bot token.<br>
(Note 2: Rubicon may gain support for being ran locally in the future. In that case, you do not need ANY tokens.)<br><br>

This shouldn't have to be stated, but this is a Python project. It was developed with love and Python 3.12.6.<br>
If you don't have Python, install Python 3.12.6, then do the aforementioned steps.

### Windows Requirements & Setup:

- Git Installed: Ensure you have Git installed on your system.
- Discord Bot Created: Have your Discord bot already created, and its bot token on hand.
- GroqCloud API Token: Make sure you have copied your GroqCloud API token.

Step-by-Step Instructions:
1. Create a Directory for Rubicon<br>
    Choose a location on your computer where you would like to download the Rubicon files.<br>
    If you do not, then the later `git clone` steps will create it for you.<br>

2. Download Rubicon<br>
    Open the Command Prompt:<br>
        Press the Windows key, type cmd, and hit Enter.

    Navigate to your chosen directory by typing the following command:
    ```bash
    cd "C:\path\to\your\directory"
    ```
    (Replace C:\path\to\your\directory with the actual path you chose.)<br><br>

    Now, download Rubicon by running `git clone https://github.com/FateUnix29/Rubicon.git`, and wait for the download to complete.<br>
    Rubicon is relatively light-weight, so it'll probably take a few seconds.<br>
    It's worth noting that, if you plan to modify Rubicon for your own purposes, it __may__ be wise to fork the GitHub repository and copy your fork instead. This requires a GitHub account.<br>
    To do that, go to `https://github.com/FateUnix29/Rubicon`, look for and click on the 'Fork' button in the top-right corner, press 'Create fork', and then run this command instead:<br>
    `git clone https://github.com/(YOUR USERNAME)/Rubicon.git`<br>
    Replace '(YOUR USERNAME)' with your GitHub username, and Rubicon.git with (your fork's name).git if you named it differently.<br>
    Creating a fork like this allows you to contribute your changes later, if you so choose. It also ensures you can keep track of your *own* Rubicon versions with version control.<br><br>

3. Navigate to the Discord Directory<br>
    Once the download is finished, change to the Discord directory with `cd Rubicon/discord`.<br>

4. Dependencies:<br>
    If you haven't already, check back to the "How do I install it?" section, which covers how to install the external libraries.<br>
    Now that you're in the discord directory, just run `pip install -r requirements.txt`, as that prior section states.<br><br>

5. Set Up Environment Variables<br>
    This section is a more flushed out version of the instructions in the "How do I install it?" section.<br>
    If you're a more advanced user, go there instead, save some time.<br><br>
    Open Edit the System Environment Variables:<br>
        Press the Windows key, type Environment Variables, and select Edit the system environment variables.<br><br>

    In the System Properties window, click on the Environment Variables button.<br>
    Under System Variables, click New and enter the following:<br>
        Variable name: DT<br>
        Variable value: (Your Discord bot token)<br>
        Click OK.<br><br>

    Add another variable by clicking New again and entering:<br>
        Variable name: GK<br>
        Variable value: (Your GroqCloud token)<br>
        Click OK.<br><br>

    It's worth noting that you certainly are not limited to these variable names. Check `keynames.json` and update it to your desired names, if needed.<br><br>

6. Final Steps<br>
    Ensure all variables are set correctly and close the Environment Variables window.<br>
    You are now ready to run your Rubicon setup with your Discord bot!<br><br>

### Linux Requirements & Setup:

- Git Installed: Most Linux users should already have Git installed. But just incase, check if you have it.
- Discord Bot Created: Have your Discord bot already created, and its bot token on hand.
- GroqCloud API Token: Make sure you have copied your GroqCloud API token.

Step-by-Step Instructions:
1. Create a Directory for Rubicon<br>
    This can be entirely skipped if you so choose, but if you want to create a directory beforehand, run `mkdir (your directory name)`.<br>

2. Download Rubicon<br>
    Open your favorite terminal emulator.<br>
    Navigate to your chosen directory, and run: `git clone https://github.com/FateUnix29/Rubicon.git`.<br>
    Rubicon is relatively light-weight, so it'll probably take a few seconds.<br><br>
    It's worth noting that, if you plan to modify Rubicon for your own purposes, it __may__ be wise to fork the GitHub repository and copy your fork instead. This requires a GitHub account.<br>
    To do that, go to `https://github.com/FateUnix29/Rubicon`, look for and click on the 'Fork' button in the top-right corner, press 'Create fork', and then run this command instead:<br>
    `git clone https://github.com/(YOUR USERNAME)/Rubicon.git`<br>
    Replace '(YOUR USERNAME)' with your GitHub username, and Rubicon.git with (your fork's name).git if you named it differently.<br>
    Creating a fork like this allows you to contribute your changes later, if you so choose. It also ensures you can keep track of your *own* Rubicon versions with version control.<br><br>

3. Navigate to the Discord Directory<br>
    Once the download is finished, change to the Discord directory with `cd Rubicon/discord`.<br>

4. Dependencies:<br>
    If you haven't already, check back to the "How do I install it?" section, which covers how to install the external libraries.<br>
    Now that you're in the discord directory, just run `pip install -r requirements.txt`, as that prior section states.<br>

5. Set Up Environment Variables<br>
    This section is a more flushed out version of the instructions in the "How do I install it?" section.<br>
    HOWEVER, the instructions are slightly different on Linux, so please don't skip this step.<br><br>
    
    Assuming you're using bash, open `~/.bashrc` in your favorite editor, or your shell's equivelent configuration file.<br>
    Add the following to the end of the file:<br>
    ```bash
    export DT=(Your Discord bot token)
    export GK=(Your GroqCloud token)
    ```
    <br>
    If you chose a different name for DT and GK in `keynames.json`, replace DT & GK with your desired names.<br>
    Replace '(Your Discord bot token)' with your Discord bot token, and '(Your GroqCloud token)' with your GroqCloud token.<br><br>
    Save and close the file.<br>
    
6. Final Steps<br>
    Ensure all variables are set correctly and close the Environment Variables window.<br>
    You are now ready to run your Rubicon setup with your Discord bot!<br><br>

### Is there a community?
Yes! Join the [Discord](https://discord.gg/AnxGWymKbA) for information on Rubicon and all of my other projects.

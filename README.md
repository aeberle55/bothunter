# Bothunter
CLI tool to locate bots on the Roosterteeth Forum


## Install
Requires Python 2.7 and BeautifulSoup 4. Python should come pre-installed on
linux systems. To get BeautifulSoup, first install pip, then the package:

Debian:
    sudo apt-get install python-pip
    sudo pip install beautifulsoup4

Red Hat:
    sudo yum install python-pip
    sudo pip install beautifulsoup4

Windows:

I don't actually have experience in windows. However, there are quite a few
resources online. If you'd like to document the process, please let me know.


## Usage
Bothunter is a command line utility that scrapes a given RT forum for spambots
by looking for unusual Unicode in their titles. It then provides a list of
probable spammers and posts for the user to browse. It can provide this
information in multiple formats, including direct print to screen, writing to
a file, and an interactive session.

### Interactive Mode
If specified by the `-I` or `--interactive` flag, the system will drop into an
interactive shell to display the information. The `p` option will print the
bot's username, a link to their account, and the title of their forum post to
the terminal. `o` opens a new tab in your browser to the bot's userpage. When
finished viewing a bot, use the `n` command to move on to the next bot in the
queue. The `p`, `o`, and `n` commands can all be followed by a number to
perform the same action on multiple bots at a time. `r` shows the nmber of
unprocessed bots in the queue. The `q` command will exit the prompt.

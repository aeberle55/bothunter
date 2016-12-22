#! /usr/bin/python
from botlib import RTForum

import argparse
import sys
import os


parser = argparse.ArgumentParser(description='Locate Spambots in RT Forums')

parser.add_argument('-f', '--forum', default='rwby',
                    help='Forum to search for spam. Default rwby')
parser.add_argument('-I', '--interactive', action='store_true',
                    help='Enter interactive shell to process bots')
parser.add_argument('-o', '--output', default=None, help='Outupt file location')
parser.add_argument('-m', '--max', default=1, type=int,
                    help='Max number of pages to check')
parser.add_argument('-q', '--quiet', action='store_true',
                    help='Do not print data to screen')


class Interactive(object):
    """
        Interactive shell for viewing bots

        Attributes:
            actions (`dict`): Mapping of inputs to their functions
            spambots (`SpamBots`): Potential spambots being examined
            name_list (`list`): List of yet to be checked bot usernames
    """
    USAGE = """Interactive Options:
    o (#) - Open Bot in webbrowser
    p (#) - Print bot summary
    n (#) - Next bot
    r     - Print the number of bots remaining
    h     - Print this help
    q     - Quit interactive mode
    (#)   - Perform the given action for the specified number of bots\n"""

    def open_tab(self, num):
        """
            Opens browser tabs to spambot accounts

            Args:
                num (`int`): Number of spambots to perform the action on
        """
        names = self.name_list[:num]
        for bot in names:
            self.spambots[bot].open_tab()

    def print_summary(self, num):
        """
            Prints a summary of spambot accounts

            Args:
                num (`int`): Number of spambots to perform the action on
        """
        names = self.name_list[:num]
        for bot in names:
            print(self.spambots[bot].summary())

    def next_bot(self, num):
        """
            Advances to the next bot in the queue

            Args:
                num (`int`): Number of spambots to perform the action on
        """
        self.name_list = self.name_list[num:]

    def help_print(self):
        """ Print the usage  """
        print(self.USAGE)

    def remaining(self):
        """ Print the number of accounts still to be parsed """
        print(len(self.name_list))

    def get_input(self):
        """
            Parse user input to decide the next action

            Returns:
                `function`: The action to perform
                `list`: List of arguments to pass the function
        """
        inp = ""
        # Ignore empty lines
        while not inp:
            inp = raw_input('> ').strip().split()
        if len(inp) not in [1, 2] or inp[0] not in self.actions.keys():
            print("Invalid input")
            return self.actions['h'], []
        if inp[0] in ['h', 'q', 'r']:
            args = []
        elif len(inp) == 1:
            args = [1]
        else:
            try:
                args = [int(inp[1])]
            except ValueError:
                print("Invalid input")
                return self.actions['h'], []
        return self.actions[inp[0]], args

    def __init__(self, spambots):
        """
            Args:
                spambots (`SpamBots`): Spambots to examine in shell
        """
        self.spambots = spambots
        self.name_list = spambots.keys()
        self.actions = {
            'o': self.open_tab,
            'p': self.print_summary,
            'n': self.next_bot,
            'r': self.remaining,
            'h': self.help_print,
            'q': None,
        }

    def loop(self):
        """ Iterate in the shell until finished """
        self.help_print()
        while True:
            action, arg = self.get_input()
            if action is None:
                break
            action(*arg)


def write_to_file(data, fpath):
    """
        Write data to a file

        Args:
            data (`str`): Data to write to file
            fpath (`str`): Valid filepath to write data to
    """
    dirname = os.path.dirname(fpath)
    if (dirname and not os.path.isdir(dirname)) or os.path.isdir(fpath):
        print("Invalid file path. Cannot write data")
        sys.exit(-1)
    with open(fpath, 'w') as f:
        f.write(data)


def main():
    args = parser.parse_args()
    forum = RTForum(args.forum, args.max, args.quiet)
    s = forum.summary()
    if not args.quiet and not args.interactive:
        print(s)
    if args.output:
        write_to_file(s, args.output)
    if args.interactive:
        Interactive(forum.spambots).loop()
    return 0

if __name__ == '__main__':
    sys.exit(main())

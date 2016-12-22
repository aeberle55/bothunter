from bs4 import BeautifulSoup

import webbrowser
import urllib2
import math
import re


class SpamBots(object):
    """
        Class to represent a collection of spambots

        Attributes:
            spammers (`dict`): Username strings associated with
                `SpamProfile` objects
    """

    def __init__(self, threads):
        """
            Args:
                threads (`list`) A list of `ForumThread` objects
        """
        self.spammers = {}
        spam_threads = [thread for thread in threads if thread.is_spam()]
        for thread in spam_threads:
            self.add_thread(thread)

    def add_thread(self, thread):
        """
            Add a spambot thread to the collection

            Args:
                thread (`ForumThread`): Thread created by a spammer
        """
        uname = thread.uname
        if not self.spammers.get(uname):
            self.spammers[uname] = SpamProfile(uname)
        self.spammers[uname].add_thread(thread)

    def summary(self):
        """
            Generate a summary of all spammers in the collection

            Returns:
                A formated string of spammers
        """
        out = ''
        for spammer in self.spammers.values():
            out += spammer.summary()

        return out

    def keys(self):
        """
            Get the usernames of spammers in the collection

            Returns:
                `list`: List of usernames in string form
        """
        return self.spammers.keys()

    def __getitem__(self, key):
        return self.spammers[key]


class SpamProfile(object):
    """
        Object representing a potential spammer and their posts

        Attributes:
            threads (`list`): List of `ForumThread` objects created
                by the spammer
            uname (`str`): Username of the spammer
            url (`str`): URL of the user's account
    """
    USER_BASE = "http://roosterteeth.com/user/"
    SUMMARY_FMT = "{0} - {1}\n{2}\n\n"

    def __init__(self, uname):
        """
            Args:
                uname (`str`): Username of the user
        """
        self.threads = []
        self.uname = uname

    def add_thread(self, thread):
        """
            Associate a thread with a user

            Args:
                thread (`ForumThread`): Thread to associate
        """
        self.threads.append(thread)

    def open_tab(self):
        """
            Opens user's page on Roosterteeth
        """
        webbrowser.open_new_tab(self.url)

    def summary(self):
        """
            Format's username, account, and posts in a string

            Returns:
                `str`: User information in string format
        """
        return self.SUMMARY_FMT.format(self.uname, self.url, self.thread_list())

    def thread_list(self):
        """
            Formats the titles of a user's threads

            Returns:
                `str`: Formated titles of threads
        """
        out = ""
        prefix = ""
        for thread in self.threads:
            out += prefix + str(thread)
            prefix = "\n"
        return out

    @property
    def url(self):
        """ URL of a user's account """
        return self.USER_BASE + self.uname

    def __str__(self):
        return self.uname + ' - ' + self.url


class ForumThread(object):
    """
        Object representing a single forum thread

        Attributes:
            url (`str`): Link to the forum thread
            title (`str`): Title of the forum thread
            uname (`str`): Username of the thread creator
    """

    SPAM_START = unichr(0xb000)
    SPAM_END = unichr(0xdfff)

    def __init__(self, url, title, uname):
        """
            Args:
                url (`str`): URL of the thread
                title (`str`): Title of the thread
                uname (`str`): Username of the thread creator
        """
        self.url = url
        self.title = title
        self.uname = uname

    def is_spam(self):
        """
            Determines if the thread is spam based on its title
            characters being in the unicode range 0xb000 to 0xdfff

            Returns:
                `bool`: True if at least one character is in the
                    unicode range of 0xb000 to 0xdfff; False otherwise
        """
        for c in self.title:
            if self.SPAM_START <= c <= self.SPAM_END:
                return True
        return False

    def __str__(self):
        return "    " + self.title.encode('utf-8')


class RTForum(object):
    """
        Scrapes and contains data on a forum on the RT website

        Attributes:
            forum (`str`): Link to the forum
            num_pages (`int`): Number of pages in the forum
            pages (`list`): List of `RTForumPage` objects in the forum
            threads (`list`): List of `ForumThread` objects in the forum
            spambots (`SpamBots`): Suspected bots found in the forum
    """
    FORUM_BASE = "http://roosterteeth.com/forum/{0}?page="
    TOPICS_RX = re.compile("^<h3>All Topics \((\d+) Topics\)<\/h3>$")
    TOPICS_PER_PAGE = 30

    def __init__(self, forum, maximum=None, quiet=False):
        """
            Args:
                forum (`str`): Name of the forum to scrape

            Kwargs:
                maximum (`int`): Maximum number of pages to scrape
                quiet (`bool`): If True, do not print status
        """
        self.forum = self.FORUM_BASE.format(forum)
        if maximum is None:
            self.get_num_pages()
        else:
            self.num_pages = maximum
        self.pages = []
        self.threads = []
        for i in range(1, self.num_pages + 1):
            if not quiet:
                print("Getting page %d of %d" % (i, self.num_pages))
            page = RTForumPage(i, self.forum)
            self.pages.append(page)
            self.threads += page.threads
        self.spambots = SpamBots(self.threads)

    def get_num_pages(self):
        """
            Determines the number of pages of content in the forum
        """
        pg = RTForumPage(1, self.forum)
        for l in pg.page.split('\n'):
            m = self.TOPICS_RX.match(l)
            if m:
                break
        if not m:
            print("Number of pages not found")
            self.num_pages = 0
            return
        self.num_pages = int(math.ceil(float(m.group(1)) /
                             self.TOPICS_PER_PAGE))

    def summary(self):
        """
            Creates a summary of spambot activity in the forum

            Returns:
                `str`: Formated summary of spam activity
        """
        return self.spambots.summary()


class RTForumPage(object):
    """
        Scrapes and represents one page on the RT Forum

        Attributes:
            page_num (`int`): Page number of this object
            base (`str`): Base URL of the forum
            page (`str`): Raw HTML of the forum page
            threads (`list`): List of `ForumThread` objects on the page
    """

    def __init__(self, num, base):
        """
            Args:
                page_num (`int`): Page number of this object
                base (`str`): Base URL of the forum
        """
        self.page_num = num
        self.base = base
        self.get_page()
        self.get_threads()

    def get_page(self):
        """ Get the raw HTML of a page from the internet """
        url = self.base + str(self.page_num)
        req = urllib2.Request(url, headers={'User-Agent': "Magic Browser"})
        response = urllib2.urlopen(req)
        self.page = response.read()

    def get_threads(self):
        """ Parse the raw HTML of a thread into data """
        soup = BeautifulSoup(self.page, 'html.parser')
        section = soup.find_all("ul", class_="all-topics")[0]
        elems = section.find_all("li")
        self.threads = []
        for elem in elems:
            url = elem.a['href']
            uname = elem.div.p.a.contents[0]
            title = elem.a.contents[0].strip()
            self.threads.append(ForumThread(url, title, uname))

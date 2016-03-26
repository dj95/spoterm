#!/usr/bin/env python3.5
#
# spoterm
#
# (c) 2016 Daniel Jankowski
# All Rights Reserved.

import os
import re
import urwid
import mainframe

from threading import Thread


CONFIG_FILE = '~/.spoterm/config'

palette = [
        ('normal', 'dark green', 'black'),
        ('error', 'light red', 'black'),
        ('warning', 'yellow', 'black'),
        ('logo', 'dark green', 'black'),
        ('status', 'dark gray', 'black'),
        ('sent', 'black', 'dark green'),
        ('incoming','black','light gray'),
        ]


# get username and password from config
def parse_config():
    username, password, keyfile = None, None, None
    with open(os.path.expanduser(CONFIG_FILE), 'r') as fp:
        for line in fp.readlines():
            if line.startswith('username'):
                username = re.sub(r'^(.*)\s=\s(.*)\n$', r'\2', line)
            if line.startswith('password'):
                password = re.sub(r'^(.*)\s=\s(.*)\n$', r'\2', line)
            if line.startswith('appkey'):
                keyfile = re.sub(r'^(.*)\s=\s(.*)\n$', r'\2', line)
    return username, password, keyfile


# start gui and initiate spotify connection
def start_gui(username, password, keyfile):
    main_layout = mainframe.MainLayout('spoterm', username, password, keyfile)
    loop = urwid.MainLoop(main_layout, palette, screen=urwid.raw_display.Screen())
    refresh = Thread(target=mainframe.refresh_screen, args=(loop,))
    refresh.start()
    loop.run()


def main():
    username, password, keyfile = parse_config()
    start_gui(username, password, keyfile)
    pass


if __name__ == '__main__':
    main()

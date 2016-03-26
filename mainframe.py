#!/usr/bin/env python3.5
#
# spoterm
#
# (c) 2016 Daniel Jankowski
# All Rights Reserved.


import time
import urwid
import spotify
import threading

import utils
import playbackthread

RUN = True


class MainLayout(urwid.Frame):

    def __init__(self, name, username=None, password=None, keyfile=None):
        # initialize ui
        self.__walker = urwid.SimpleListWalker([])
        self.__list = urwid.ListBox(self.__walker)
        self.__input = urwid.Edit(caption="$ ")
        self.__playing = urwid.Edit(caption="", align='center')

        list_cont = urwid.LineBox(self.__list, title=name)
        inp_cont = urwid.LineBox(self.__input)
        play_cont = urwid.LineBox(self.__playing)

        super().__init__(list_cont, play_cont, footer=inp_cont, focus_part='footer')

        # modes
        self.__command_mode = False
        self.__search_mode = False

        # print spotify logo
        self.__walker.append(urwid.Text(('logo', ' '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '          ###########                                               '), urwid.CENTER)) 
        self.__walker.append(urwid.Text(('logo', '       #################                                            '), urwid.CENTER)) 
        self.__walker.append(urwid.Text(('logo', '     #####################                                          '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '   ######/^^^^^^^^^^^\######                                        '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '  #####/ ............. \#####                      _   _  __        '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', ' #####/ /#############\ \#####     ___ _ __   ___ | |_(_)/ _|_   _  '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', ' #########/^^^^^^^^^\#########    / __| \'_ \ / _ \| __| | |_| | | | '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', ' #######/ ........... \#######    \__ \ |_) | (_) | |_| |  _| |_| | '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', ' ######/ /###########\ \######    |___/ .__/ \___/ \__|_|_|  \__, | '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '  #########/^^^^^^^\#########         |_|                    |___/  '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '   ######/ ......... \######                                        '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '     ###/ /#########\ \###                                          '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '       #################                                            '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', '          ###########                                               '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', ' '), urwid.CENTER))
        self.__walker.append(urwid.Text(('logo', ' '), urwid.CENTER))
        self.__list.set_focus(len(self.__walker) - 1)

        # attributes
        self.__session = None
        self.__logged_in_event = None
        self.__artists_last_search = None
        self.__tracks_last_search = None
        self.__audio = None
        self.__playlists = None
        self.__albums = None
        self.__selected_album = None
        self.__selected_playlist = None
        self.__selected_artist = None
        self.__play = False

        # log in, if config exists
        if username != None and password != None and keyfile != None:
            self.__session, self.__logged_in_event, self.__audio = utils.start_session(username, password, keyfile)
            self.__logged_in_event.wait()
            self.__walker.append(urwid.Text(('normal', 'Successfully logged in'), urwid.CENTER))
            self.__list.set_focus(len(self.__walker) - 1)
            self.__draw_divider()
            self.__session.process_events()
       
        # start playback thread
        self.__playback_thread = playbackthread.playback_thread(self, self.__playing)
        self.__playback_thread.start()
        
        # event listener that calls the next song, when recent song finished
        self.__session.on(spotify.SessionEvent.END_OF_TRACK, self.next_track)

    # stop playback thread and exit gui mainloop
    def __shutdown(self):
        self.__playback_thread.stop_event.set()
        global RUN
        RUN = False
        raise urwid.ExitMainLoop()

    # parse input in command mode(':')
    def __parse_command(self):
        inp = self.__input.get_edit_text()
        
        if inp.lower() == 'q' or inp.lower() == 'quit': # exit spoterm
            self.__shutdown()
            return
        elif inp.startswith('login'): # log in, if no config is provided
            if not self.__session and not self.__logged_in_event.is_set():
                args = inp.split(' ')
                self.__session, self.__logged_in_event, self.__audio = utils.start_session(args[1], args[2])
                self.__logged_in_event.wait()
                self.__walker.append(urwid.Text(('normal', 'Successfully logged in'), urwid.CENTER))
                self.__list.set_focus(len(self.__walker) - 1)
                self.__draw_divider()
                self.__session.process_events()
            return
        elif inp.startswith('play') or inp.startswith('p '):
            args = inp.split(' ')
            if len(args) == 2:
                if args[1].startswith('a'): # play album
                    
                    return
                elif args[1].startswith('t'): # play track
                    self.__playback_thread.set_tracklist(self.__tracks) # use playback thread for advanced tracklist handling
                    self.__playback_thread.set_tracknumber(int(args[1][1:]) - 1)
                    self.__playback_thread.set_next()
                    self.__play = True
                    self.__playing.set_caption('|> ')
                    return
        elif inp.startswith('select') or inp.startswith('s '): # select shown playlist or artist
            args = inp.split(' ')
            if len(args) == 2:
                if args[1].startswith('p'): #  select playlist
                    self.__selected_playlist = self.__playlists[int(args[1][1:]) - 1]
                    self.__walker.append(urwid.Text(('normal', 'selected playlist: ' + self.__selected_playlist.name + '\n'), urwid.LEFT))
                    self.__list.set_focus(len(self.__walker) - 1)
                    self.__tracks = self.__selected_playlist.tracks
                    for i in range(len(self.__selected_playlist.tracks)):
                        self.__walker.append(urwid.Text(('normal', str(i + 1) + ') '+ str(self.__selected_playlist.tracks[i].name)), urwid.LEFT))
                        self.__list.set_focus(len(self.__walker) - 1)
                    self.__draw_divider()
                    return
                if args[1].startswith('al'): # select album
                    self.__selected_album = self.__albums[int(args[1][2:]) - 1]
                    browser = self.__selected_album.browse()
                    browser.load()
                    track_names = []
                    for i in range(len(browser.tracks)):
                        track_names.append(browser.tracks[i].name)
                    self.__draw_results('tracks', track_names)
                    self.__draw_divider
                    self.__tracks = browser.tracks
                    return
                if args[1].startswith('a'): # select artist
                    self.__selected_artist = self.__artists[int(args[1][1:]) - 1]
                    browser = self.__selected_artist.browse()
                    browser.load()
                    self.__albums = browser.albums
                    album_names = []
                    for i in range(len(browser.albums)):
                        album_names.append(browser.albums[i].name)
                    self.__draw_results('albums', album_names)
                    self.__draw_divider()
                    return
        elif inp.lower() == 'playlists' or inp.lower() == 'pl': # show all personal playlists
            if len(self.__session.playlist_container) > 0:
                playlists = [p.name for p in self.__session.playlist_container]
                self.__playlists = self.__session.playlist_container
                self.__draw_results('playlists', playlists)
                self.__draw_divider()
            
        # no valid input    
        self.__input.set_caption('$ ')
        self.__input.set_edit_text('Wrong command')

    # parse input in search mode ('/')
    def __parse_search(self):
        if self.__logged_in_event.is_set():
            # initiate search
            inp = self.__input.get_edit_text()
            search = self.__session.search(inp)
            search.load()

            # get names of results
            artists = [a.load().name for a in search.artists[:3]]
            tracks = [t.load().name for t in search.tracks[:3]]

            # draw results
            self.__walker.append(urwid.Text(('normal', 'search for: ' + inp), urwid.LEFT))
            self.__list.set_focus(len(self.__walker) - 1)
            self.__draw_results('\nartists', artists)
            self.__draw_results('\ntracks', tracks)
            self.__artists = search.artists
            self.__tracks = search.tracks
            self.__draw_divider()
            return
        
        self.__input.set_caption('$ ')
        self.__input.set_edit_text('Please log in to search')

    # draw search results
    def __draw_results(self, title, results):
        self.__walker.append(urwid.Text(('normal', title + '\n'), urwid.LEFT))
        self.__list.set_focus(len(self.__walker) - 1)
        for i in range(len(results)):
            self.__walker.append(urwid.Text(('normal', str(i + 1) + ') '+ results[i]), urwid.LEFT))
            self.__list.set_focus(len(self.__walker) - 1)

    def __draw_divider(self):
        self.__walker.append(urwid.Divider('\u2500'))
        self.__list.set_focus(len(self.__walker) - 1)

    def next_track(self, error_type):
        self.__playback_thread.next_track()

    def get_player(self):
        return self.__session.player

    def keypress(self, size, key):
        if key == 'enter': # parse input
            if self.__command_mode: # parse command input
                self.__parse_command()
                self.__command_mode = False
                self.__input.set_caption('$ ')
                self.__input.set_edit_text('')
            elif self.__search_mode:
                self.__parse_search() # parse search input
                self.__search_mode = False
                self.__input.set_caption('$ ')
                self.__input.set_edit_text('')
            return
        elif key == ':': # command mode
            self.__command_mode = True
            self.__input.set_caption(':')
            self.__input.set_edit_text('')
            return
        elif key == '/': # search mode
            self.__search_mode = True
            self.__input.set_caption('/')
            self.__input.set_edit_text('')
            return
        elif key == 'esc': # abort
            if self.__command_mode:
                self.__input.set_caption('$ ')
                self.__input.set_edit_text('')
                self.command_mode = False
            elif self.__search_mode:
                self.__input.set_caption('$ ')
                self.__input.set_edit_text('')
                self.search_mode = False
            return
        elif key == 'p' and not self.__command_mode and not self.__search_mode: # toggle play/pause
            if not self.__play: # start playback
                self.__session.player.play()
                self.__input.set_caption('$ ')
                self.__input.set_edit_text('')
                self.__playing.set_caption('|> ')
                self.__play = True
            else: # pause playback
                self.__session.player.pause()
                self.__input.set_caption('$ ')
                self.__input.set_edit_text('')
                self.__playing.set_caption('|| ')
                self.__play = False
            return
        elif key == 's' and not self.__command_mode and not self.__search_mode: # stop track
            self.__session.player.stop()
            self.__input.set_caption('$ ')
            self.__input.set_edit_text('')
            return
        elif key == 'h' and self.__play and not self.__command_mode and not self.__search_mode: # previous track
            self.__playback_thread.previous_track()
            self.__input.set_caption('$ ')
            self.__input.set_edit_text('')
            return
        elif key == 'l' and self.__play and not self.__command_mode and not self.__search_mode: # next track
            self.__playback_thread.next_track()
            self.__input.set_caption('$ ')
            self.__input.set_edit_text('')
            return
        if not self.__command_mode and not self.__search_mode:
            self.__input.set_edit_text('')

        return super().keypress(size, key)


def refresh_screen(mainloop):
    time.sleep(1)
    while RUN:
        mainloop.draw_screen()
        time.sleep(1)

#!/usr/bin/env python3.5
#
# spoterm
#
# (c) 2016 Daniel Jankowski
# All Rights Reserved.

import time
import spotify

from threading import Thread, Event


class playback_thread(Thread):

    def __init__(self, callback, trackwindow):
        super().__init__()
        self.stop_event = Event()
        self.callack = callback
        self.__tracklist = None
        self.__tracknumber = 0
        self.__player = callback.get_player()
        self.__track_window = trackwindow
        self.__next = False

    def get_tracknumber(self):
        return self.__tracknumber

    def set_tracknumber(self, tracknumber):
        self.__tracknumber = tracknumber

    def set_tracklist(self, tracklist):
        self.__tracklist = tracklist

    def set_next(self):
        self.__next = True
    
    # initiates the threadloop to play the previous track
    def previous_track(self):
        if self.__tracklist:
            if len(self.__tracklist) > 0:
                self.__tracknumber = (self.__tracknumber - 1) % len(self.__tracklist)
                self.__next = True

    # initiates the threadloop to play the next track
    def next_track(self):
        if self.__tracklist:
            if len(self.__tracklist) > 0:
                self.__tracknumber = (self.__tracknumber + 1) % len(self.__tracklist)
                self.__next = True

    def run(self):
        self.__tracknumber = 0
        while not self.stop_event.is_set():
            # load and play next track
            if (self.__player.state == spotify.player.PlayerState.UNLOADED or self.__next) and self.__tracklist:
                self.__next = False
                track = self.__tracklist[self.__tracknumber]
                track.load()
                self.__player.load(track)
                self.__player.play()
                self.__track_window.set_edit_text(str(track.artists[0].name) + ' - ' + str(track.name))
            time.sleep(1.0)

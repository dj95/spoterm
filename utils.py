#!/usr/bin/env python3.5
#
# spoterm
#
# (c) 2016 Daniel Jankowski
# All Rights Reserved.

import os
import spotify
import threading

logged_in_event = threading.Event() 


def connection_state_listener(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in_event.set()


# start spotify session and log in
def start_session(username, password, keyfile):
    config = spotify.Config()
    config.load_application_key_file(os.path.expanduser(keyfile))
    config.user_agent = 'spoterm'
    config.tracefile = b'/tmp/libspotify-trace.log'
    session = spotify.Session(config)
    
    loop = spotify.EventLoop(session)
    loop.start()

    audio = spotify.AlsaSink(session)

    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, connection_state_listener)

    session.login(username, password)
    return session, logged_in_event, audio

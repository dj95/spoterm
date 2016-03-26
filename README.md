# spoterm

A simple tui for spotify.

------------------------

### Requirements

- Python 3
- libspotify
- pyspotify
- pyalsaaudio
- urwid

------------------------

### Installation

- Clone this repository.
- Copy the config file to `~/.spoterm/config` and fill in your credentials.
- Copy your spotify-appkey into `~/.spoterm/` and edit the config-file, so the correct path is given
- Make the `client.py` executable and run it

------------------------

### Usage

- Command-Mode, when you press `:`
  - `:pl` or `:playlists` list all your playlists
  - `:s [number]` or `:select [number]` loads the playlist, you select with the number
  - `:p t[number]` or `:play t[number]` plays the track of your selected playlist or search
- Search-Mode, when you press `/`
  - Just type in a title or artist name and watch the results
- `h` plays the previous track
- `l` plays the next track
- `p` toggles play/pause
- `s` stops the playback
- Press escape to exit command- or search-mode

------------------------

### Todo

- offline playlist support
- better player
- volume control
- improve ui
- move spotify-appkey location
- find suitable license
- error handling(!!!)

------------------------

### License

All Rights Reserved.

Unauthorized copying of this project, via any medium is strictly prohibited

Proprietary and confidential.

© 2016 Daniel Jankowski


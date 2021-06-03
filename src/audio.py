"""Play wav or mp3 files.

Python do not have support for media playing in the standard library. 
pythonsound(https://github.com/TaylorSMarks/playsound) is a package that
provides such functionality on three desktop systems, but it has some external
dependencies for OS X (Appkit, ObjectC) and Linux (gstreamer).

In this module, we will use the existing external command line players of OS X and Linux
to avoid the dependency of above libraries.

This file is basically a modified copy of playsound.py.
"""
import subprocess
import os.path
from time import sleep

class PlaysoundException(Exception):
    pass

def _playsoundWin(sound, block = True):
    '''
    Utilizes windll.winmm. Tested and known to work with MP3 and WAVE on
    Windows 7 with Python 2.7. Probably works with more file formats.
    Probably works on Windows XP thru Windows 10. Probably works with all
    versions of Python.
    Inspired by (but not copied from) Michael Gundlach <gundlach@gmail.com>'s mp3play:
    https://github.com/michaelgundlach/mp3play
    I never would have tried using windll.winmm without seeing his code.
    '''
    from ctypes import c_buffer, windll
    from random import random
    from time   import sleep
    from sys    import getfilesystemencoding

    def winCommand(*command):
        buf = c_buffer(255)
        command = ' '.join(command).encode(getfilesystemencoding())
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = ('\n    Error ' + str(errorCode) + ' for command:'
                                '\n        ' + command.decode() +
                                '\n    ' + errorBuffer.value.decode())
            raise PlaysoundException(exceptionMessage)
        return buf.value

    alias = 'playsound_' + str(random())
    winCommand('open "' + sound + '" alias', alias)
    winCommand('set', alias, 'time format milliseconds')
    durationInMS = winCommand('status', alias, 'length')
    winCommand('play', alias, 'from 0 to', durationInMS.decode())

    if block:
        sleep(float(durationInMS) / 1000.0)

def play_with_external_command(command, sound, block = True):
    '''
    Using the given `command` to play the `sound` file.
    '''
    args = command + [os.path.abspath(sound)]

    if block:
        subprocess.call(args)
    else:
        p = subprocess.Popen(args)

def _playsoundOSX(sound, block=False):
    play_with_external_command('/usr/bin/afplay', sound, block)
    
def _playsoundNix(sound, block=True):
    """Play a sound using any available player.
    """
    # Linux don't have a built in player, so we need to try some popular ones.notification_frame
    players = [
        ['mplayer', '-really-quiet', '-nolirc'],
        ['ffplay', '-nodisp', '-autoexit'],
        ['cvlc']
    ]
    mp3_only = [
        ['mpg321', '-q'],
        ['mpg123', '-q'],
    ]
    wav_only = [
        ['aplay']
    ]
    _, ext = os.path.splitext(sound)
    ext = ext.lower()
    if ext == 'mp3':
        player_opts = players + mp3_only
    elif ext == 'wav':
        player_opts = players + wav_only
    else:
        player_opts = players
    player = None
    for p in player_opts:
        if os.path.exists(f'/usr/bin/{p[0]}'):
            player = p
            break
    if player is None:
        print("Can't find supported player.")
        return
    play_with_external_command(player, sound, block)
    
from platform import system
system = system()

if system == 'Windows':
    playsound = _playsoundWin
elif system == 'Darwin':
    playsound = _playsoundOSX
else:
    playsound = _playsoundNix

del system
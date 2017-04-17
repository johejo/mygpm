#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division, absolute_import, unicode_literals
from builtins import *  # noqa

from getpass import getpass

from gmusicapi import Mobileclient

import subprocess

import urllib3

import vlc

import json

import time

# JSON attribute
class D(dict):
    __getattr__ = dict.__getitem__


#get API
def ask_for_credentials():

    api = Mobileclient()

    logged_in = False
    attempts = 0

    while not logged_in and attempts < 3:
        email = input('Email: ')
        password = getpass()

        try:
            logged_in = api.login(email, password, Mobileclient.FROM_MAC_ADDRESS)
        except:
            print()

        attempts += 1

    return api


#api check
def play():

    api = ask_for_credentials()

    if not api.is_authenticated():
        print("Sorry, those credentials weren't accepted.")
        return

    print('Successfully logged in.\n')

    search(api)

#search and play
def search(api):
    search_word = input('Input search word: ')
    try:
        results = api.search(search_word, 1)
    except:
        print("search error")
        search(api)

    resultjson = json.dumps(results)
    resultjson = json.loads(resultjson, object_hook=D)

    try:
        stream_url = api.get_stream_url(resultjson.song_hits[0].track.storeId)

    except:
        print("search error")
        search(api)

    p = vlc.MediaPlayer()
    p.set_mrl(stream_url)
    try:
        p.play()
    except:
        search()

    start = time.time()
    while(True):
        print("Play time: {}".format(time.time() - start))
        music_simple_info(resultjson)
        cmd = input('press \'Enter\' to see info\npress \'s\' to stop and exit\npress \'p\' to pause\npress \'r\' to serch other song\n')
        if cmd == 's':
            p.stop()
            api.logout()
            print('All done!')
            exit()

        elif cmd =='y':
            p.stop()
        elif cmd == 'p':
            p.pause()
            pause_flag = 1
        elif (cmd == 'p') and (pause_flag == 1):
            p.play()
        elif cmd == 'r':
            p.stop()
            search(api)

#print info
def music_simple_info(resultjson):
    print()
    length = int(resultjson.song_hits[0].track.durationMillis)
    album = resultjson.song_hits[0].track.album
    artist = resultjson.song_hits[0].track.artist
    title = resultjson.song_hits[0].track.title
    year = resultjson.song_hits[0].track.year
    print("Tile: {}".format(title))
    print("Album: {}".format(album))
    print("Artist: {}".format(artist))
    print("Year: {}".format(year))
    print("Length: {0}m{1}s".format(length//1000//60, length//1000%60))

if __name__ == '__main__':
    play()

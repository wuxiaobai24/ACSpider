#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 10:56:48 2018

read config for get username and password

@author: wuxiaobai24
"""

from configparser import ConfigParser

config_file = '../../config.ini'

cfg = ConfigParser()
cfg.read(config_file)


def get_user():
    username = cfg.get('USER', 'username')
    password = cfg.get('USER', 'password')
    return {"username": username, "password": password}


def update_last_url(url):
    cfg.set('SPIDER', 'last_url', url)
    with open(config_file, 'w') as f:
        cfg.write(f)


def get_last_url():
    return cfg.get('SPIDER', 'last_url')


if __name__ == '__main__':
    '''test'''
    print(get_user())
    print(get_last_url())
    update_last_url(get_last_url())

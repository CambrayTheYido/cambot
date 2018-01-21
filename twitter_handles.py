#!/usr/bin/env python
#  -*- coding: utf-8 -*-

twitter_handles = {"yotto": "@yottomusic",
                   "deadmau5": "@deadmau5",
                   "eric prydz": "@ericprydz",
                   "dusky": "@duskymusic",
                   "maduk": "@MadukDnB",
                   "no mana": "@ihavenomanas",
                   "pryda": "@ericprydz (Pryda)",
                   "cirez d": "@ericprydz (Cirez D)",
                   "tonja holma" : "@ericprydz (Tonja Holma)",
                   "miike snow": "@miikesnow",
                   "london grammar": "@londongrammar",
                   "jme": "@JmeBBK",
                   "disclosure": "@disclosure",
                   "chase & status": "@chaseandstatus",
                   "kendrick lamar": "@kendricklamar",
                   "madeon": "@madeon",
                   "sub focus": "@subfocus",
                   "matt lange": "@MattLange",
                   "dimension" : "@dimension_uk",
                   "attlas" : "@attlas",
                   "draft" : "@DraftUK",
                   "i_o" : "@i_oofficial",
                   "grabbitz" : "@grabbitz",
                   "kölsch" : "@kolschofficial"
                   }


def is_artist_in_dict(artist_name):
    artist_name = str(artist_name)
    for key, value in twitter_handles.items():
        if artist_name.lower() == key.lower() or key.lower() in artist_name.lower():
            artist_name = artist_name.lower().replace(key, value)
            break
    return artist_name.title()

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telepot
from config import *

def main():
    bot = telepot.Bot(token)
    bot_msg = bot.getMe()
    source = open('config.py', 'a')
    print("bot_id = '" + str(bot_msg['id']) + "'", file=source)
    print("Bot_id was set. Send a message to the bot from father.")
    offset = 1
    while True:
        upd_arr = bot.getUpdates(offset=offset, limit=1)
        if len(upd_arr) == 0:
            continue
        upd = upd_arr[0]
        offset = upd['update_id'] + 1
        if upd['message'] is None:
            print('Text message, please.')
            continue
        print("father_id = '" + str(upd['message']['from']['id']) + "'", file=source)
        from_dict = upd['message']['from']
        name = from_dict['first_name']
        if 'last_name' in from_dict:
            name += ' ' + from_dict['last_name']
        if 'username' in from_dict:
            name += ' @' + from_dict['username']
        print('Father_id was set. The user ' + name + ' is now the father. Run run_me.py to start the bot')
        break;


if __name__ == '__main__':
    main()

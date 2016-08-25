#!/usr/bin/python3
# -*- coding: utf-8 -*-

import telepot
import psycopg2

from datetime import datetime
from functools import reduce

from config import *

class Bot:

    def __init__(self):             # data from config!
        self.bot = telepot.Bot(token)
        self.conn = psycopg2.connect(database=dbname, user=sql_user, password=sql_passwd, host='localhost')
        self.cur = self.conn.cursor()

    def run(self):
        self.bot.message_loop(self.handle, run_forever="Listening")

    def handle(self, msg):
        self.curr_msg = msg
        c_type, chat_type, chat_id = telepot.glance(msg)
        if c_type != 'text':
            return
        if msg['from']['id'] == int(father_id):
            self.process_fathers_message(msg)
            print(msg)
            return
        self.parse(msg, True)
        self.forward(msg)
        print(msg)

    def parse(self, msg, to_me):
        cmd = 'INSERT INTO ' + table_name + ' (' +  reduce(lambda x,y: x+', '+y, cols_names) + ') VALUES (' + ('%s, '*len(cols_names))[:-2] + ');'
        user_name = msg['from']['first_name'] 
        if 'last_name' in msg['from']:
            user_name += ' ' + msg['from']['last_name']
        if 'username' in msg['from']:
            user_name += ' @' + msg['from']['username']
        dt = datetime.fromtimestamp(msg['date'])
        self.cur.execute(cmd, [msg['message_id'], msg['from']['id'], user_name, msg['text'], dt, 't' if to_me == True else 'f'])
        self.conn.commit()

    def confirm_acceptance(self, msg):
        thanks = 'Благодарим за обращение, ваше сообщение будет передано представителю ООО "ЗХТО".'
        self.bot.sendMessage(msg['from']['id'], thanks, reply_to_message_id=msg['message_id']) 

    def forward(self, msg):
        self.bot.forwardMessage(father_id, msg['from']['id'], msg['message_id'])

    def process_fathers_message(self, msg):
        if 'reply_to_message' in msg:
            self.reply_request(msg)
            return
        text = msg['text'].lower()
        space = text.find(' ')
        if space != -1:
            word = text[:space]
            if word == 'show':
                self.show_request(text[space + 1:])
            elif word == 'reply':
                self.reply_request(text[space + 1:])
            elif word == 'send':
                self.send_request(text[space + 1:])
            elif word == 'help':
                self.help_request(text[space + 1:])
            else:
                self.bot.sendMessage(father_id, 'Это сообщение - не команда для бота. Попробуй help.', reply_to_message_id=msg['message_id'])
        else:
            if text == 'help':
                self.help_request()
            elif text == 'send':
                self.send_request()
            else:
                self.bot.sendMessage(father_id, 'Это сообщение - не команда для бота. Попробуй help.', reply_to_message_id=msg['message_id'])

    def show_request(self, *args):
        if len(args) > 0:
            if args[0] == 'contacts':
                self.cur.execute('SELECT DISTINCT user_name FROM ' + table_name)
                text = ''
                for name in self.cur.fetchall():
                    text += name[0] + '\n'
                self.bot.sendMessage(father_id, text)

    def reply_request(self, msg):
        msg1 = msg['reply_to_message']
        if 'forward_from' not in msg1:
            self.bot.sendMessage(father_id, "Can't reply to the message that is not forwarded")
            return
        ffrom = str(msg1['forward_from']['id'])
        fdate = datetime.fromtimestamp(msg1['forward_date'])
        cmd = 'SELECT (id, user_id, date) FROM test WHERE user_id=%s AND date=%s'
        self.cur.execute(cmd, [ffrom, fdate])
        msg_id = self.cur.fetchone()[0]
        print(msg_id)
        msg_id = msg_id.split(',')[0][1:]
        print(msg_id)
        msg2 = self.bot.sendMessage(ffrom, msg['text'], reply_to_message_id=msg_id)
        print(msg2)
        self.parse(msg2, False)

    
    def send_request(self, *args):
        pass
    """
        if len(args) > 0:
            text = args[0]
            to_pos = text.find('to=')
            if to_pos == -1:
                print('no "to", do smth with your code')
                return
            else:
                to_pos += len('to=')
            delim = text[to_pos]
            
            to = msg[msg.find('to=')+4:msg[msg.find
    """

    def help_request(self, *args):
        help_text = 'Что можно, а что я ещё не сделал:\n'
        help_text += 'show contacts - список людей, которым можно отправить сообщение\n'
        help_text += 'Чтобы ответить на сообщение, reply боту на него.\n'
        help_text += 'пока всё'
        self.bot.sendMessage(father_id, help_text)

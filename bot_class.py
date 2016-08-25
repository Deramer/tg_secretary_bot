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
        self.form = {}
        self.stop = {'mode':'start', 'exceptions':[]}
        self.determine = {}

    def run(self):
        self.bot.message_loop(self.handle, run_forever="Listening")

    def handle(self, msg):
        self.curr_msg = msg
        c_type, chat_type, chat_id = telepot.glance(msg)
        if c_type != 'text':
            return
        if msg['from']['id'] == int(father_id):
            self.process_fathers_message(msg)
            #print(msg)
            return
        if ((self.stop['mode'] == 'start' and msg['from']['id'] not in self.stop['exceptions'])
                or (self.stop['mode'] == 'stop' and msg['from']['id'] in self.stop['exceptions'])):
            self.parse(msg, True)
            self.show_message(msg['message_id'])
        else:
            self.parse(msg, True, unread=True)
        #self.forward(msg)
        #print(msg)

    def parse(self, msg, to_me, to_id=None, unread=False):
        cmd = ('INSERT INTO ' + messages_table + ' (' +  reduce(lambda x,y: x+', '+y, messages_cols)
               + ') VALUES (' + ('%s, '*len(messages_cols))[:-2] + ');')
        args = []
        args.append(msg['message_id'])
        self.parse_contact(msg)
        if to_me:
            args.append(msg['from']['id'])
        else:
            if to_id == None:
                args.append(msg['from']['id'])
                print("You better tell self.parse to_id")
            else:
                args.append(to_id)
        args.append(datetime.fromtimestamp(msg['date']))
        if 'reply_to_message' in msg:
            args.append(msg['reply_to_message']['message_id'])
        else:
            args.append(None)
        if 'forward_from' in msg and msg['forward_from'] is not None:
            args.append(self.parse_forward(msg))
            args.append(None)
        else:
            args.append(None)
            args.append(msg['text'])
        args.append('t' if to_me == True else 'f')
        args.append(unread)
        #print(cmd, args)
        self.cur.execute(cmd, args)
        self.conn.commit()

    def parse_contact(self, msg, from_str='from'):
        args = []
        args.append(msg[from_str]['id'])
        args.append(msg[from_str]['first_name'])
        if 'last_name' in msg[from_str]:
            args.append(msg[from_str]['last_name'])
        else:
            args.append('')
        if 'username' in msg[from_str]:
            args.append(msg[from_str]['username'])
        else:
            args.append('')
        cmd = "SELECT * FROM " + contacts_table + " WHERE " + reduce(lambda x,y: x+y+'=%s AND ', contacts_cols, '')[:-5] + ';'
        print(msg)
        self.cur.execute(cmd, args)
        if self.cur.fetchone() is None:
            if from_str == 'from' and args[0] != int(father_id) and args[0] != int(bot_id):
                self.confirm_acceptance(msg)
            cmd = "INSERT INTO " + contacts_table +  ' (' +  reduce(lambda x,y: x+', '+y, contacts_cols) + ") VALUES (" +  ('%s, '*len(forwarded_cols))[:-2] + ');'
            self.cur.execute(cmd, args)
            self.conn.commit()

    def parse_forward(self, msg):
        cmd = 'INSERT INTO ' + forwarded_table + ' (' +  reduce(lambda x,y: x+', '+y, forwarded_cols[1:]) + ') VALUES (' + ('%s, '*len(forwarded_cols[1:]))[:-2] + ');'
        args = []
        args.append(msg['forward_from']['id'])
        #self.parse_contact(msg, from_str='forward_from')
        args.append(datetime.fromtimestamp(msg['forward_date']))
        args.append(msg['text'])
        self.cur.execute(cmd, args)
        self.conn.commit()
        cmd2 = 'SELECT * FROM ' + forwarded_table + ' WHERE from_id=%s AND date=%s'
        self.cur.execute(cmd2, [args[forwarded_cols.index('from_id')-1], args[forwarded_cols.index('date')-1]])
        return self.cur.fetchone()[0]

    def confirm_acceptance(self, msg):
        thanks = 'Благодарим за обращение, ваше сообщение будет передано представителю ООО "ЗХТО".'
        self.bot.sendMessage(msg['from']['id'], thanks, reply_to_message_id=msg['message_id']) 

    def forward(self, msg):
        self.bot.forwardMessage(father_id, msg['from']['id'], msg['message_id'])

    def process_fathers_message(self, msg):
        if msg['text'][0] == '\\':
            cmd = msg['text'][1:].lower()
            if cmd == 'status':
                self.status_request()
                return
        if len(self.determine) > 1:
            self.determine_info(msg=msg)
            return
        if 'reply_to_message' in msg:
            self.reply_request(msg)
            return
        if len(self.form) > 0:
            if msg['text'].lower() == 'cancel':
                self.form = {}
                return
            if self.form['request'] == 'send':
                self.send_request(msg)
                return
            if self.form['request'] == 'stream':
                self.stream_request(msg)
                return
        text = msg['text'].lower()
        space = text.find(' ')
        if space != -1:
            word = text[:space]
            if word == 'show':
                self.show_request(text[space + 1:])
            elif word == 'reply':
                self.reply_request(text[space + 1:])
            elif word == 'send' or text == 'написать' or text == 'write':
                self.send_request(msg)
            elif word == 'stop':
                self.stop_request(msg)
            elif word == 'start':
                self.start_request(msg)
            elif word == 'help':
                self.help_request(text[space + 1:])
            else:
                self.bot.sendMessage(father_id, 'Это сообщение - не команда для бота. Попробуй help.', reply_to_message_id=msg['message_id'])
        else:
            if text == 'help':
                self.help_request()
            elif text == 'send' or text == 'написать' or text == 'write':
                self.send_request()
            elif text == 'stream':
                self.stream_request()
            elif text == 'stop':
                self.stop_request()
            elif text == 'start':
                self.start_request()
            elif text == 'status':
                self.status_request()
            else:
                self.bot.sendMessage(father_id, 'Это сообщение - не команда для бота. Попробуй help.', reply_to_message_id=msg['message_id'])

    def show_request(self, *args):
        if len(args) > 0:
            if args[0] == 'contacts':
                self.cur.execute('SELECT * FROM ' + contacts_table)
                text = ''
                for info in self.cur.fetchall():
                    text += info[1]
                    if info[2] != '':
                        text += ' ' + info[2]
                    if info[3] != '':
                        text += ' @' + info[3]
                    text += '\n'
                self.bot.sendMessage(father_id, text)

    def show_message(self, msg_id, prefix='', is_reply=False):
        self.cur.execute('SELECT * FROM Messages WHERE msg_id=%s', (msg_id,))
        msg_list = self.cur.fetchone()
        if msg_list is None:
            print("No message with id " + str(msg_id) + " in database, can't show it")
            return
        msg = self.msg_list_to_dict(msg_list)
        user_id = msg['from_id']
        name = self.get_full_name_from_id(user_id)
        from_to = prefix
        if msg['to_me']:
            from_to += 'From ' + name + ' to me'
        else:
            from_to += 'From me to ' + name
        from_to += ' at ' + str(msg['date'])
        msg1 = self.bot.sendMessage(father_id, from_to)
        #print(msg)
        if msg['forwarded_id'] is None:
            if msg['reply_to_msg_id'] is None or  is_reply:
                msg2 = self.bot.sendMessage(father_id, msg['text'])
            else:
                msg2 = self.bot.sendMessage(father_id, msg['text'])
                self.show_message(msg['reply_to_msg_id'], 'Which is a reply to the message ', True)
        else:
            msg2 = self.bot.forwardMessage(father_id, msg['from_id'], msg['msg_id'])
        cmd = "INSERT INTO reply (father_id, source_id) VALUES (%s, %s)"
        self.cur.execute(cmd, [msg1['message_id'], msg['msg_id']])
        self.cur.execute(cmd, [msg2['message_id'], msg['msg_id']])
        self.conn.commit()

    def reply_request(self, msg):
        msg1 = msg['reply_to_message']
        self.cur.execute('SELECT * FROM Reply WHERE father_id=%s', [msg1['message_id']])
        #print(msg['message_id'])
        try:
            msg_id = self.cur.fetchone()[1]
        except TypeError:
            print("Can't reply: no source message in 'reply' database")
            return
        self.cur.execute('SELECT * FROM Messages WHERE msg_id=%s', [msg_id])
        msg_list = self.cur.fetchone()
        if msg_list is None:
            print("Can't reply: no source message in 'messages' database")
        msg_dict = self.msg_list_to_dict(msg_list)
        sent_msg = self.bot.sendMessage(msg_dict['from_id'], msg['text'], reply_to_message_id=msg_dict['msg_id'])
        self.parse(sent_msg, False, msg_dict['from_id'])
    
    def send_request(self, *args):
        if len(self.form) == 0:
            self.form['request'] = 'send'
            self.bot.sendMessage(father_id, 'To... ("cancel" to cancel sending)')
        elif len(self.form) == 1:
            full_name = args[0]['text']
            info = self.get_info_from_full_name(full_name)
            if info is None or len(info) == 0:
                self.bot.sendMessage(father_id, 'There is no ' + full_name + ' in the database. Try again or "cancel" to quit.')
                return
            if len(info) == 1:
                self.form['user_id'] = info[0][0]
                text =  'Sending to ' + self.get_full_name_from_info(info[0]) +'\nEnter the text (or "cancel")'
                self.bot.sendMessage(father_id, text)
            print(info)
        elif len(self.form) == 2:
             sent_msg = self.bot.sendMessage(self.form['user_id'], args[0]['text'])
             self.parse(sent_msg, False, self.form['user_id'])
             self.form = {}

    def stream_request(self, *args):
        if len(self.form) == 0:
            self.form['request'] = 'stream'
            if len(args) > 0:
                pass
            else:
                self.bot.sendMessage(father_id, 'To... ("cancel" to cancel sending)')
        elif len(self.form) == 1:
            full_name = args[0]['text']
            info = self.get_info_from_full_name(full_name)
            if info is None or len(info) == 0:
                self.bot.sendMessage(father_id, 'There is no ' + full_name + ' in the database. Try again or "cancel" to quit.')
                return
            if len(info) == 1:
                self.form['user_id'] = info[0][0]
                text =  'Streaming to ' + self.get_full_name_from_info(info[0]) +'\nEnter the text, type "cancel" to stop stream'
                self.bot.sendMessage(father_id, text)
            print(info)
        elif len(self.form) == 2:
             sent_msg = self.bot.sendMessage(self.form['user_id'], args[0]['text'])
             self.parse(sent_msg, False, self.form['user_id'])

    def stop_request(self, *args):
        if len(args) == 0:
            self.stop['mode'] = 'stop'
            self.stop['exceptions'] = []
        elif len(args) == 1:
            text = args[0]['text']
            name = text[text.find(' ')+1:]
            info = self.get_info_from_full_name(name)
            if info is None or len(info) == 0:
                self.bot.sendMessage(father_id, 'There is no ' + name + ' in the database. Try again.')
                return
            if len(info) == 1:
                if self.stop['mode'] == 'stop' and info[0][0] in self.stop['exceptions']:
                    self.stop['exceptions'].remove(info[0][0])
                elif self.stop['mode'] == 'start' and info[0][0] not in self.stop['exceptions']:
                    self.stop['exceptions'].append(info[0][0])

    def start_request(self, *args):
        if len(args) == 0:
            self.stop['mode'] = 'start'
            self.stop['exceptions'] = []
            self.cur.execute("SELECT msg_id, unread FROM Messages WHERE unread='t'")
            unread = self.cur.fetchall()
            for msg in unread:
                self.show_message(msg[messages_cols.index('msg_id')])
            self.cur.execute("UPDATE Messages SET unread='f' WHERE unread='t'")
            self.conn.commit()
        elif len(args) == 1:
            text = args[0]['text']
            name = text[text.find(' ')+1:]
            info = self.get_info_from_full_name(name)
            if info is None or len(info) == 0:
                self.bot.sendMessage(father_id, 'There is no ' + name + ' in the database. Try again.')
                return
            if len(info) == 1:
                user_id = info[0][0]
                view_unr = False
                if self.stop['mode'] == 'start' and user_id in self.stop['exceptions']:
                    self.stop['exceptions'].remove(user_id)
                    view_unr = True
                elif self.stop['mode'] == 'stop' and user_id not in self.stop['exceptions']:
                    self.stop['exceptions'].append(user_id)
                    view_unr = True
                if view_unr:
                    self.cur.execute("SELECT msg_id, from_id, unread FROM Messages WHERE unread='t' AND from_id=%s", (user_id,))
                unread = self.cur.fetchall()
                for msg in unread:
                    self.show_message(msg[messages_cols.index('msg_id')])
                self.cur.execute("UPDATE Messages SET unread='f' WHERE unread='t' AND from_id=%s", (user_id,))
                self.conn.commit()

    def status_request(self):
        status = ''
        if len(self.form) > 0:
            if self.form['request'] == 'send':
                status += 'You are sending message'
                if 'user_id' in self.form:
                    status += ' to ' + self.get_full_name_from_id(self.form['user_id']) + '\n'
                else:
                    status += '\n'
            elif self.form['request'] == 'stream':
                status += 'You are streaming'
                if 'user_id' in self.form:
                    status += ' to ' + self.get_full_name_from_id(self.form['user_id']) + '\n'
                else:
                    status += '\n'
        if self.stop['mode'] == 'stop':
            status += 'Accepting of messages is stopped'
        else:
            status += 'Accepting of messages is not stopped'
        if len(self.stop['exceptions']) > 0:
            status += ' except for the users:\n'
            for user_id in self.stop['exceptions']:
                status += self.get_full_name_from_id(user_id) + '\n'
        else:
            status += '\n'
        self.cur.execute("SELECT unread FROM Messages WHERE unread='t'")
        unread = self.cur.fetchall()
        if unread is None or len(unread) == 0:
            status += "You haven't unread messages\n"
        else:
            status += "You have " + str(len(unread)) + " unread message(s)\n"
        self.bot.sendMessage(father_id, status[:-1])

    def help_request(self, *args):
        help_text = 'Что можно, а что я ещё не сделал:\n'
        help_text += 'show contacts - список людей, которым можно отправить сообщение\n'
        help_text += 'Чтобы ответить на сообщение, reply боту на него.\n'
        help_text += 'send - отправить одно сообщение\n'
        help_text += 'stream - отправлять все сообщения одному человеку\n'
        help_text += 'stop - новые сообщения не будут показываться\n'
        help_text += 'start - новые сообщения будут показываться, не показанные ранее будут показаны сейчас\n' # русский забыл?
        help_text += 'status - текущее состояние бота\n'
        help_text += 'пока всё'
        self.bot.sendMessage(father_id, help_text)

    def determine_info(self, name=None, msg=None):
        if msg == None:
            if name == None:
                print('Did you really call determine_info without arguments?\n')
                return
            info = self.get_info_from_full_name(name)
            if info is None or len(info) == 0:
                self.bot.sendMessage(father_id, 'There is no ' + name + ' in the database. Try again.')
                self.determine['variants'] = []
                self.determine['name'] = name
                self.determine['result'] = ''
                return
            if len(info) == 1:
                self.determine['result'] = info[0]
                return
            if len(info) > 1:
                text = "There're many " + name + " in the database. Which one do you need? (enter number)\n"
                for n, item in enumerate(info):
                    text += str(n) + ') ' +  get_full_name_from_info(item) + '\n'
                self.bot.sendMessage(father_id, text[:-1])
                self.determine['variants'] = info
                self.determine['name'] = name
                self.determine['result'] = ''
                return
        elif name == None:
            if msg['text'].lower() == 'cancel' or msg['text'].lower() == '\\cancel':
                self.determine = {}
                self.form = {}
                return
            if 'variants' not in self.determine:
                print('Determine_info(msg) was called, though variants are not in dictionary. Think again.\n
                        Oh, and if you are not me, be patient. I am just a kid.')
            if len(self.determine['variants']) == 0:
                self.determine_info(msg['text'])
                return
            else:
                n = msg['text']
                try:
                    n = int(n)
                except ValueError:
                    self.bot.sendMessage(father_id, msg['text'] + ' is not a number. Try again.')
                    return
                if n > len(self.determine['variants']) or n < 0:
                    self.bot.sendMesage(father_id, "That number doesn't point to a name. Try again.")
                self.determine['result'] = info[n]
                try:
                    self.determine.pop('name')
                    self.determine.pop('variants')
                except KeyError:
                    print('In desperate attempt to delete keys from self.determine I got KeyError. Func determine_info\n')
                    return


    # internal transfroming functions

    def msg_list_to_dict(self, msg_list):
        msg_dict = {}
        for i, item in enumerate(messages_cols):
            msg_dict[item] = msg_list[i]
        return msg_dict
    
    def get_full_name_from_id(self, msg_id):
        self.cur.execute('SELECT * FROM Contacts WHERE id=%s', (msg_id,))
        l = self.cur.fetchone()
        if l is None:
            return None
        name = l[1]
        if l[2] != '':
            name += ' ' + l[2]
        if l[3] != '':
            name += ' @' + l[3]
        return name

    def get_info_from_full_name(self, name):
        name = name.split()
        username = None
        to_del = -1
        for i, item in enumerate(name):
            if item[0] == '@':
                username = item
                to_del = i
        if to_del != -1:
            del name[to_del]
        if len(name) == 0:
            self.cur.execute('SELECT * FROM Contacts WHERE username=%s', (args[0],))
            return self.cur.fetchall()
        elif len(name) == 1:
            self.cur.execute('SELECT * FROM Contacts WHERE first_name=%s OR last_name=%s', (name[0], name[0]))
            res = self.cur.fetchall()
        elif len(name) == 2:
            cmd = 'SELECT * FROM Contacts WHERE (first_name=%s AND last_name=%s) OR (first_name = %s AND last_name=%s)'
            self.cur.execute(cmd, (name[0], name[1], name[1], name[0]))
            res = self.cur.fetchall()
        if username is not None and res is not None:
            res = [x for x in res if x[3] == username]
        return res

    def get_full_name_from_info(self, l):
        name = l[1]
        if l[2] != '':
            name += ' ' + l[2]
        if l[3] != '':
            name += ' @' + l[3]
        return name

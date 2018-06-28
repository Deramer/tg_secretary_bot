"""
You need to fill this, until next comment.
token will be given you by botfather in telegram.
sql_host, sql_user, sql_passwd and dbname are what they seem to be. I won't create them.
father_id is telegram id of human being that will read messages sent to bot and write sage answers.
bot_id is id of the bot. There're must be an echo bot to determine father_id and bot_id.
"""
token = '613785453:AAFPOTCzlGf75ySCGb-Af07-_OoamNd_D2c'
sql_host = 'localhost'
sql_user = 'telegram_bot'
sql_passwd = '123456'
dbname = 'telegram'
#father_id = '259114535'
#bot_id = '322932958'
bot_id = '613785453'
father_id = '241300348'

heroku = True

"""
Ok, that's it. The rest of file is about sql tables, I'll hopefully handle them myself.
You can change tables' names and some of the columns' names and still have hope that bot will work. Though I see no reason for this.
"""
messages, forwarded, reply, contacts, blacklist, media, blocked = {}, {}, {}, {}, {}, {}, {}
all_tables = [messages, forwarded, reply, contacts, blacklist, media, blocked]
messages['table'] = 'messages'
messages['cols'] = ['msg_id', 'from_id', 'date', 'reply_to_msg_id', 'forwarded_id', 'text', 'to_me', 'unread']
messages['types'] = ['INT UNIQUE', 'INT', 'TIMESTAMP', 'INT', 'INT', 'VARCHAR(2000)', 'BOOLEAN', 'BOOLEAN']
forwarded['table'] = 'forwarded'
forwarded['cols'] = ['id', 'from_id', 'date', 'text']
forwarded['types'] = ['SERIAL PRIMARY KEY', 'INT', 'TIMESTAMP', 'VARCHAR(2000)']
reply['table'] = 'reply'                   # OK. When I'm forwarding a message to the father chat, I'm losing it's original id
reply['cols'] = ['father_id', 'source_id']   # "reply" table allows to restore this information
reply['types'] = ['INT', 'INT']
contacts['table'] = 'contacts'
contacts['cols'] = ['id', 'first_name', 'last_name', 'username']
contacts['types'] = ['INT UNIQUE', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)']
blacklist['table'] = 'blacklist'
blacklist['cols'] = ['id', 'first_name', 'last_name', 'username']
blacklist['types'] = ['INT UNIQUE', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)']
media['table'] = 'media'
media['cols'] = ['msg_id', 'from_id', 'date', 'reply_to_msg_id', 'forwarded_id', 'type', 'file_id', 'to_me', 'unread']
media['types'] = ['INT UNIQUE', 'INT', 'TIMESTAMP', 'INT', 'INT', 'INT', 'VARCHAR(120)', 'BOOLEAN', 'BOOLEAN']
blocked['table'] = 'blocked'
blocked['cols'] = ['id', 'first_name', 'last_name', 'username']
blocked['types'] = ['INT PRIMARY KEY', 'VARCHAR(100)', 'VARCHAR(100)', 'VARCHAR(100)']

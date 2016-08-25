"""
You need to fill this, until next comment.
token will be given you by botfather in telegram.
sql_host, sql_user, sql_passwd and dbname are what they seem to be. I won't create them.
father_id is telegram id of human being that will read messages sent to bot and write sage answers.
bot_id is id of bot. There're must be an echo bot to determine father_id and bot_id.
"""
token = '248756472:AAHcRGmbcjkk11H2R_hKMpLLE5DMU47TOEw'
sql_host = 'localhost'
sql_user = 'telegram_bot'
sql_passwd = '123456'
dbname = 'telegram'
#father_id = '123990110'
father_id = '259114535'            # my id, actually, just for debug
bot_id = '248756472'
"""
Ok, that's it. The rest of file is about sql tables, I'll hopefully handle them myself.
You can change tables' names and some of the columns' names and still have hope that bot will work. Though I see no reason for this.
"""
forwarded_table = 'forwarded'
messages_table = 'messages'
forwarded_cols = ['id', 'from_id', 'date', 'text']
messages_cols = ['msg_id', 'from_id', 'date', 'reply_to_msg_id', 'forwarded_id', 'text', 'to_me', 'unread']
reply_table = 'reply'                   # OK. When I'm forwarding a message to the father chat, I'm losing it's original id
reply_cols = ['father_id', 'source_id']   # "reply" table allows to restore this information
contacts_table = 'contacts'
contacts_cols = ['id', 'first_name', 'last_name', 'username']
blacklist_table = 'blacklist'
blacklist_cols = ['id', 'first_name', 'last_name', 'username']
media_table = 'media'
media_cols = ['msg_id', 'from_id', 'date', 'reply_to_msg_id', 'forwarded_id', 'type', 'file_id', 'to_me', 'unread']

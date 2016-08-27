#Telegram bot
Does it need a name?

##Requirements

To run program you'll need:

- python3,

- PostgreSQL (9.4+),

- psycopg2,

- telepot.

Tested configuration is python3.5.2, PostgreSQL v9.5.4, psycopg2 v2.6.1, telepot v8.3 and Ubuntu 16.04LTS.

After installing that, fill first lines of **config.py**. Open it for instructions.

Finally, run run\_me.py.


##Extended help.

Users' names are case-sensitive, so 'user' and 'User' are completely different users. User's name is 'required' first name and 'optional' last name and username (the last starts with '@'). Enter any subset of them to start identifing user and follow instructions. Print "cancel" or "\cancel" to quit.
Commands are case-insensitive. "cancel", "Cancel" and "CaNcEl" are completely identical.

###Method's of sending:

1. just type anything that is not a command. You'll be asked about target user.

2. Type some text, on the next line print **To** and something, identifying target user.

3. Send message **send** to the bot and follow instructions.

4. To reply a particular message, use telegram function 'reply'. Bot will reply to user that sent message.

5. Send message **stream** and follow instructions to open a "stream" to user. Every message sent to the bot during "streaming" will be sent to that user instantly. "Cancel" will stop this madness. Messages from every user will be shown immediately after recieving.

6. **Dialog** is similar to "stream", but only messages from the target user will be shown. The rest will be shown after closing of the dialog.

7. To send document/photo/video/audio, send it to the bot. In stream and dialog it will be sent to the target user, in normal mode you will be asked about the target.

8. While sending a particular message, enter **all** or **.all** instead of user's name to send it to all users from contacts list.

###Show family

Show gives you information of various kinds.

**show contacts** - full list of users who can be targets in any operation that requires user. In telegram bot can't write to user first and can't send messages to other bots at all, so this is really full list.

**show blacklist** - about blacklist see paragraph in "Other functions". This command... shows blacklist.

**show status** - show: what you are doing (stream, dialog); status of accepting messages (stop/start, exceptions); number of unread messages. Also available as **status** and **\status**.

**show message _id_** - show message with given numeric id. Id's can be found in text files with history.

**show history** or **show messages** - show history in various ways. 

- Last - will show last _number_ messages, where _number_ will be asked in process.

- All - show all history.

- By date - messages sent in the given time interval.

History can be put in text file and sent as a document.

###Other functions

Enter **blacklist** and **unblacklist** with user's name to add to and remove from the blacklist. Blacklisted users are not allowed to send messages to the bot.

Enter **stop** to stop viewing recieved messages. Enter **start** to view all received during "stop" mode and return to normal mode.
"Stop" or "start" with user's name will do exactly the same for particular user.
Dialog with a user is "stop", "start user", "stream" to user.

**Cancel** or **\cancel** stops nearly every operation.

**\reset** resets any operation you were doing, as well as call **start**. It is not really possible to distinguish bot after **\reset** and after restart, except that for restarting you need system administrator to boot server. If something goes horribly wrong - **\reset** it.

##Notes on the code:

- There're three variables that control the flow of the data. self.stop for stop/start, self.determine for getting id of a target user from "father's" information and self.form for filling "form", which contains information that will be needed after next message of father.
Do not increase this number. Now it all is just complicated, but after a few wrong steps it will become not-working-at-all.

- functions that are mentioned in self.process\_father\_message must never call each other. NEVER. They all actively use that three variables, and "undefined behaviour" is the most kind words for the consequences of wrong call.
(Actually, start() and stop() can interact with other functions - they are working with different variables.)

- self.determine\_info and self.parse are created to be called from other functions. So they are quite complicated. Touch them only if you are completely sure that you know what you are doing.

- self.special\_send\_request is a good example. If there must be a new feature, let it be alike.
(though, I'm sure, it is not an example of good style. It is just about "how all this works".)

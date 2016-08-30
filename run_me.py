#!/usr/bin/python3
# -*- coding: utf-8 -*-

import bot_class
import sys

def main():
    while True:
        try:
            bot = bot_class.Bot()
            bot.run()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e,file=sys.stdout)

if __name__ == '__main__':
    main()

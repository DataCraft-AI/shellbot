#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import logging
import mock
from multiprocessing import Process, Queue
import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from shellbot import Context, ShellBot, Shell


my_bot = ShellBot(mouth=Queue())

class CommandsTests(unittest.TestCase):

    def setUp(self):
        my_bot.shell = Shell(bot=my_bot)

    def test_noop(self):

        logging.info('***** noop')

        from shellbot.commands import Noop

        c = Noop(my_bot)

        self.assertEqual(c.keyword, u'pass')
        self.assertEqual(c.information_message, u'Do absolutely nothing')
        self.assertEqual(c.usage_message, None)
        self.assertTrue(c.is_interactive)
        self.assertTrue(c.is_hidden)

        c.execute()
        with self.assertRaises(Exception):
            my_bot.mouth.get_nowait()


if __name__ == '__main__':

    Context.set_logger()
    sys.exit(unittest.main())

#!/usr/bin/env python

import colorlog
import unittest
import logging
import os
from multiprocessing import Process, Queue
import sys

sys.path.insert(0, os.path.abspath('..'))

from shellbot.context import Context
from shellbot.shell import Shell


class CommandsTests(unittest.TestCase):

    def test_base(self):

        settings = {
            'hello': 'world',
        }
        context = Context(settings)
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.base import Command

        c = Command(shell)

        self.assertEqual(c.context.get('general.hello'), 'world')

        self.assertEqual(c.keyword, None)
        self.assertEqual(c.information_message, None)
        self.assertEqual(c.usage_message, None)
        self.assertTrue(c.is_interactive)
        self.assertFalse(c.is_hidden)

        c.execute()
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_from_base(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.base import Command

        c = Command(shell)
        c.keyword = 'batman'
        c.information_message = "I'm Batman!"
        c.execute()
        self.assertEqual(mouth.get(), c.information_message)
        with self.assertRaises(Exception):
            print(mouth.get_nowait())

        class Batcave(Command):
            keyword = 'batcave'
            information_message = "The Batcave is silent..."

            def execute(self, arguments=None):
                if arguments:
                    self.shell.say("The Batcave echoes, '{0}'".format(arguments))
                else:
                    self.shell.say(self.information_message)

        c = Batcave(shell)
        c.execute('')
        self.assertEqual(mouth.get(), "The Batcave is silent...")
        c.execute('hello?')
        self.assertEqual(mouth.get(), "The Batcave echoes, 'hello?'")
        with self.assertRaises(Exception):
            print(mouth.get_nowait())

        class Batsignal(Command):
            keyword = 'batsignal'
            information_message = "NANA NANA NANA NANA"
            information_file = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"

            def execute(self, arguments=None):
                self.shell.say(self.information_message,
                               file=c.information_file)

        c = Batsignal(shell)
        c.execute()
        item = mouth.get()
        self.assertEqual(item.message, c.information_message)
        self.assertEqual(item.file, c.information_file)

    def test_noop(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.noop import Noop

        c = Noop(shell)

        self.assertEqual(c.keyword, 'pass')
        self.assertEqual(c.information_message, 'Does absolutely nothing.')
        self.assertEqual(c.usage_message, None)
        self.assertTrue(c.is_interactive)
        self.assertTrue(c.is_hidden)

        c.execute()
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_version(self):

        settings = {
            'bot': {'name': 'testy', 'version': '17.4.1'},
        }
        context = Context(settings)
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.version import Version

        c = Version(shell)

        self.assertEqual(c.keyword, 'version')
        self.assertEqual(c.information_message, 'Displays software version.')
        self.assertEqual(c.usage_message, None)
        self.assertTrue(c.is_interactive)
        self.assertFalse(c.is_hidden)

        c.execute()
        self.assertEqual(mouth.get(), 'testy version 17.4.1')
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_help(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.help import Help

        c = Help(shell)

        self.assertEqual(c.keyword, 'help')
        self.assertEqual(
            c.information_message,
            'Lists available commands and related usage information.')
        self.assertEqual(c.usage_message, 'help <command>')
        self.assertTrue(c.is_interactive)
        self.assertFalse(c.is_hidden)

        c.execute()
        self.assertEqual(mouth.get(), 'No command has been found.')
        with self.assertRaises(Exception):
            print(mouth.get_nowait())

    def test_help_true(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        shell.load_command('shellbot.commands.help')

        from shellbot.commands.help import Help

        c = Help(shell)

        c.execute()
        self.assertEqual(
            mouth.get(),
            'help - Lists available commands and related usage information.')
        with self.assertRaises(Exception):
            mouth.get_nowait()

        c.execute("help")
        self.assertEqual(
            mouth.get(),
            'help - Lists available commands and related usage information.')
        self.assertEqual(
            mouth.get(),
            'usage:')
        self.assertEqual(
            mouth.get(),
            'help <command>')
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_help_false(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.help import Help

        c = Help(shell)

        c.execute()
        self.assertEqual(mouth.get(), 'No command has been found.')
        with self.assertRaises(Exception):
            mouth.get_nowait()

        c.execute("*unknown*command*")
        self.assertEqual(mouth.get(), 'No command has been found.')
        with self.assertRaises(Exception):
            print(mouth.get_nowait())

        shell.load_command('shellbot.commands.help')

        c.execute("*unknown*command*")
        self.assertEqual(mouth.get(), 'This command is unknown.')
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_echo(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.echo import Echo

        c = Echo(shell)

        self.assertEqual(c.keyword, 'echo')
        self.assertEqual(c.information_message, 'Echoes input string.')
        self.assertEqual(c.usage_message, 'echo "a string to be echoed"')
        self.assertTrue(c.is_interactive)
        self.assertFalse(c.is_hidden)

        message = "hello world"
        c.execute(message)
        self.assertEqual(mouth.get(), message)
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_sleep(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.sleep import Sleep

        c = Sleep(shell)

        self.assertEqual(c.keyword, 'sleep')
        self.assertEqual(c.information_message, 'Sleeps for a while.')
        self.assertEqual(c.usage_message, 'sleep <n>')
        self.assertFalse(c.is_interactive)
        self.assertTrue(c.is_hidden)

        c.execute('')
        with self.assertRaises(Exception):
            mouth.get_nowait()

        c.execute('2')
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_default(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        from shellbot.commands.default import Default

        c = Default(shell)

        self.assertEqual(c.keyword, '*default')
        self.assertEqual(c.information_message, 'Handles unmatched command.')
        self.assertEqual(c.usage_message, None)
        self.assertTrue(c.is_interactive)
        self.assertTrue(c.is_hidden)

        shell.verb = '*unknown*'
        c.execute('test of default command')
        self.assertEqual(mouth.get(),
                         "Sorry, I do not know how to handle '*unknown*'")
        with self.assertRaises(Exception):
            mouth.get_nowait()

    def test_empty(self):

        context = Context()
        mouth = Queue()
        shell = Shell(context, mouth)

        shell.load_command('shellbot.commands.help')

        from shellbot.commands.empty import Empty

        c = Empty(shell)

        self.assertEqual(c.keyword, '*empty')
        self.assertEqual(c.information_message, 'Handles empty command.')
        self.assertEqual(c.usage_message, None)
        self.assertTrue(c.is_interactive)
        self.assertTrue(c.is_hidden)

        c.execute()
        self.assertEqual(
            mouth.get(),
            'help - Lists available commands and related usage information.')
        with self.assertRaises(Exception):
            print(mouth.get_nowait())

if __name__ == '__main__':

    handler = colorlog.StreamHandler()
    formatter = colorlog.ColoredFormatter(
        "%(asctime)-2s %(log_color)s%(message)s",
        datefmt='%H:%M:%S',
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )
    handler.setFormatter(formatter)

    logging.getLogger('').handlers = []
    logging.getLogger('').addHandler(handler)

    logging.getLogger('').setLevel(level=logging.DEBUG)

    sys.exit(unittest.main())

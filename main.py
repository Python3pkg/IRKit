#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (print_function, division, absolute_import, unicode_literals, )

import json
from argparse import ArgumentParser


from irkit.resolve import resolve_irkit_addresses
from irkit._info import VERSION


def save_signal(name, signal):
    from os import environ, path, makedirs

    config_root = path.join(environ['HOME'], '.config')
    if not path.exists(config_root):
        makedirs(config_root)
    dir_to_save = path.join(config_root, 'irkit-py')
    if not path.exists(dir_to_save):
        makedirs(dir_to_save)

    with open(path.join(dir_to_save, 'signal.json'), 'w+') as f:
        config = json.loads(f.read() or '{}')
        config[name] = signal

        f.write(json.dumps(config))


desc = """
IRKit CLI Client for Python. v{0} See also http://getirkit.com/#IRKit-Device-API
""".format(VERSION)
CMD_PARSER = ArgumentParser(description=desc)


subparsers = CMD_PARSER.add_subparsers(help='sub-command help')


def local_func(args):
    from irkit.api import LocalAPI

    if args.verbose:
        from logging import DEBUG
        from irkit import logger, handler
        handler.setLevel(DEBUG)
        logger.setLevel(DEBUG)

    base_uri = resolve_irkit_addresses()[0]
    if args.host:
        print(base_uri)
        return

    api = LocalAPI(base_uri)
    if args.keys:
        print(api.keys.post())
        print('this is your key')
        return
    elif args.send:
        raw_data = json.loads(args.send)
        result = api.messages.post(raw_data)
        print('')
        print('send signal: ' + unicode(result))
        return
    elif args.retrieve:
        result = api.messages.get()
        if result.is_empty():
            return print('retrieve empty data. you should send signal to irkit before retrieve.')

        if args.save:
            save_signal(args.save, result.as_dict())
            print('save signal as {} in ~/.config/irkit-py/signal.json'.format(args.save))
        print('')
        print('retrieve: ' + str(result))
        return
    else:
        print('need argument. see help')
        return


LOCAL_PARSER = subparsers.add_parser('local', help='api for locals.')
LOCAL_PARSER.add_argument('--host', action='store_true', help='show irkit host')
LOCAL_PARSER.add_argument('-k', '--keys', action='store_true', help='get a client token.')
LOCAL_PARSER.add_argument('-r', '--retrieve', action='store_true', help='retrieve a signal')
LOCAL_PARSER.add_argument(
    '--save',
    action='store',
    default='',
    metavar='signal-name',
    help='you should appoint a name. save retrieved signal to ~/.config/irkit-py/signal.json with name',
)
LOCAL_PARSER.add_argument('-s', '--send', metavar='signal-info', help='send a signal data or api response')
# TODO: verbose level hint: add_argument(action='count')
LOCAL_PARSER.add_argument('-v', '--verbose', action='store_true', help='put verbose logs')
LOCAL_PARSER.set_defaults(func=local_func)


INTERNET = subparsers.add_parser('global', help='api for internets.')


args = CMD_PARSER.parse_args()
args.func(args)

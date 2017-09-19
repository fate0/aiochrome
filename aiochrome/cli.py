# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import click
import asyncio
import aiochrome
from functools import update_wrapper


click.disable_unicode_literals_warning = True
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


shared_options = [
    click.option("--host", "-t", type=click.STRING, default='127.0.0.1', help="HTTP frontend host"),
    click.option("--port", "-p", type=click.INT, default=9222, help="HTTP frontend port"),
    click.option("--secure", "-s", is_flag=True, help="HTTPS/WSS frontend")
]


def add_shared_options(func):
    for option in shared_options:
        func = option(func)

    return func


class JSONTabEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, aiochrome.Tab):
            return obj._kwargs

        return super(JSONTabEncoder, self).default(self, obj)


def coro(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))

    return update_wrapper(wrapper, f)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(aiochrome.__version__)
def main():
    pass


@main.command(context_settings=CONTEXT_SETTINGS)
@add_shared_options
@coro
async def list(host, port, secure):
    """list all the available targets/tabs"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)
    try:
        browser = aiochrome.Browser(url)
        click.echo(json.dumps(await browser.list_tab(), cls=JSONTabEncoder, indent=4))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("url", required=False)
@add_shared_options
@coro
async def new(host, port, secure, url="about:blank"):
    """create a new target/tab"""
    _url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = aiochrome.Browser(_url)
        click.echo(json.dumps(await browser.new_tab(url), cls=JSONTabEncoder, indent=4))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("id")
@add_shared_options
@coro
async def activate(host, port, secure, id):
    """activate a target/tab by id"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = aiochrome.Browser(url)
        click.echo(await browser.activate_tab(id))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("id")
@add_shared_options
@coro
async def close(host, port, secure, id):
    """close a target/tab by id"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = aiochrome.Browser(url)
        click.echo(await browser.close_tab(id))
    except Exception as e:
        click.echo(e)


@main.command(context_settings=CONTEXT_SETTINGS)
@add_shared_options
@coro
async def version(host, port, secure):
    """show the browser version"""
    url = "%s://%s:%s" % ("https" if secure else "http", host, port)

    try:
        browser = aiochrome.Browser(url)
        click.echo(json.dumps(await browser.version(), indent=4))
    except Exception as e:
        click.echo(e)


if __name__ == '__main__':
    main()

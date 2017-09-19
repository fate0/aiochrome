# -*- coding: utf-8 -*-

import os
import json
import asyncio
import logging
import warnings
import functools
import websockets

from .exceptions import *


__all__ = ["Tab"]


logger = logging.getLogger(__name__)


class GenericAttr:
    def __init__(self, name, tab):
        self.__dict__['name'] = name
        self.__dict__['tab'] = tab

    def __getattr__(self, item):
        method_name = "%s.%s" % (self.name, item)
        event_listener = self.tab.get_listener(method_name)

        if event_listener:
            return event_listener

        return functools.partial(self.tab.call_method, method_name)

    def __setattr__(self, key, value):
        self.tab.set_listener("%s.%s" % (self.name, key), value)


class Tab:
    status_initial = 'initial'
    status_started = 'started'
    status_stopped = 'stopped'

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.type = kwargs.get("type")
        self.debug = os.getenv("DEBUG", False)
        self.loop = kwargs.get('loop', None) or asyncio.get_event_loop()

        self._websocket_url = kwargs.get("webSocketDebuggerUrl")
        self._kwargs = kwargs

        self._cur_id = 1000

        self._ws = None

        self._recv_task = None
        self._handle_event_task = None

        self._stopped = asyncio.Event()
        self._started = False
        self.status = self.status_initial

        self.event_handlers = {}
        self.method_results = {}
        self.event_queue = asyncio.Queue()

    async def _send(self, message, timeout=None):
        if 'id' not in message:
            self._cur_id += 1
            message['id'] = self._cur_id

        message_json = json.dumps(message)

        if self.debug:  # pragma: no cover
            print("SEND ► %s" % message_json)

        if not isinstance(timeout, (int, float)) or timeout > 1:
            q_timeout = 1
        else:
            q_timeout = timeout / 2.0

        try:
            queue = asyncio.Queue()
            self.method_results[message['id']] = queue

            # just raise the exception to user
            await self._ws.send(message_json)

            while not self._stopped.is_set():
                try:
                    if isinstance(timeout, (int, float)):
                        if timeout < q_timeout:
                            q_timeout = timeout

                        timeout -= q_timeout

                    return await asyncio.wait_for(queue.get(), q_timeout)
                except asyncio.TimeoutError:
                    if isinstance(timeout, (int, float)) and timeout <= 0:
                        raise TimeoutException("Calling %s timeout" % message['method'])

                    continue

            raise UserAbortException("User abort, call stop() when calling %s" % message['method'])
        finally:
            self.method_results.pop(message['id'])

    async def _recv_loop(self):
        while not self._stopped.is_set():
            try:
                message_json = await self._ws.recv()
                message = json.loads(message_json)
            except:
                continue

            if self.debug:  # pragma: no cover
                print('◀ RECV %s' % message_json)

            if "method" in message:
                await self.event_queue.put(message)

            elif "id" in message:
                if message["id"] in self.method_results:
                    await self.method_results[message['id']].put(message)
            else:  # pragma: no cover
                warnings.warn("unknown message: %s" % message)

    async def _handle_event_loop(self):
        while True:
            event = await self.event_queue.get()

            if event['method'] in self.event_handlers:
                try:
                    await self.event_handlers[event['method']](**event['params'])
                except Exception as e:
                    logger.error("callback %s exception" % event['method'], exc_info=True)

    def __getattr__(self, item):
        attr = GenericAttr(item, self)
        setattr(self, item, attr)
        return attr

    async def call_method(self, _method, *args, **kwargs):
        if not self._started:
            raise RuntimeException("Cannot call method before it is started")

        if args:
            raise CallMethodException("the params should be key=value format")

        if self._stopped.is_set():
            raise RuntimeException("Tab has been stopped")

        timeout = kwargs.pop("_timeout", None)
        result = await self._send({"method": _method, "params": kwargs}, timeout=timeout)
        if 'result' not in result and 'error' in result:
            warnings.warn("%s error: %s" % (_method, result['error']['message']))
            raise CallMethodException("calling method: %s error: %s" % (_method, result['error']['message']))

        return result['result']

    def set_listener(self, event, callback):
        if not callback:
            return self.event_handlers.pop(event, None)

        if not callable(callback):
            raise RuntimeException("callback should be callable")

        self.event_handlers[event] = callback
        return True

    def get_listener(self, event):
        return self.event_handlers.get(event, None)

    def del_all_listeners(self):
        self.event_handlers = {}
        return True

    async def start(self):
        if self._started:
            return False

        if not self._websocket_url:
            raise RuntimeException("Already has another client connect to this tab")

        self._started = True
        self.status = self.status_started
        self._stopped.clear()
        self._ws = await websockets.connect(self._websocket_url, loop=self.loop)

        self._recv_task = asyncio.ensure_future(self._recv_loop(), loop=self.loop)
        self._handle_event_task = asyncio.ensure_future(self._handle_event_loop(), loop=self.loop)

        return True

    async def stop(self):
        if self._stopped.is_set():
            return False

        if not self._started:
            raise RuntimeException("Tab is not running")

        self.status = self.status_stopped
        self._stopped.set()
        await self._ws.close()
        self._recv_task.cancel()
        self._handle_event_task.cancel()
        return True

    async def wait(self, timeout=None):
        if not self._started:
            raise RuntimeException("Tab is not running")

        if timeout:
            try:
                await asyncio.wait_for(self._stopped.wait(), timeout)
                return True
            except asyncio.TimeoutError:
                return False

        await self._recv_task
        await self._handle_event_task

    def __str__(self):
        return "<Tab [%s]>" % self.id

    __repr__ = __str__

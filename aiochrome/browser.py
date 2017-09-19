#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import aiohttp

from .tab import Tab


__all__ = ["Browser"]


class Browser:
    _all_tabs = {}

    def __init__(self, url="http://127.0.0.1:9222", loop=None):
        self.dev_url = url
        self.loop = loop or asyncio.get_event_loop()

        if self.dev_url not in self._all_tabs:
            self._tabs = self._all_tabs[self.dev_url] = {}
        else:
            self._tabs = self._all_tabs[self.dev_url]

        self.session = aiohttp.ClientSession(loop=self.loop)

    async def new_tab(self, url=None, timeout=None):
        url = url or ''
        async with self.session.get("{}/json/new?{}".format(self.dev_url, url), timeout=timeout) as rp:
            tab_json = await rp.json()
            tab = Tab(**tab_json)
            self._tabs[tab.id] = tab
            return tab

    async def list_tab(self, timeout=None):
        async with self.session.get("{}/json".format(self.dev_url), timeout=timeout) as rp:
            tabs_map = {}
            for tab_json in await rp.json():
                if tab_json['type'] != 'page':  # pragma: no cover
                    continue

                if tab_json['id'] in self._tabs and self._tabs[tab_json['id']].status != Tab.status_stopped:
                    tabs_map[tab_json['id']] = self._tabs[tab_json['id']]
                else:
                    tabs_map[tab_json['id']] = Tab(**tab_json)

            self._tabs = tabs_map
            return list(self._tabs.values())

    async def activate_tab(self, tab_id, timeout=None):
        if isinstance(tab_id, Tab):
            tab_id = tab_id.id

        async with self.session.get("%s/json/activate/%s" % (self.dev_url, tab_id), timeout=timeout) as rp:
            return await rp.text()

    async def close_tab(self, tab_id, timeout=None):
        if isinstance(tab_id, Tab):
            tab_id = tab_id.id

        tab = self._tabs.pop(tab_id, None)
        if tab and tab.status == Tab.status_started:  # pragma: no cover
            tab.stop()

        async with self.session.get("%s/json/close/%s" % (self.dev_url, tab_id), timeout=timeout) as rp:
            return await rp.text()

    async def version(self, timeout=None):
        async with self.session.get("%s/json/version" % self.dev_url, json=True, timeout=timeout) as rp:
            return await rp.json()

    def __str__(self):
        return '<Browser %s>' % self.dev_url

    __repr__ = __str__

    def __del__(self):
        if not self.session.closed:
            self.session.close()

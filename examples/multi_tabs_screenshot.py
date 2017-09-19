#! /usr/bin/env python
# -*- coding: utf-8 -*-

import time
import base64
import asyncio
import aiochrome


urls = [
    "http://fatezero.org",
    "http://blog.fatezero.org",
    "http://github.com/fate0",
    "http://github.com/fate0/aiochrome"
]


class EventHandler(object):
    screen_lock = asyncio.Lock()

    def __init__(self, browser, tab):
        self.browser = browser
        self.tab = tab
        self.start_frame = None

    async def frame_started_loading(self, frameId):
        if not self.start_frame:
            self.start_frame = frameId

    async def frame_stopped_loading(self, frameId):
        if self.start_frame == frameId:
            await self.tab.Page.stopLoading()

            async with self.screen_lock:
                # must activate current tab
                print(await self.browser.activate_tab(self.tab.id))

                try:
                    data = await self.tab.Page.captureScreenshot()
                    with open("%s.png" % time.time(), "wb") as fd:
                        fd.write(base64.b64decode(data['data']))
                finally:
                    await self.tab.stop()


async def close_all_tabs(browser):
    tabs = await browser.list_tab()
    if len(tabs) == 0:
        return

    for tab in tabs:
        try:
            await tab.stop()
        except aiochrome.RuntimeException:
            pass

        await browser.close_tab(tab)

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 0


async def main():
    browser = aiochrome.Browser()

    await close_all_tabs(browser)

    tabs = []
    for i in range(len(urls)):
        tabs.append(await browser.new_tab())

    for i, tab in enumerate(tabs):
        eh = EventHandler(browser, tab)
        tab.Page.frameStartedLoading = eh.frame_started_loading
        tab.Page.frameStoppedLoading = eh.frame_stopped_loading

        await tab.start()
        await tab.Page.stopLoading()
        await tab.Page.enable()
        await tab.Page.navigate(url=urls[i])

    for tab in tabs:
        await tab.wait(60)
        await tab.stop()
        await browser.close_tab(tab)

    print('Done')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()

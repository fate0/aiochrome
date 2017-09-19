#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
require chrome version >= 61.0.3119.0
headless mode
"""


import time
import asyncio
import aiochrome


class EventHandler(object):
    def __init__(self, browser, tab):
        self.browser = browser
        self.tab = tab
        self.start_frame = None
        self.is_first_request = True
        self.html_content = None

    async def frame_started_loading(self, frameId):
        if not self.start_frame:
            self.start_frame = frameId

    async def request_intercepted(self, interceptionId, request, **kwargs):
        if self.is_first_request:
            self.is_first_request = False
            headers = request.get('headers', {})
            headers['Test-key'] = 'test-value'
            await self.tab.Network.continueInterceptedRequest(
                interceptionId=interceptionId,
                headers=headers,
                method='POST',
                postData="hello post data: %s" % time.time()
            )
        else:
            await self.tab.Network.continueInterceptedRequest(
                interceptionId=interceptionId
            )

    async def frame_stopped_loading(self, frameId):
        if self.start_frame == frameId:
            await self.tab.Page.stopLoading()
            result = await self.tab.Runtime.evaluate(expression="document.documentElement.outerHTML")
            self.html_content = result.get('result', {}).get('value', "")
            print(self.html_content)
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
    for i in range(4):
        tabs.append(await browser.new_tab())

    for i, tab in enumerate(tabs):
        eh = EventHandler(browser, tab)
        tab.Network.requestIntercepted = eh.request_intercepted
        tab.Page.frameStartedLoading = eh.frame_started_loading
        tab.Page.frameStoppedLoading = eh.frame_stopped_loading

        await tab.start()
        await tab.Page.stopLoading()
        await tab.Page.enable()
        await tab.Network.setRequestInterceptionEnabled(enabled=True)
        await tab.Page.navigate(url="http://httpbin.org/post")

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

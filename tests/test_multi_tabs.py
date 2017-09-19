# -*- coding: utf-8 -*-

import pytest
import asyncio
import logging
import aiochrome
import functools


logging.basicConfig(level=logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)


async def close_all_tabs(browser):
    tabs = await browser.list_tab()
    if len(tabs) == 0:
        return

    logging.debug("[*] recycle")
    for tab in tabs:
        await browser.close_tab(tab)

    await asyncio.sleep(1)
    assert len(browser.list_tab()) == 0


@pytest.mark.asyncio
async def new_multi_tabs(browser, n):
    tabs = []
    for i in range(n):
        tabs.append(await browser.new_tab())

    return tabs


@pytest.mark.asyncio
async def test_normal_callmethod():
    browser = aiochrome.Browser()
    tabs = await new_multi_tabs(browser, 10)

    for tab in tabs:
        await tab.start()
        result = await tab.Page.navigate(url="http://www.fatezero.org")
        assert result['frameId']

    await asyncio.sleep(3)

    for tab in tabs:
        result = await tab.Runtime.evaluate(expression="document.domain")
        assert result['result']['type'] == 'string'
        assert result['result']['value'] == 'www.fatezero.org'
        await tab.stop()


@pytest.mark.asyncio
async def test_set_event_listener():
    browser = aiochrome.Browser()
    tabs = await new_multi_tabs(browser, 10)

    async def request_will_be_sent(tab, **kwargs):
        await tab.stop()

    for tab in tabs:
        await tab.start()
        tab.Network.requestWillBeSent = functools.partial(request_will_be_sent, tab)
        await tab.Network.enable()
        try:
            await tab.Page.navigate(url="chrome://newtab/")
        except aiochrome.UserAbortException:
            pass

    for tab in tabs:
        if not await tab.wait(timeout=5):
            assert False, "never get here"
        await tab.stop()

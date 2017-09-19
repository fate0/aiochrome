# -*- coding: utf-8 -*-

import pytest
import asyncio
import logging
import aiochrome

logging.basicConfig(level=logging.INFO)


async def close_all_tabs(browser):
    if len(await browser.list_tab()) == 0:
        return

    logging.debug("[*] recycle")
    for tab in await browser.list_tab():
        await browser.close_tab(tab)

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 0


@pytest.mark.asyncio
async def test_normal_callmethod():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    await tab.start()
    result = await tab.Page.navigate(url="http://www.fatezero.org")
    assert result['frameId']

    await asyncio.sleep(1)
    result = await tab.Runtime.evaluate(expression="document.domain")

    assert result['result']['type'] == 'string'
    assert result['result']['value'] == 'www.fatezero.org'
    await tab.stop()


@pytest.mark.asyncio
async def test_invalid_method():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    await tab.start()
    try:
        await tab.Page.NotExistMethod()
        assert False, "never get here"
    except aiochrome.CallMethodException:
        pass
    await tab.stop()


@pytest.mark.asyncio
async def test_invalid_params():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    await tab.start()
    try:
        await tab.Page.navigate()
        assert False, "never get here"
    except aiochrome.CallMethodException:
        pass

    try:
        await tab.Page.navigate("http://www.fatezero.org")
        assert False, "never get here"
    except aiochrome.CallMethodException:
        pass

    try:
        await tab.Page.navigate(invalid_params="http://www.fatezero.org")
        assert False, "never get here"
    except aiochrome.CallMethodException:
        pass

    try:
        await tab.Page.navigate(url="http://www.fatezero.org", invalid_params=123)
    except aiochrome.CallMethodException:
        assert False, "never get here"

    await tab.stop()


@pytest.mark.asyncio
async def test_set_event_listener():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    async def request_will_be_sent(**kwargs):
        await tab.stop()

    await tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    await tab.Network.enable()

    try:
        await tab.Page.navigate(url="chrome://newtab/")
    except aiochrome.UserAbortException:
        pass

    if not await tab.wait(timeout=5):
        assert False, "never get here"


@pytest.mark.asyncio
async def test_set_wrong_listener():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    await tab.start()
    try:
        tab.Network.requestWillBeSent = "test"
        assert False, "never get here"
    except aiochrome.RuntimeException:
        pass
    await tab.stop()


@pytest.mark.asyncio
async def test_get_event_listener():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    async def request_will_be_sent(**kwargs):
        await tab.stop()

    await tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    await tab.Network.enable()
    try:
        await tab.Page.navigate(url="chrome://newtab/")
    except aiochrome.UserAbortException:
        pass

    if not await tab.wait(timeout=5):
        assert False, "never get here"

    assert tab.Network.requestWillBeSent == request_will_be_sent
    tab.Network.requestWillBeSent = None

    assert not tab.get_listener("Network.requestWillBeSent")
    # notice this
    assert tab.Network.requestWillBeSent != tab.get_listener("Network.requestWillBeSent")

    await tab.stop()


@pytest.mark.asyncio
async def test_reuse_tab_error():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    async def request_will_be_sent(**kwargs):
        await tab.stop()

    await tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    await tab.Network.enable()
    try:
        await tab.Page.navigate(url="chrome://newtab/")
    except aiochrome.UserAbortException:
        pass

    if not await tab.wait(timeout=5):
        assert False, "never get here"

    try:
        await tab.Page.navigate(url="http://www.fatezero.org")
        assert False, "never get here"
    except aiochrome.RuntimeException:
        pass
    await tab.stop()


@pytest.mark.asyncio
async def test_del_event_listener():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()
    test_list = []

    async def request_will_be_sent(**kwargs):
        test_list.append(1)
        tab.Network.requestWillBeSent = None

    await tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    await tab.Network.enable()
    await tab.Page.navigate(url="chrome://newtab/")
    await tab.Page.navigate(url="http://www.fatezero.org")

    if await tab.wait(timeout=5):
        assert False, "never get here"

    assert len(test_list) == 1
    await tab.stop()


@pytest.mark.asyncio
async def test_del_all_event_listener():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()
    test_list = []

    async def request_will_be_sent(**kwargs):
        test_list.append(1)
        tab.del_all_listeners()

    await tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    await tab.Network.enable()
    await tab.Page.navigate(url="chrome://newtab/")

    if await tab.wait(timeout=5):
        assert False, "never get here"

    assert len(test_list) == 1
    await tab.stop()


class CallableClass(object):
    def __init__(self, tab):
        self.tab = tab

    async def __call__(self, *args, **kwargs):
        await self.tab.stop()


@pytest.mark.asyncio
async def test_use_callable_class_event_listener():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    await tab.start()
    tab.Network.requestWillBeSent = CallableClass(tab)
    await tab.Network.enable()
    try:
        await tab.Page.navigate(url="chrome://newtab/")
    except aiochrome.UserAbortException:
        pass

    if not await tab.wait(timeout=5):
        assert False, "never get here"

    await tab.stop()


@pytest.mark.asyncio
async def test_status():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    assert tab.status == aiochrome.Tab.status_initial

    async def request_will_be_sent(**kwargs):
        await tab.stop()

    tab.Network.requestWillBeSent = request_will_be_sent

    assert tab.status == aiochrome.Tab.status_initial

    await tab.start()
    await tab.Network.enable()
    assert tab.status == aiochrome.Tab.status_started

    try:
        await tab.Page.navigate(url="chrome://newtab/")
    except aiochrome.UserAbortException:
        pass

    if not await tab.wait(timeout=5):
        assert False, "never get here"

    await tab.stop()
    assert tab.status == aiochrome.Tab.status_stopped


@pytest.mark.asyncio
async def test_call_method_timeout():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    await tab.start()
    await tab.Page.navigate(url="chrome://newtab/", _timeout=5)

    try:
        await tab.Page.navigate(url="http://www.fatezero.org", _timeout=0.8)
    except aiochrome.TimeoutException:
        pass

    try:
        await tab.Page.navigate(url="http://www.fatezero.org", _timeout=0.005)
    except aiochrome.TimeoutException:
        pass

    await tab.stop()


@pytest.mark.asyncio
async def test_callback_exception():
    browser = aiochrome.Browser()
    tab = await browser.new_tab()

    async def request_will_be_sent(**kwargs):
        raise Exception("test callback exception")

    await tab.start()
    tab.Network.requestWillBeSent = request_will_be_sent
    await tab.Network.enable()
    await tab.Page.navigate(url="chrome://newtab/")

    if await tab.wait(timeout=3):
        assert False, "never get here"

    await tab.stop()

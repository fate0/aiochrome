# -*- coding: utf-8 -*-

import pytest
import asyncio
import logging
import aiochrome


logging.basicConfig(level=logging.INFO)


async def close_all_tabs(browser):
    if len(await browser.list_tab()) == 0:
        return

    for tab in await browser.list_tab():
        await browser.close_tab(tab)

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 0


@pytest.mark.asyncio
async def test_chome_version():
    browser = aiochrome.Browser()
    await close_all_tabs(browser)

    browser_version = await browser.version()
    assert isinstance(browser_version, dict)


@pytest.mark.asyncio
async def test_browser_list():
    browser = aiochrome.Browser()
    await close_all_tabs(browser)

    tabs = await browser.list_tab()
    assert len(tabs) == 0


@pytest.mark.asyncio
async def test_browser_new():
    browser = aiochrome.Browser()
    await close_all_tabs(browser)

    await browser.new_tab()
    tabs = await browser.list_tab()
    assert len(tabs) == 1


@pytest.mark.asyncio
async def test_browser_activate_tab():
    browser = aiochrome.Browser()
    await close_all_tabs(browser)

    tabs = []
    for i in range(10):
        tabs.append(await browser.new_tab())

    for tab in tabs:
        await browser.activate_tab(tab)


@pytest.mark.asyncio
async def test_browser_tabs_map():
    browser = aiochrome.Browser()
    await close_all_tabs(browser)

    tab = await browser.new_tab()
    assert tab in await browser.list_tab()

    await browser.close_tab(tab)
    assert tab not in await browser.list_tab()


@pytest.mark.asyncio
async def test_browser_new_10_tabs():
    browser = aiochrome.Browser()
    tabs = []
    for i in range(10):
        tabs.append(await browser.new_tab())

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 10

    for tab in tabs:
        await browser.close_tab(tab.id)

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 0


@pytest.mark.asyncio
async def test_browser_new_100_tabs():
    browser = aiochrome.Browser()
    tabs = []
    for i in range(100):
        tabs.append(await browser.new_tab())

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 100

    for tab in tabs:
        await browser.close_tab(tab)

    await asyncio.sleep(1)
    assert len(await browser.list_tab()) == 0

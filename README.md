# aiochrome

[![Build Status](https://travis-ci.org/fate0/aiochrome.svg?branch=master)](https://travis-ci.org/fate0/aiochrome)
[![Codecov](https://img.shields.io/codecov/c/github/fate0/aiochrome.svg)](https://codecov.io/gh/fate0/aiochrome)
[![Updates](https://pyup.io/repos/github/fate0/aiochrome/shield.svg)](https://pyup.io/repos/github/fate0/aiochrome/)
[![PyPI](https://img.shields.io/pypi/v/aiochrome.svg)](https://pypi.python.org/pypi/aiochrome)
[![PyPI](https://img.shields.io/pypi/pyversions/aiochrome.svg)](https://github.com/fate0/aiochrome)

A Python Package for the Google Chrome Dev Protocol, [more document](https://fate0.github.io/aiochrome/)

## Table of Contents

* [Installation](#installation)
* [Setup Chrome](#setup-chrome)
* [Getting Started](#getting-started)
* [Tab management](#tab-management)
* [Debug](#debug)
* [Examples](#examples)
* [Ref](#ref)


## Installation

To install aiochrome, simply:

```
$ pip install -U aiochrome
```

or from GitHub:

```
$ pip install -U git+https://github.com/fate0/aiochrome.git
```

or from source:

```
$ python setup.py install
```

## Setup Chrome

simply:

```
$ google-chrome --remote-debugging-port=9222
```

or headless mode (chrome version >= 59):

```
$ google-chrome --headless --disable-gpu --remote-debugging-port=9222
```

or use docker:

```
$ docker pull fate0/headless-chrome
$ docker run -it --rm --cap-add=SYS_ADMIN -p9222:9222 fate0/headless-chrome
```

## Getting Started

``` python
import asyncio
import aiochrome


async def main():
    # create a browser instance
    browser = aiochrome.Browser(url="http://127.0.0.1:9222")

    # create a tab
    tab = await browser.new_tab()

    # register callback if you want
    async def request_will_be_sent(**kwargs):
        print("loading: %s" % kwargs.get('request').get('url'))

    tab.Network.requestWillBeSent = request_will_be_sent

    # start the tab
    await tab.start()

    # call method
    await tab.Network.enable()
    # call method with timeout
    await tab.Page.navigate(url="https://github.com/fate0/aiochrome", _timeout=5)

    # wait for loading
    await tab.wait(5)

    # stop the tab (stop handle events and stop recv message from chrome)
    await tab.stop()

    # close tab
    await browser.close_tab(tab)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()
```

or (alternate syntax)

``` python
import asyncio
import aiochrome


async def main():
    browser = aiochrome.Browser(url="http://127.0.0.1:9222")
    tab = await browser.new_tab()

    async def request_will_be_sent(**kwargs):
        print("loading: %s" % kwargs.get('request').get('url'))

    tab.set_listener("Network.requestWillBeSent", request_will_be_sent)

    await tab.start()
    await tab.call_method("Network.enable")
    await tab.call_method("Page.navigate", url="https://github.com/fate0/aiochrome", _timeout=5)

    await tab.wait(5)
    await tab.stop()

    await browser.close_tab(tab)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()

```

more methods or events could be found in
[Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/tot/)


## Debug

set DEBUG env variable:

![aiochrome_with_debug_env](https://raw.githubusercontent.com/fate0/aiochrome/master/docs/images/aiochrome_with_debug_env.png)


## Tab management

run `aiochrome -h` for more info

example:

![aiochrome_tab_management](https://raw.githubusercontent.com/fate0/aiochrome/master/docs/images/aiochrome_tab_management.png)


## Examples

please see the [examples](http://github.com/fate0/aiochrome/blob/master/examples) directory for more examples


## Ref

* [chrome-remote-interface](https://github.com/cyrus-and/chrome-remote-interface/)
* [Chrome DevTools Protocol](https://chromedevtools.github.io/devtools-protocol/tot/)

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
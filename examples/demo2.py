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

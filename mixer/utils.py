import asyncio
import inspect

def run(*args):

    coros = list(filter(inspect.iscoroutine, args))
    future = None

    if len(coros) == 1:
        future = coros[0]
    elif len(coros) > 1:
        future = asyncio.gather(*coros)

    if future:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

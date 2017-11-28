'''
sec (2) the skeleton of webapp

'''

import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime

from aiohttp import web

def index(request):
	return web.Response(body = b'<h1> Ausome</h1>')


@asyncio.coroutine
def init(loop):
	app=web.Application(loop=loop)
	#init application
	app.router.add_route('GET','/', index )
	#init router
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1', 9000)
	#init server, will not meet visit before
	logging.info('server start at address http://127.0.0.7:9000...')
	return srv

'''
	#testing
'''
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()

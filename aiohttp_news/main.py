from aiohttp import web
import asyncio
from settings import config
from routes import setup_routes
from db import pg_context
from views import getnews, on_shutdown


async def start_background_tasks(app):
    app['news_listener'] = asyncio.create_task(getnews(app))

async def cleanup_background_tasks(app):
    app['news_listener'].cancel()
    await app['news_listener']

app = web.Application()
app['config'] = config
app["sockets"] = []
app['news'] = []
app.on_startup.append(start_background_tasks)
app.on_cleanup.append(cleanup_background_tasks)
setup_routes(app)
app.cleanup_ctx.append(pg_context)
app.on_shutdown.append(on_shutdown)
web.run_app(app)




from aiohttp import web
import requests
from lxml import etree as et
import datetime as dt
import asyncio
import time
import db
import pandas as pd
from sqlalchemy import desc

async def index(request: web.Request):
    resp = web.WebSocketResponse()
    available = resp.can_prepare(request)
    if not available:
        with open('../templates/index.html', "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await resp.prepare(request)

    await resp.send_str("Welcome!!!")

    try:
        print("Someone joined.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone joined")
        request.app["sockets"].append(resp)

        async for msg in resp:

            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not resp:
                        await ws.send_str(msg.data)
            else:
                return resp
        return resp

    finally:
        request.app["sockets"].remove(resp)
        print("Someone disconnected.")
        for ws in request.app["sockets"]:
            await ws.send_str("Someone disconnected.")


async def getnews(app):
    count = 0
    while True:
        async with app['db'].acquire() as conn:
            cursor = await conn.execute(db.news.select())
            records = await cursor.fetchall()
            df = pd.DataFrame(records, columns=['id', 'author', 'title', 'description', 'pubdate'])
            df = df.astype({'id': 'int', 'author': 'str', 'title': 'str', 'description': 'str', 'pubdate': 'datetime64'})
            app['news'] = df
        count += 1
        await asyncio.sleep(5)
        r = requests.get('https://lenta.ru/rss/top7')
        print('запрос выполнен')
        data = r.content
        root = et.XML(data)
        id = 0
        news = []
        for chanel in root:
            for item in chanel:
                if item.tag == 'item':
                    news.append({})
                    news[id]['id'] = 0
                    for value in item:
                        if value.tag == 'author':
                            news[id][value.tag] = value.text
                        if value.tag == 'title':
                            news[id][value.tag] = value.text
                        if value.tag == 'description':
                            news[id][value.tag] = value.text.strip()
                        if value.tag == 'pubDate':
                            publicdate = dt.datetime.strptime(value.text, '%a, %d %b %Y %H:%M:%S %z')
                            news[id][(value.tag).lower()] = dt.datetime.combine(publicdate.date(), publicdate.time())
                    id += 1
        base_id = df['id'].to_list()[-1]
        for new in news:
            if new['title'] in df['title'].to_list():
                continue
            else:
                base_id += 1
                new['id'] = base_id
                async with app['db'].acquire() as conn:
                    cursor = await conn.execute(db.news.insert(), [new])
        async with app['db'].acquire() as conn:
            cursor = await conn.execute(db.news.select().order_by(desc('pubdate')).limit(5))
            records = await cursor.fetchall()
            msg = [dict(q) for q in records]
            str_send = ''
            for m in msg:
                str_send += m['pubdate'].strftime('%d.%m.%Y %H:%M') + ' ' + m['author'] + '<br/>'\
                            + m['title'] + '<br/>' + '<br/>'\
                            + m['description'] + '<br/>' + '<br/>'
            #print(str_send)
            for ws in app['sockets']:
                await ws.send_str(str_send)

async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()










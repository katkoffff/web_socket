import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, Text,
    Integer, String, Date
    )

__all__ = ['news', 'pg_context']

meta = MetaData()
news = Table(
    'news', meta,

    Column('id', Integer, primary_key=True),
    Column('author', String(200), nullable=False),
    Column('title', String(200), nullable=False),
    Column('description', Text, nullable=False),
    Column('pubdate', Date, nullable=False)
    )

async def pg_context(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        )
    app['db'] = engine
    yield
    app['db'].close()
    await app['db'].wait_closed()

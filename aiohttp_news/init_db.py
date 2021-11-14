from sqlalchemy import create_engine, MetaData
from aiohttp_news.settings import config
from aiohttp_news.db import news

DSN = "postgresql://{user}:{password}@{host}:{port}/{database}"

def create_tables(engine):
    meta = MetaData()
    meta.create_all(bind=engine, tables=[news])

def sample_data(engine):
    conn = engine.connect()
    conn.execute(news.insert(), [
    {'author': 'anymouse',
     'title': 'anymouse',
     'description': 'anymouse',
     'pub_date': '2015-12-15 17:17:49.629+02'}
    ])
    conn.close()

if __name__ == '__main__':
    db_url = DSN.format(**config['postgres'])
    engine = create_engine(db_url)
    #create_tables(engine)
    #sample_data(engine)
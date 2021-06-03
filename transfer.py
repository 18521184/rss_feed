#!/usr/bin/env python3
# This file is to transfer data from old_articles database to articles database due to missing id column
# , which is very important to the in-building search engine model

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# specify database configurations
config = {
    'host': 'localhost',
    'port': 15432,
    'user': 'mysql_longnguyen',
    'password': 'mysql_longnguyen',
    'database': 'corpus'
}
db_user = config.get('user')
db_pwd = config.get('password')
db_host = config.get('host')
db_port = config.get('port')
db_name = config.get('database')

# specify connection string
connection_str = f"mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}"

# connect to database
engine = create_engine(connection_str)
# connection = engine.connect()
db = scoped_session(sessionmaker(bind=engine))

def main():
    # Retrieve data from old database
    docs = db.execute("select * from old_articles").fetchall()
    for doc in docs:
        # old_articles structure
        # 0: id (will be renamed to hash); 1: summary; 2: title; 3: content; 4: feed_url; 5: url; 6: publish_date
        hash = doc[0]
        summary = doc[1]
        title = doc[2]
        content = doc[3]
        feed_url = doc[4]
        url = doc[5]
        publish_date = doc[6]

        # Insert data into new database
        db.execute(
            "INSERT INTO articles (hash, summary, title, content, feed_url, url, publish_date) VALUES (:hash, :summary, :title, :content, :feed_url, :url, :publish_date)",
            {
                "hash": hash,
                "summary": str(summary),
                "title": title,
                "content": content,
                "feed_url": feed_url,
                "url": url,
                "publish_date": publish_date
            }
        )
        
    db.commit()

if __name__ == '__main__':
    main()

# New database structure
# 0: id; 1: hash; 2: summary; 3: title; 4: content; 5: feed_url; 6: url; 7: publish_date

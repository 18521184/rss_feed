from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def create_connector():
    # specify database configurations
    config = {
        'host': 'localhost',
        'port': 3306,
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
    db = scoped_session(sessionmaker(bind=engine))

    return db

def add(db, data, feed_url):
    # Count number of articles in this RSS feed
    n_articles = len(data['articles'])
    
    count = 0
    # Convert and import articles as CSV entries into CSV file 
    for j in range(n_articles):
        hash = data['articles'][j]['hash']
        summary = data['articles'][j]['summary']
        title = data['articles'][j]['title'],
        content = data['articles'][j]['content'],
        url = data['articles'][j]['url'],         # Article URL
        publish_date = data['articles'][j]['publish_date']

        check = db.execute("SELECT hash FROM articles WHERE hash = :hash",
                {"hash": hash}).fetchone()
        try:        
            # If the article haven't existed
            if not check:
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
                count += 1
        except Exception as err:
            print(err)
    
    db.commit()
    print("[+] Added: {} articles".format(count))
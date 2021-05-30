from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

def establish():
    # specify database configurations
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'mysql_longnguyen',
        'password': 'mysql_longnguyen',
        'database': 'covid19'
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

    return db

def add(db, data, feed_url):
    # Count number of articles in this RSS feed
    n_articles = len(data['articles'])
    
    # Convert and import articles as CSV entries into CSV file 
    for j in range(n_articles):
        id = data['articles'][j]['id']
        summary = data['articles'][j]['summary']
        title = data['articles'][j]['title'],
        content = data['articles'][j]['content'],
        url = data['articles'][j]['url'],         # Article URL
        publish_date = data['articles'][j]['publish_date']

        check = db.execute("SELECT * FROM articles WHERE id = :id",
                {"id": id}).fetchone()
        try:        
            # If the article haven't existed
            if not check:
                db.execute(
                    "INSERT INTO articles (id, summary, title, content, feed_url, url, publish_date) VALUES (:id, :summary, :title, :content, :feed_url, :url, :publish_date)",
                    {
                        "id": id,
                        "summary": str(summary),
                        "title": title,
                        "content": content,
                        "feed_url": feed_url,
                        "url": url,
                        "publish_date": publish_date
                    }
                )
        except Exception as err:
            print(data['articles'][j]['summary'])
            print(err)
    
    db.commit()
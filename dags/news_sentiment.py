from airflow import DAG # type: ignore
from airflow.operators.python import PythonOperator # type: ignore
from datetime import datetime
import requests
import psycopg2
from psycopg2.extras import execute_values
from textblob import TextBlob
from dotenv import load_dotenv
import os

# Environment variables
load_dotenv()
POSTGRES_NAME= os.getenv("DATABASE_NAME")
POSTGRES_USER= os.getenv("DATABASE_USER")
POSTGRES_PASS= os.getenv("DATABASE_PASSWORD")
API_KEY= os.getenv("API_KEY")

# Base NYT URL for technology section
BASE_URL = 'https://api.nytimes.com/svc/topstories/v2/technology.json'

# Fetch news articles
def fetch_news(**kwargs):
    params = {'api-key': API_KEY}
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        articles = response.json().get('results', [])[:kwargs['page_size']]
        return [
            {
                'title': article.get('title', ''),
                'abstract': article.get('abstract', ''),
                'url': article.get('url', ''),
                'source': 'New York Times',
                'published_at': article.get('published_date', None),
                'section': article.get('section', ''),
                'subsection': article.get('subsection', ''),
                'geo_facet': ', '.join(article.get('geo_facet', []))
            }
            for article in articles if article.get('title') and article.get('abstract')
        ]
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

# Connect to PostgreSQL
def connect_db():
    return psycopg2.connect(
        dbname=POSTGRES_NAME,
        user=POSTGRES_USER,
        password=POSTGRES_PASS,
        host="host.docker.internal",
        port="5432"
    ) 

# Create tables if they don't exist
def create_tables():
    conn = connect_db()
    queries = [
        """
        CREATE TABLE IF NOT EXISTS news_articles (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            url TEXT NOT NULL,
            source TEXT,
            published_at TIMESTAMP,
            section TEXT,
            subsection TEXT,
            geo_facet TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (title, published_at)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            abstract TEXT,
            url TEXT NOT NULL,
            source TEXT,
            published_at TIMESTAMP,
            section TEXT,
            subsection TEXT,
            geo_facet TEXT,
            sentiment_score FLOAT,
            sentiment_label TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (title, published_at)
        );
        """
    ]
    try:
        with conn.cursor() as cur:
            for query in queries:
                cur.execute(query)
            conn.commit()
    finally:
        conn.close()

# Insert articles into the database
def insert_articles(**kwargs):
    articles = kwargs['ti'].xcom_pull(task_ids='fetch_news')
    conn = connect_db()
    query = """
    INSERT INTO news_articles (title, abstract, url, source, published_at, section, subsection, geo_facet)
    VALUES %s
    ON CONFLICT (title, published_at) DO NOTHING;
    """
    values = [
        (
            article['title'],
            article['abstract'],
            article['url'],
            article['source'],
            article['published_at'],
            article['section'],
            article['subsection'],
            article['geo_facet']
        )
        for article in articles
    ]
    try:
        with conn.cursor() as cur:
            execute_values(cur, query, values)
            conn.commit()
    finally:
        conn.close()

def preprocess_text(text):
    text = text.lower()
    text = ''.join(char for char in text if char.isalnum() or char.isspace())
    text = ' '.join(text.split())
    return text

# Analyze sentiment and insert sentiment data
def analyze_and_insert_sentiment():
    conn = connect_db()
    try:
        # Fetch articles
        query = """
        SELECT title, abstract, url, source, published_at, section, subsection, geo_facet
        FROM news_articles;
        """
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

        # Analyze sentiment
        articles = [
            {
                'title': row[0],
                'abstract': row[1],
                'url': row[2],
                'source': row[3],
                'published_at': row[4],
                'section': row[5],
                'subsection': row[6],
                'geo_facet': row[7],
                'sentiment_score': TextBlob(preprocess_text(row[1])).sentiment.polarity,
                'sentiment_label': (
                    'positive' if TextBlob(row[1]).sentiment.polarity > 0 else
                    'negative' if TextBlob(row[1]).sentiment.polarity < 0 else 'neutral'
                )
            }
            for row in rows
        ]

        # Insert sentiment data
        query = """
        INSERT INTO news_sentiment (title, abstract, url, source, published_at, section, subsection, geo_facet, sentiment_score, sentiment_label)
        VALUES %s
        ON CONFLICT (title, published_at) DO NOTHING;
        """
        values = [
            (
                article['title'],
                article['abstract'],
                article['url'],
                article['source'],
                article['published_at'],
                article['section'],
                article['subsection'],
                article['geo_facet'],
                article['sentiment_score'],
                article['sentiment_label']
            )
            for article in articles
        ]
        with conn.cursor() as cur:
            execute_values(cur, query, values)
            conn.commit()
    finally:
        conn.close()

# Define the DAG
default_args = {"retries": 1}
with DAG(
    dag_id="nyt_news_sentiment",
    default_args=default_args,
    description="Fetch news from NYT, analyze sentiment, and store in PostgreSQL",
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:
    create_tables_task = PythonOperator(
        task_id="create_tables",
        python_callable=create_tables
    )

    fetch_news_task = PythonOperator(
        task_id="fetch_news",
        python_callable=fetch_news,
        op_kwargs={"page_size": 5}
    )

    insert_articles_task = PythonOperator(
        task_id="insert_articles",
        python_callable=insert_articles,
        provide_context=True
    )

    analyze_and_insert_sentiment_task = PythonOperator(
        task_id="analyze_and_insert_sentiment",
        python_callable=analyze_and_insert_sentiment
    )

    create_tables_task >> fetch_news_task >> insert_articles_task >> analyze_and_insert_sentiment_task

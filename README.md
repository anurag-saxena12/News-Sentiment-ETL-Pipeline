# News-Sentiment-ETL-Pipeline

## Project Overview: News Sentiment ETL Pipeline

The **News Sentiment ETL Pipeline** is a data engineering project designed to automate the extraction, sentiment analysis, and storage of news article data. Using **Apache Airflow**, the pipeline orchestrates the collection of news data, applies sentiment analysis leveraging **TextBlob**, and stores the results in a **PostgreSQL** database. The project runs inside **Docker** containers for easy deployment and scalability, with the exception of the database, which runs separately to ensure efficient data management. The analyzed sentiment data can be visualized using **Grafana**, allowing users to track sentiment trends over time. This project highlights essential data engineering concepts such as **workflow orchestration**, **containerization**, **automated data ingestion**, and **visualization**, making it a practical demonstration of building efficient ETL workflows with minimal infrastructure costs.


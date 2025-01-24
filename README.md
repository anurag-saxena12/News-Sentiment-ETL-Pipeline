# News-Sentiment-ETL-Pipeline

## Project Overview: News Sentiment ETL Pipeline

The **News Sentiment ETL Pipeline** is a data engineering project designed to automate the extraction, sentiment analysis, and storage of news article data. Using **Apache Airflow**, the pipeline orchestrates the collection of news data, applies sentiment analysis leveraging **TextBlob**, and stores the results in a **PostgreSQL** database. The project runs inside **Docker** containers for easy deployment and scalability, with the exception of the database, which runs separately to ensure efficient data management. The analyzed sentiment data can be visualized using **Grafana**, allowing users to track sentiment trends over time. This project highlights essential data engineering concepts such as **workflow orchestration**, **containerization**, **automated data ingestion**, and **visualization**, making it a practical demonstration of building efficient ETL workflows with minimal infrastructure costs.

## Architecture Diagram

![Project Architecture](assets/nyt_sentiment_architecture_diagram.png)

## Prerequisites

Ensure the following are installed on your local machine before proceeding:

1. **PostgreSQL** (version 12 or higher)
   - Download from [PostgreSQL official site](https://www.postgresql.org/download/)
   - Ensure the PostgreSQL service is running and accessible.
   
2. **Docker & Docker Compose**
   - Install Docker: [Get Docker](https://docs.docker.com/get-docker/)
   - Install Docker Compose: [Get Docker Compose](https://docs.docker.com/compose/install/)
   
3. **Python 3.8+** (optional, for local development)
   - Install from [Python official site](https://www.python.org/downloads/)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/News-Sentiment-ETL-Pipeline.git
   cd News-Sentiment-ETL-Pipeline

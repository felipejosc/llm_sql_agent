# llm_sql_agent

AI powered SQL exploration agent that translates natural language questions into PostgreSQL queries using LangChain, Groq and Streamlit.
# AI SQL Exploration Agent

AI SQL Exploration Agent is a natural language interface for exploring PostgreSQL databases.

The project allows users to ask business questions in plain English and receive structured SQL based answers through a Streamlit interface. It uses LangChain tools, custom agent logic and Groq's Qwen 32B model to interpret requests, generate queries and interact with the database safely.

This project was built to make data exploration faster, more accessible and less dependent on manual SQL writing.

## What it demonstrates

Data engineering and backend development  
Natural language to SQL workflows  
PostgreSQL database integration  
LLM powered agent design  
Streamlit application development  
Environment based configuration and credential protection  

## Tech Stack

Python 3.10  
PostgreSQL  
LangChain Tools  
Groq API  
Qwen 32B  
Streamlit  

## Running Locally

## Running Locally

Create a virtual environment:

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Tech Stack

Python 3.10  
PostgreSQL  
LangChain  
Groq API  
Streamlit  

## Security

Credentials are managed with environment variables and protected with `.gitignore`.

# llm_sql_agent

AI-powered SQL exploration agent using PostgreSQL, LangChain Tools and Streamlit

**Project Structure:**
- `agent_core/`
  - `agent.py`
  - `tools.py`
  - `config.py`
  - `log_utils.py`
  - `__init__.py`
- `app.py`
- `requirements.txt`
- `.gitignore`
- `README.md`

**Running Locally:**
Create a virtual environment:
python -m venv venv

Activate:
(Windows) 
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Configure .env:
GROQ_API_KEY=xxxx
DB_NAME=xxxx
DB_USER=xxxx
DB_PASSWORD=xxxx
DB_HOST=localhost
DB_PORT=5432

Run:
Streamlit run app.py
=====================================
 Area       Technology
  
 Agent       LangChain Tools + Custom Logic     
 LLM         Qwen 32B (Groq API)                
 Backend     Python 3.10+                       
 DB          PostgreSQL                         
 UI          Streamlit                          
 Security   .gitignore + environment variables 

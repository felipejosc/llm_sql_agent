from functools import wraps
import psycopg2
from psycopg2.extras import RealDictCursor
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from agent_core.log_utils import log_panel
from agent_core.config import Config



def with_sql_cursor(func):
    """Abre conexão + cursor automaticamente e injeta como 1º argumento."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(
                dbname=Config.DB_NAME,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                cursor_factory=RealDictCursor,
            )

            # Evita crash de encoding
            conn.set_client_encoding("LATIN1")

            cur = conn.cursor()
            result = func(cur, *args, **kwargs)
            conn.commit()
            return result

        except Exception as e:
            log_panel("Erro SQL", repr(e))
            raise e

        finally:
            try:
                if cur:
                    cur.close()
                if conn:
                    conn.close()
            except:
                pass

    return wrapper



# FUNÇÕES SQL BASE (COM cur como primeiro parâmetro)
@with_sql_cursor
def _list_tables_impl(cur):
    """Retorna a lista de todas as tabelas do esquema público."""
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name
    """)
    return [row["table_name"] for row in cur.fetchall()]


@with_sql_cursor
def _describe_table_impl(cur, table: str):
    """Descreve as colunas e tipos de uma tabela."""
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name=%s AND table_schema='public'
        ORDER BY ordinal_position
    """, (table,))
    return cur.fetchall()


@with_sql_cursor
def _sample_rows_impl(cur, table: str, limit: int = 5):
    """Retorna uma amostra de linhas de qualquer tabela."""
    from psycopg2 import sql
    
    # Valida que a tabela existe
    cur.execute("""
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='public' AND table_name=%s
    """, (table,))
    
    if not cur.fetchone():
        return [{"erro": f"Tabela '{table}' não encontrada"}]
    
    # Query segura
    query = sql.SQL("SELECT * FROM {} LIMIT %s").format(sql.Identifier(table))
    cur.execute(query, (min(limit, 100),))
    return cur.fetchall()


@with_sql_cursor
def _execute_sql_impl(cur, query: str):
    """Executa SQL arbitrário e retorna resultados seguros."""
    query = query.strip().rstrip(';')
    cur.execute(query)

    try:
        rows = cur.fetchall()

        # Sanitização para evitar erros de encoding
        def clean_value(v):
            if isinstance(v, bytes):
                return v.decode("latin1", "replace")
            if isinstance(v, str):
                return v.encode("utf-8", "replace").decode("utf-8", "replace")
            return v

        return [
            {k: clean_value(v) for k, v in row.items()}
            for row in rows
        ]

    except psycopg2.ProgrammingError:
        # Query não retorna dados (INSERT, UPDATE, etc)
        return [{"status": "Comando executado com sucesso", "rows_affected": cur.rowcount}]



# WRAPPERS SEM O PARÂMETRO 'cur' (para o LangChain)
def list_tables_wrapper():
    """Wrapper sem parâmetros para list_tables"""
    return _list_tables_impl()


def describe_table_wrapper(table: str):
    """Wrapper que recebe apenas 'table'"""
    return _describe_table_impl(table)


def sample_rows_wrapper(table: str, limit: int = 5):
    """Wrapper que recebe apenas 'table' e 'limit'"""
    return _sample_rows_impl(table, limit)


def execute_sql_wrapper(query: str):
    """Wrapper que recebe apenas 'query'"""
    return _execute_sql_impl(query)



class DescribeTableInput(BaseModel):
    table: str = Field(description="Nome da tabela a ser descrita")


class SampleRowsInput(BaseModel):
    table: str = Field(description="Nome da tabela")
    limit: int = Field(default=5, description="Número de linhas a retornar (máximo 100)")


class ExecuteSQLInput(BaseModel):
    query: str = Field(description="Query SQL a ser executada")



def get_available_tools():
    """Retorna todas as ferramentas SQL disponíveis."""

    list_tables_tool = StructuredTool.from_function(
        func=list_tables_wrapper,  
        description="Lista todas as tabelas disponíveis no esquema público do PostgreSQL."
    )

    describe_table_tool = StructuredTool.from_function(
        func=describe_table_wrapper,  
        name="describe_table",
        description="Descreve as colunas, tipos de dados e propriedades de uma tabela específica.",
        args_schema=DescribeTableInput,
    )

    sample_rows_tool = StructuredTool.from_function(
        func=sample_rows_wrapper,  
        name="sample_rows",
        description="Retorna uma amostra de registros de uma tabela para visualização.",
        args_schema=SampleRowsInput,
    )

    execute_sql_tool = StructuredTool.from_function(
        func=execute_sql_wrapper,  
        name="execute_sql",
        description="Executa uma query SQL arbitrária e retorna os resultados.",
        args_schema=ExecuteSQLInput,
    )

    return [
        list_tables_tool,
        describe_table_tool,
        sample_rows_tool,
        execute_sql_tool,
    ]



from util import get_db_connection, get_sqlalchemy_url
import os
from openai import OpenAI
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, create_engine, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# Load environment variables
load_dotenv()

# Configure OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

STORED_PROC_QUERY = """
SELECT n.nspname AS schema_name,
       p.proname AS procedure_name,
       pg_catalog.pg_get_function_arguments(p.oid) AS arguments,
       t.typname AS return_type,
       pg_get_functiondef(p.oid) AS procedure_code
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
JOIN pg_type t ON p.prorettype = t.oid
WHERE p.prokind = 'p'  -- Only procedures (not functions or aggregates)
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')  -- Exclude system schemas
ORDER BY schema_name, procedure_name;
"""

TABLE_DEFINITIONS_QUERY = """
SELECT table_name, 
       string_agg(
           column_name || ' ' || data_type || 
           CASE 
               WHEN character_maximum_length IS NOT NULL 
               THEN '(' || character_maximum_length || ')'
               ELSE ''
           END ||
           CASE 
               WHEN is_nullable = 'NO' THEN ' NOT NULL'
               ELSE ''
           END,
           E'\n    ' ORDER BY ordinal_position
       ) as columns
FROM information_schema.columns
WHERE table_schema = 'public'
GROUP BY table_name;
"""

def get_table_definitions(connection):
    """Get table definitions from database"""
    with connection.cursor() as cursor:
        cursor.execute(TABLE_DEFINITIONS_QUERY)
        results = cursor.fetchall()
        
        definitions = []
        for table_name, columns in results:
            definitions.append(f"""
CREATE TABLE {table_name} (
    {columns}
);""")
        return "\n".join(definitions)

def get_translation_prompt(proc_name, arguments, proc_code, table_definitions):
    return f"""Translate this PostgreSQL stored procedure into a Python function using SQLAlchemy ORM.
Output only pure Python code without any markdown formatting, section numbers, or explanatory text.

Table Definitions:
{table_definitions}

Procedure Name: {proc_name}
Arguments: {arguments}

PostgreSQL Code:
{proc_code}

Requirements for the output:
1. Start with all necessary imports (sqlalchemy, datetime, os)
2. Define SQLAlchemy models with proper relationships and foreign keys
3. Define the main function with type hints
4. Use SQLAlchemy 2.0+ style with session-based transactions
5. Include error handling with try/except and session rollback
6. Add docstring to the main function
7. Use this exact database connection code:
    from util import get_sqlalchemy_url
    engine = create_engine(get_sqlalchemy_url())
8. Include calculation_date in provisions table with default=func.now()
9. Add proper relationships between models (one-to-many, many-to-one)
10. Output only executable Python code without any markdown or comments

Example format:
from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, create_engine, func
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from util import get_sqlalchemy_url
import os
from datetime import date

Base = declarative_base()

class ModelName(Base):
    __tablename__ = '...'
    # columns and relationships

def function_name(param: type) -> return_type:
    \"\"\"Docstring\"\"\"
    engine = create_engine(get_sqlalchemy_url())
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # logic here
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
"""

def translate_with_openai(proc_name, arguments, proc_code, table_definitions):
    """Translate a stored procedure to Python using OpenAI API"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in translating PostgreSQL procedures to SQLAlchemy Python code. Use modern practices and clear documentation."
                },
                {
                    "role": "user",
                    "content": get_translation_prompt(proc_name, arguments, proc_code, table_definitions)
                }
            ],
            model="gpt-4",
            temperature=0.2
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"# Error during translation: {str(e)}"

def save_procedure(connection, schema_name, proc_name, arguments, return_type, proc_code):
    """Save procedure details to a Python file with SQLAlchemy translation"""
    os.makedirs("translated_procedures", exist_ok=True)
    
    filename = f"translated_procedures/{schema_name}_{proc_name}.py"
    
    # Get table definitions from database
    table_definitions = get_table_definitions(connection)
    
    # Get SQLAlchemy translation
    translation = translate_with_openai(proc_name, arguments, proc_code, table_definitions)
    
    # Remove any markdown code block indicators if present
    translation = translation.replace("```python", "").replace("```", "").strip()
    
    content = f'''"""
PostgreSQL Stored Procedure: {proc_name}
Schema: {schema_name}
Arguments: {arguments}
Return Type: {return_type}

Original PostgreSQL Code:
{proc_code}
"""

{translation}
'''
    
    with open(filename, 'w') as f:
        f.write(content)
    return filename

def list_stored_procedures(connection):
    """List all stored procedures in the database and save them to files"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(STORED_PROC_QUERY)
            results = cursor.fetchall()
            
            if not results:
                print("No stored procedures found.")
                return
            
            for row in results:
                schema_name, proc_name = row[0], row[1]
                arguments, return_type = row[2], row[3]
                proc_code = row[4]
                
                filename = save_procedure(connection, schema_name, proc_name, 
                                       arguments, return_type, proc_code)
                
                print(f"\nSaved procedure to: {filename}")
                print("=" * 80)
                print(f"Schema: {schema_name}")
                print(f"Procedure: {proc_name}")
                print(f"Arguments: {arguments}")
                print(f"Return Type: {return_type}")
                print("-" * 80)
                
    except Exception as e:
        print(f"Error listing stored procedures: {e}")

def main():
    connection = None
    try:
        connection = get_db_connection()
        print("Connected to the database.")
        
        list_stored_procedures(connection)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting stored procedure analysis...")
    main()
    print("Analysis completed.")
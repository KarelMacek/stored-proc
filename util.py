import psycopg
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection configuration
DATABASE_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT")
}

def get_db_connection():
    """Create and return a database connection"""
    return psycopg.connect(
        f"dbname={DATABASE_CONFIG['dbname']} "
        f"user={DATABASE_CONFIG['user']} "
        f"password={DATABASE_CONFIG['password']} "
        f"host={DATABASE_CONFIG['host']} "
        f"port={DATABASE_CONFIG['port']}"
    )

def execute_sql_commands(commands, connection):
    """Execute a list of SQL commands within a transaction"""
    with connection.cursor() as cursor:
        for command in commands:
            cursor.execute(command)
        connection.commit()

def run_and_print_provisions(connection, agent_id):
    """Run the calculate_provisions stored procedure and print results"""
    try:
        # Call the stored procedure
        with connection.cursor() as cursor:
            cursor.execute("CALL calculate_provisions(%s)", (agent_id,))
            connection.commit()
            
            # Fetch and print the results
            cursor.execute("""
                SELECT 
                    a.name as agent_name,
                    p.policy_type,
                    p.premium_amount,
                    pr.provision_amount,
                    pr.calculation_date
                FROM provisions pr
                JOIN agents a ON pr.agent_id = a.agent_id
                JOIN policies p ON pr.policy_id = p.policy_id
                WHERE pr.agent_id = %s
                ORDER BY pr.calculation_date DESC
            """, (agent_id,))
            
            results = cursor.fetchall()
            
            print("\nProvision Calculation Results:")
            print("-" * 80)
            print(f"{'Agent':15} {'Policy Type':15} {'Premium':12} {'Provision':12} {'Date'}")
            print("-" * 80)
            
            for row in results:
                print(f"{row[0]:15} {row[1]:15} ${row[2]:10.2f} ${row[3]:10.2f} {row[4]}")
            
    except Exception as e:
        print(f"Error running provisions: {e}")

def get_sqlalchemy_url():
    """Create and return SQLAlchemy database URL from environment variables"""
    return (f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@"
            f"{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['dbname']}")

from util import get_db_connection, execute_sql_commands

# SQL statements for table creation, procedure, and sample data
CREATE_TABLES = [
    """
    CREATE TABLE IF NOT EXISTS agents (
        agent_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        region VARCHAR(50) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS policies (
        policy_id SERIAL PRIMARY KEY,
        agent_id INT NOT NULL REFERENCES agents(agent_id),
        policy_type VARCHAR(50) NOT NULL,
        premium_amount NUMERIC(12, 2) NOT NULL,
        issue_date DATE NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS commission_rates (
        policy_type VARCHAR(50) PRIMARY KEY,
        commission_rate NUMERIC(5, 2) NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS provisions (
        provision_id SERIAL PRIMARY KEY,
        agent_id INT NOT NULL REFERENCES agents(agent_id),
        policy_id INT NOT NULL REFERENCES policies(policy_id),
        provision_amount NUMERIC(12, 2) NOT NULL,
        calculation_date DATE NOT NULL DEFAULT CURRENT_DATE
    );
    """
]

CREATE_PROCEDURE = """
CREATE OR REPLACE PROCEDURE calculate_provisions(agent_id_input INT)
LANGUAGE plpgsql
AS $$
DECLARE
    policy RECORD;
    commission_rate_value NUMERIC(5, 2);
    provision_amount NUMERIC(12, 2);
BEGIN
    FOR policy IN
        SELECT * FROM policies WHERE agent_id = agent_id_input
    LOOP
        SELECT cr.commission_rate
        INTO commission_rate_value
        FROM commission_rates cr
        WHERE cr.policy_type = policy.policy_type;

        provision_amount := policy.premium_amount * (commission_rate_value / 100);

        INSERT INTO provisions (agent_id, policy_id, provision_amount)
        VALUES (policy.agent_id, policy.policy_id, provision_amount);
    END LOOP;
END;
$$;
"""

INSERT_SAMPLE_DATA = [
    # Sample agents
    """
    INSERT INTO agents (name, region) VALUES 
    ('Alice', 'North'),
    ('Bob', 'South')
    ON CONFLICT DO NOTHING;
    """,
    # Sample policies
    """
    INSERT INTO policies (agent_id, policy_type, premium_amount, issue_date) VALUES 
    (1, 'Health', 1000.00, '2024-01-01'),
    (1, 'Life', 1500.00, '2024-02-01'),
    (2, 'Health', 2000.00, '2024-01-15')
    ON CONFLICT DO NOTHING;
    """,
    # Sample commission rates
    """
    INSERT INTO commission_rates (policy_type, commission_rate) VALUES 
    ('Health', 10.0),
    ('Life', 12.0)
    ON CONFLICT (policy_type) DO NOTHING;
    """
]

def main():
    connection = None
    try:
        connection = get_db_connection()
        print("Connected to the database.")
        
        print("Creating tables...")
        execute_sql_commands(CREATE_TABLES, connection)
        
        print("Creating stored procedure...")
        execute_sql_commands([CREATE_PROCEDURE], connection)
        
        print("Inserting sample data...")
        execute_sql_commands(INSERT_SAMPLE_DATA, connection)
        
        print("Database setup completed successfully.")
    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed.")

if __name__ == "__main__":
    print("Starting database setup...")
    main()
    print("Setup completed.")

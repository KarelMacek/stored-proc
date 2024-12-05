# Stored Procedure to SQLAlchemy Converter 🔄

An experimental demonstration of converting PostgreSQL stored procedures to SQLAlchemy ORM code using OpenAI's GPT-4 API 🤖

## Overview 📝

This project showcases how traditional PostgreSQL stored procedures can be automatically translated into modern Python code using SQLAlchemy ORM. It serves as a proof of concept for modernizing database operations.

## Features ✨

- 🔄 Automatic translation of PostgreSQL procedures to SQLAlchemy code
- 🏗️ Generation of SQLAlchemy models with proper relationships
- 🧪 Test utilities for both stored procedures and generated code
- 📝 Maintains original procedure documentation

## How does it work? 🤔

The project uses OpenAI's GPT-4 API to translate the stored procedures to Python code. The translation is based on a set of instructions that are provided to the GPT-4 API.

Original stored procedure:

```sql
CREATE OR REPLACE PROCEDURE public.calculate_provisions(IN agent_id_input integer)
 LANGUAGE plpgsql
AS $procedure$
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
$procedure$
```
	
Generated SQLAlchemy code:

```python
def calculate_provisions(agent_id_input: int) -> None:
    """Calculate provisions for a given agent"""
    engine = create_engine(get_sqlalchemy_url())
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        policies = session.query(Policy).filter(Policy.agent_id == agent_id_input).all()
        for policy in policies:
            commission_rate_value = session.query(CommissionRate.commission_rate).filter(
                CommissionRate.policy_type == policy.policy_type).scalar()
            provision_amount = policy.premium_amount * (commission_rate_value / 100)
            provision = Provision(agent_id=policy.agent_id, policy_id=policy.policy_id, provision_amount=provision_amount)
            session.add(provision)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
```
Some parts are not shown here, for the full code, see [the complete example](translated_procedures/public_calculate_provisions_EXAMPLE.py)


## Setup 🚀

1. Ensure you have a PostgreSQL running and a PostgreSQL client installed on your machine:

It depends on your preferrences, there are many ways to run PostgreSQL, for example:
- Docker
- Local installation
- Cloud service

For a local client, it depends on your OS, for example:
- Windows: install PostgreSQL client from [here](https://www.postgresql.org/download/windows/)
- Linux: install PostgreSQL client from package manager, for example `sudo apt-get install postgresql-client`
- MacOS: install PostgreSQL client from [here](https://www.postgresql.org/download/macosx/)

2. Configure environment variables in `.env`:
Copy `.env.example` to `.env` and set the values for your PostgreSQL database and OpenAI API key.

```env
DB_NAME=your_db_name
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=your_windows_ip
DB_PORT=5432
OPENAI_API_KEY=your_api_key
```


3. Install Python dependencies:

Set up a virtual environment and install the dependencies:

```bash
pip install -r requirements.txt
```

## Usage 💻

1. Create test database and tables:

```bash
python 01_create_dummy.py
```

2. Test original stored procedure:

```bash
python 02_test_stored_proc.py
```

3. Generate SQLAlchemy code:

```bash
python 03_translate_stored_procedures.py
```

4. Test generated SQLAlchemy code:

```bash
python 04_test_sqlalchemy.py
```
## Future Developments 🔮

### Modern Alternatives 🚀

While this project focuses on converting stored procedures to SQLAlchemy, there are several modern alternatives for implementing business logic that traditionally lived in stored procedures:

- [ ] **Apache Spark**: For large-scale data processing and transformations
- [ ] **Apache Airflow**: For complex workflow orchestration and scheduling
- [ ] **AWS Lambda**: For serverless, event-driven computations
- [ ] **FastAPI**: For building high-performance APIs with Python
- [ ] **dbt (data build tool)**: For data transformation workflows
- [ ] **Prefect**: For modern dataflow automation

Each has its own strengths and use cases, and the choice depends on your specific requirements.

### AI Model Considerations 🤖

Currently, this project uses OpenAI's GPT-4, which is a general-purpose language model. Future improvements could explore:

- [ ] Specialized database-focused LLMs
- [ ] Fine-tuned models for SQL-to-ORM translation
- [ ] Open-source alternatives (like CodeLlama)
- [ ] Domain-specific models for financial calculations
- [ ] Self-hosted models for data privacy

### Validation 🧪

The project could benefit from automated comparison testing:
- [ ] Input validation between procedures and generated code
- [ ] Output comparison for identical datasets
- [ ] Performance benchmarking
- [ ] Edge case handling verification
- [ ] SQL query plan analysis

### Other Areas for Improvement 🔨

- [ ] Support for more complex stored procedures
- [ ] Better handling of database-specific functions
- [ ] Transaction management improvements
- [ ] Enhanced error handling in generated code
- [ ] Support for more PostgreSQL-specific types
- [ ] Test coverage for generated code
- [ ] Documentation generation
- [ ] CI/CD pipeline setup

## Project Structure 📁

```plaintext
.
├── 01_create_dummy.py         # Creates test database and tables
├── 02_test_stored_proc.py     # Tests original stored procedure
├── 03_translate_stored_procedures.py  # Main translation script
├── 04_test_sqlalchemy.py      # Tests generated SQLAlchemy code
├── util.py                    # Utility functions
├── requirements.txt           # Python dependencies
└── translated_procedures/     # Generated SQLAlchemy code
```

## Contributing 🤝

This is an experimental demonstration. Feel free to fork and experiment with your own improvements!

## License 📄

MIT

## Note ℹ️

This is a demonstration project and should not be used in production without proper testing and validation. The generated code should be reviewed and adjusted as needed.
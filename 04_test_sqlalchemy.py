from translated_procedures.public_calculate_provisions import (
    Agent, Policy, CommissionRate, Provision, calculate_provisions, Base
)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv
from datetime import date

# Load environment variables
load_dotenv()

# Create database URL from config
db_url = (f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
          f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

# Create engine and tables
engine = create_engine(db_url)

def test_calculate_provisions():
    """Test the SQLAlchemy version of calculate_provisions"""
    try:
        # Create a session
        with Session(engine) as session:
            # Get agent IDs from database
            agent_ids = session.query(Agent.agent_id).all()
            
            print("\nTesting SQLAlchemy calculate_provisions:")
            print("-" * 80)
            
            for (agent_id,) in agent_ids:
                print(f"\nCalculating provisions for Agent ID: {agent_id}")
                
                # Calculate provisions
                calculate_provisions(agent_id)
                
                # Query and print results
                results = (
                    session.query(
                        Agent.name,
                        Policy.policy_type,
                        Policy.premium_amount,
                        Provision.provision_amount,
                        Provision.calculation_date
                    )
                    .join(Provision, Agent.agent_id == Provision.agent_id)
                    .join(Policy, Provision.policy_id == Policy.policy_id)
                    .filter(Agent.agent_id == agent_id)
                    .order_by(Provision.calculation_date.desc())
                    .all()
                )
                
                print(f"{'Agent':15} {'Policy Type':15} {'Premium':12} {'Provision':12} {'Date'}")
                print("-" * 80)
                for row in results:
                    print(f"{row[0]:15} {row[1]:15} ${row[2]:10.2f} ${row[3]:10.2f} {row[4]}")

    except Exception as e:
        print(f"Error testing provisions: {e}")

if __name__ == "__main__":
    print("Starting SQLAlchemy provision calculations...")
    test_calculate_provisions()
    print("\nCalculations completed.")

"""
PostgreSQL Stored Procedure: calculate_provisions
Schema: public
Arguments: IN agent_id_input integer
Return Type: void

Original PostgreSQL Code:
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

"""

from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey, create_engine, func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm.declarative import declarative_base
from util import get_sqlalchemy_url
import os

Base = declarative_base()

class Agent(Base):
    __tablename__ = 'agents'
    agent_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    region = Column(String(50), nullable=False)
    policies = relationship('Policy', back_populates='agent')

class CommissionRate(Base):
    __tablename__ = 'commission_rates'
    policy_type = Column(String(50), primary_key=True)
    commission_rate = Column(Numeric, nullable=False)

class Policy(Base):
    __tablename__ = 'policies'
    policy_id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'), nullable=False)
    policy_type = Column(String(50), nullable=False)
    premium_amount = Column(Numeric, nullable=False)
    issue_date = Column(Date, nullable=False)
    agent = relationship('Agent', back_populates='policies')
    provisions = relationship('Provision', back_populates='policy')

class Provision(Base):
    __tablename__ = 'provisions'
    provision_id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey('agents.agent_id'), nullable=False)
    policy_id = Column(Integer, ForeignKey('policies.policy_id'), nullable=False)
    provision_amount = Column(Numeric, nullable=False)
    calculation_date = Column(Date, default=func.now())
    policy = relationship('Policy', back_populates='provisions')

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

import sys

from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

from config import MissingConfigError, get_engine


try:
    engine = get_engine()
except MissingConfigError:
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None
Base = declarative_base()


class BusinessUnit(Base):
    __tablename__ = "business_units"
    id = Column(Integer, primary_key=True, index=True)
    office_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=True) 
    longitude = Column(Float, nullable=True)

class Manager(Base):
    __tablename__ = "managers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False) # Спец, Ведущий спец, Глав спец
    skills = Column(String, nullable=False) 
    unit_name = Column(String, nullable=False) 
    current_load = Column(Integer, default=0)

class Ticket(Base):
    __tablename__ = "tickets"
    id = Column(Integer, primary_key=True, index=True)
    client_guid = Column(String, nullable=False)
    gender = Column(String)
    birth_date = Column(String)
    segment = Column(String) 
    description = Column(Text)
    attachment = Column(String)
    country = Column(String)
    region = Column(String)
    city = Column(String)
    street = Column(String)
    building = Column(String)
    
class RoutingResult(Base):
    __tablename__ = "routing_results"
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, unique=True, index=True)
    assigned_manager_id = Column(Integer, ForeignKey("managers.id"), nullable=False)

    ai_type = Column(String)
    ai_sentiment = Column(String)
    ai_priority = Column(Integer)
    ai_language = Column(String)
    ai_summary = Column(Text)



def init_db(reset: bool = False):
    db_engine = get_engine()
    if reset:
        print("Dropping old tables...")
        Base.metadata.drop_all(bind=db_engine)
    print("Creating database tables...")
    Base.metadata.create_all(bind=db_engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    try:
        init_db(reset="--reset" in sys.argv)
    except MissingConfigError as exc:
        raise SystemExit(str(exc)) from exc

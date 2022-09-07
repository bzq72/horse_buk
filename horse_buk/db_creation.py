""" Constains ORM's Classes which were used for creation DB """

import sqlalchemy as sql
from sqlalchemy import text, ForeignKey, MetaData, Integer, String, Float, Column
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Enterprise DB to be used
DRIVER = "ODBC Driver 17 for SQL Server"
SERVERNAME = "DESKTOP-1SHBR4M"
INSTANCENAME = "\SQLEXPRESS"
DB = "horse_buk_db"

engine = sql.create_engine(f"mssql+pyodbc://@{SERVERNAME}{INSTANCENAME}/{DB}?driver={DRIVER}", pool_size=50)
con = engine.connect()
metadata_obj = MetaData()
Base = declarative_base()

    
class Jockeys(Base):
    __tablename__ = 'Jockeys'
    ID = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    race_place = relationship('Race_places', back_populates = "jockey")

class Trainers(Base):
    __tablename__ = 'Trainers'
    ID = Column(Integer, primary_key=True) 
    name = Column(String(30), nullable=False)
    surname = Column(String(30), nullable=False)   
    horses = relationship('Horses', back_populates = "trainer")
    
class Owners(Base):
    __tablename__ = 'Owners'
    ID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    horses = relationship('Horses', back_populates = "owner")

class Stables(Base):
    __tablename__ = 'Stables'
    ID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    adress = Column(String(50))
    horses = relationship('Horses', back_populates = "stable")

class Horses(Base):
    __tablename__ = 'Horses'
    ID = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    coat = Column(String(30))
    gender = Column(String(30))
    brith_date = Column(String(30))
    breed = Column(String(30))
    origin = Column(String(30))
    father_ID = Column(Integer)
    mother_ID = Column(Integer)
    trainer_ID = Column(Integer, ForeignKey(Trainers.ID))
    owner_ID = Column(Integer, ForeignKey(Owners.ID))
    stable_ID = Column(Integer, ForeignKey(Stables.ID))
    size = Column(String(30))
    trainer = relationship('Trainers',back_populates = "horses")
    stable = relationship('Stables',back_populates = "horses")
    owner = relationship('Owners',back_populates = "horses")
    race_place = relationship('Race_places',back_populates = "horse")
    
class Race_days(Base):
    __tablename__ = 'Race_days'
    ID = Column(Integer, primary_key=True)
    date = Column(String(30), nullable=False)
    track = Column(String(30), nullable=False)
    track_condition = Column(String(50))
    weather = Column(String(30))
    races = relationship('Race', back_populates = "race_day")

class Race(Base):
    __tablename__ = 'Race'
    ID = Column(Integer, primary_key=True)
    race_day_id = Column(Integer, ForeignKey(Race_days.ID), nullable=False)
    horse_group = Column(String(250), nullable=False)
    horse_age = Column(String(30), nullable=False)
    distance = Column(String(30), nullable=False)
    time = Column(String(100))
    finish = Column(String(100))
    race_day = relationship('Race_days', back_populates = "races")
    places = relationship('Race_places', back_populates = "race")
    booking_rates = relationship('Booking_rates', back_populates = "race")

class Race_places(Base):
    __tablename__ = 'Race_places'
    ID = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.ID), nullable=False)
    place = Column(Integer, nullable=False)
    horse_id = Column(Integer, ForeignKey(Horses.ID), nullable=False)
    jockey_id = Column(Integer, ForeignKey(Jockeys.ID), nullable=False)
    race = relationship('Race', back_populates = "places")
    horse = relationship('Horses', back_populates = "race_place")
    jockey = relationship('Jockeys', back_populates = "race_place")

class Booking_rates(Base):
    __tablename__ = 'Booking_rates'
    ID = Column(Integer, primary_key=True)
    race_id = Column(Integer, ForeignKey(Race.ID), nullable=False)
    zwc = Column(Float, nullable=False)
    pdk = Column(Float)
    trj = Column(Float)
    tpl = Column(Float)
    kwn = Column(Float)
    czw = Column(Float)
    spt = Column(Float)
    race = relationship('Race', back_populates = "booking_rates")

   
Base.metadata.create_all(engine)

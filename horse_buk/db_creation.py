""" Constains ORM's Classes which were used for creation DB """

import sqlalchemy as sql
from sqlalchemy import text, ForeignKey, MetaData, Integer, String, Float, Column
from sqlalchemy.orm import declarative_base, relationship


metadata_obj = MetaData()
Base = declarative_base()

class Jockeys(Base):
    """include informations about table Jockeys"""
    __tablename__ = 'Jockeys'
    ID = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    race_place = relationship('Race_places', back_populates = "jockey")

class Trainers(Base):
    """include informations about table Trainers"""
    __tablename__ = 'Trainers'
    ID = Column(Integer, primary_key=True) 
    name = Column(String(30), nullable=False)
    surname = Column(String(30), nullable=False)   
    horses = relationship('Horses', back_populates = "trainer")
    
class Owners(Base):
    """include informations about table Owners"""
    __tablename__ = 'Owners'
    ID = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    horses = relationship('Horses', back_populates = "owner")

class Stables(Base):
    """include informations about table Stables"""
    __tablename__ = 'Stables'
    ID = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    adress = Column(String(150))
    horses = relationship('Horses', back_populates = "stable")

class Horses(Base):
    """include informations about table Horses"""
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
    """include informations about table Race_days"""
    __tablename__ = 'Race_days'
    ID = Column(Integer, primary_key=True)
    date = Column(String(30), nullable=False)
    track = Column(String(30), nullable=False)
    track_condition = Column(String(150))
    weather = Column(String(150))
    races = relationship('Race', back_populates = "race_day")

class Race(Base):
    """include informations about table Race"""
    __tablename__ = 'Race'
    ID = Column(Integer, primary_key=True)
    race_day_id = Column(Integer, ForeignKey(Race_days.ID), nullable=False)
    horse_group = Column(String(500), nullable=False)
    horse_age = Column(String(30), nullable=False)
    distance = Column(String(30), nullable=False)
    time = Column(String(100))
    finish = Column(String(100))
    race_day = relationship('Race_days', back_populates = "races")
    places = relationship('Race_places', back_populates = "race")
    booking_rates = relationship('Booking_rates', back_populates = "race")

class Race_places(Base):
    """include informations about table Race_places"""
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
    """include informations about table Booking_rates"""
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

class Protocols(Base):
    """include protocols address"""
    __tablename__ = 'Protocols'
    ID = Column(Integer, primary_key=True)
    url_adress = Column(String(200), nullable=False)

while True:
    # Enterprise DB to be used
    print("Please enterprise database, which you want to use.\n")
    DRIVER = input("Put info about drivier e.g. ODBC Driver 17 for SQL Server\n")
    SERVERNAME = input("Put servername e.g. DESKTOP-1SHBR4M\n")
    INSTANCENAME = input("Put instance name e.g. \SQLEXPRESS\n")
    DB = input("Put database name e.g. horse_buk_db\n")
    try: 
        engine = sql.create_engine(f"mssql+pyodbc://@{SERVERNAME}{INSTANCENAME}/{DB}?driver={DRIVER}", pool_size=50)
        con = engine.connect()
        print("Connected to database")
        break
    except: 
        print("Something went wrong, please try again")

Base.metadata.create_all(engine)
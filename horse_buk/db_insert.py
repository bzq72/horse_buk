from unicodedata import name
import db_creation as db
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind = db.engine)
session = Session()

def start_session():
    Session = sessionmaker(bind = db.engine)
    session = Session()
    
def insert_record(record):
    session.add(record)
    session.commit()

def insert_owner(owner_name):
    start_session()
    record = db.Owners(name = owner_name)
    insert_record(record)
    print(f'Owner {owner_name} has been added')

def insert_jockey(jockey_name, jockey_surname):
    start_session()
    record = db.Jockeys(name = jockey_name, surname = jockey_surname)
    insert_record(record)
    print(f'Jockey {jockey_name,jockey_surname} has been added')

def insert_trainer(trainer_name, trainer_surname):
    start_session()
    record = db.Trainers(name = trainer_name, surname = trainer_surname)
    insert_record(record)
    print(f"Trainer {trainer_name,trainer_surname} has been added!")
        
def insert_stable(stable_name, stable_adress = None):
    start_session()
    record = db.Stables(name = stable_name, adress = stable_adress)
    insert_record(record)
    print(f"Stable {stable_name} has been added!")

def insert_horse(horse_name, horse_gender, horse_brith_date, horse_coat = None
                , horse_breed = None, horse_origin = None, horse_father_ID = None
                , horse_mother_ID = None, horse_trainer_ID = None
                , horse_owner_ID = None, horse_stable_ID = None
                , horse_size = None):
    start_session()
    record = db.Horses(name = horse_name, coat = horse_coat, gender =horse_gender
                        , brith_date = horse_brith_date, breed = horse_breed
                        , origin = horse_origin, father_ID = horse_father_ID
                        , mother_ID = horse_mother_ID, trainer_ID =horse_trainer_ID
                        , owner_ID = horse_owner_ID, stable_ID = horse_stable_ID
                        , size = horse_size)                     
    insert_record(record)
    print(f'Horse {horse_name} has been added')

def insert_race_day(rd_date, rd_track, rd_track_condition = None, rd_weather = None):
    start_session()
    record = db.Race_days(date = rd_date, track = rd_track
                                , track_condition = rd_track_condition
                                , weather = rd_weather)
    insert_record(record)
    print(f'Race day on {rd_date} in {rd_track} has been added')


def insert_race(race_race_day_ID, race_horse_group, race_horse_age, race_distance
                , race_time, race_finish, race_booking_rates_ID, race_track = None):
    start_session()
    if session.query(db.Race).filter(db.Race.race_day_id==race_race_day_ID 
                                          & db.Race.time==race_time).count() == 0: return  
    else:
        record = db.Race(race_day_ID = race_race_day_ID, track = race_track
                                , horse_group = race_horse_group, horse_age = race_horse_age
                                , distance = race_distance, time = race_time, finish = race_finish
                                , booking_rates_ID = race_booking_rates_ID)
        insert_record(record)
            
def insert_race_place(rp_race_ID, rp_place, rp_horse_ID, rp_jockey_ID):
    start_session()
    if session.query(db.Race_places).filter(db.Race_places.race_id==rp_race_ID 
                                          & db.Race_places.place==rp_place).count() == 0: return  
    else:
        record = db.Race_places(race_ID = rp_race_ID, place = rp_place
                            , horse_ID = rp_horse_ID, jockey_ID = rp_jockey_ID)   
        insert_record(record)

def insert_booking_rates(br_race_id, br_zwc, br_pdk, br_tri = None, br_czw = None
                        , br_kwt = None, br_spt = None):
    start_session()
    if session.query(db.Race_places).filter(db.Booking_rates.race_id==br_race_id).count() == 0: return  
    else:
        record = db.Booking_rates(race_id = br_race_id, zwc = br_zwc, pdk = br_pdk
                                        , tri = br_tri, czw = br_czw, kwt = br_kwt
                                        , spt = br_spt)
        insert_record(record)
    
#insert_owner()
    
#for t in session.query(db.Owners).filter(db.Owners.name == 'test'):
#    print(t.ID, t.name)
#print (session.query(db.Owners.name).all())

#Session = sessionmaker(bind = db.engine)
#session = Session()

#if "test      " in session.query(db.Owners.name).all()[0]: print("ten ziomek juz jest")
#for w in session.query(db.Owners.name).all():
#    print(w)
#    if w[0].rstrip() == "test": print("ten ziomek")
#q = session.query(db.Owners).filter(db.Owners.name == 'test      ').count()

#print(q)
    
print (session.query(db.Horses.name).all())

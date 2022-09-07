"""Contains funcions for inserting records to horse_buk_db"""

from unicodedata import name
import db_creation as db
from sqlalchemy.orm import sessionmaker

    
def insert_record(record):
    Session = sessionmaker(bind = db.engine)
    session = Session()
    session.add(record)
    session.commit()

def is_exist(table, query_filter):
    Session = sessionmaker(bind = db.engine)
    session = Session()
    result = session.query(table).filter(query_filter).first()
    if result: return True
    else: return False

def insert_owner(owner_name):
    owner_name = owner_name[0:20]
    query_filter = (db.Owners.name == owner_name)
    if not is_exist(db.Owners, query_filter):
        record = db.Owners(name = owner_name)
        insert_record(record)
        print(f'Owner {owner_name} has been added')
    else: print(f'Owner {owner_name} is already exist')


def insert_jockey(jockey_name, jockey_surname):
    query_filter = (db.Jockeys.name == jockey_name) & (db.Jockeys.surname == jockey_surname)
    if not is_exist(db.Jockeys, query_filter):
        record = db.Jockeys(name = jockey_name, surname = jockey_surname)
        insert_record(record)
        print(f'Jockey {jockey_name} {jockey_surname} has been added')
    else: print(f'Jockey {jockey_name} {jockey_surname} is already exist')


def insert_trainer(trainer_name, trainer_surname):
    query_filter = ((db.Trainers.name == trainer_name) & (db.Jockeys.surname == trainer_surname))
    if not is_exist(db.Trainers, query_filter):
        record = db.Trainers(name = trainer_name, surname = trainer_surname)
        insert_record(record)
        print(f"Trainer {trainer_name} {trainer_surname} has been added!")
    else: print(f'Trainer {trainer_name}, {trainer_surname} is already exist')

        
def insert_stable(stable_name, stable_adress = None):
    query_filter = (db.Stables.name == stable_name)
    if not is_exist(db.Stables, query_filter):
        record = db.Stables(name = stable_name.strip(), adress = stable_adress)
        insert_record(record)
        print(f"Stable {stable_name} has been added!")
    else: print(f'Stable {stable_name} is already exist')


def insert_horse(horse_name, horse_gender, horse_brith_date, horse_coat = None
                , horse_breed = None, horse_origin = None, horse_father_ID = None
                , horse_mother_ID = None, horse_trainer_ID = None
                , horse_owner_ID = None, horse_stable_ID = None
                , horse_size = None):
    query_filter = ((db.Horses.name == horse_name) & (db.Horses.brith_date == horse_brith_date)
                    & (db.Horses.gender == horse_gender))
    if not is_exist(db.Horses, query_filter):
        record = db.Horses(name = horse_name, coat = horse_coat, gender =horse_gender
                            , brith_date = horse_brith_date, breed = horse_breed
                            , origin = horse_origin, father_ID = horse_father_ID
                            , mother_ID = horse_mother_ID, trainer_ID =horse_trainer_ID
                            , owner_ID = horse_owner_ID, stable_ID = horse_stable_ID
                            , size = horse_size)                     
        insert_record(record)
        print(f'Horse {horse_name} has been added')
    else: print(f'Horse {horse_name} is alredy exist')


def insert_race_day(rd_date, rd_track, rd_track_condition = None, rd_weather = None):
    query_filter = ((db.Race_days.date == rd_date) & (db.Race_days.track == rd_track))
    if not is_exist(db.Race_days, query_filter):
        record = db.Race_days(date = rd_date, track = rd_track
                                    , track_condition = rd_track_condition
                                    , weather = rd_weather)
        insert_record(record)
        print(f'Race day on {rd_date} in {rd_track} has been added')
    else: print(f'Race day on {rd_date} in {rd_track} is already exist')


def insert_race(race_race_day_ID, race_horse_group, race_horse_age, race_distance
                , race_time, race_finish, race_track = None):
    query_filter = ((db.Race.race_day_id == race_race_day_ID) & (db.Race.horse_group == race_horse_group)
                    & (db.Race.time == race_time))
    if not is_exist(db.Race, query_filter):
        record = db.Race(race_day_id = int(race_race_day_ID)
                                , horse_group = race_horse_group, horse_age = race_horse_age
                                , distance = race_distance, time = race_time, finish = race_finish)
        insert_record(record)
        print(f'Race horses {race_horse_group} with time {race_time} has been added')
    else: print(f'Race horses {race_horse_group} with time {race_time} is already exist')

            
def insert_race_place(rp_race_ID, rp_place, rp_horse_ID, rp_jockey_ID):
    query_filter = ((db.Race_places.race_id == rp_race_ID) & (db.Race_places.place == rp_place))
    if not is_exist(db.Race_places, query_filter):
        record = db.Race_places(race_id = rp_race_ID, place = rp_place
                            , horse_id = rp_horse_ID, jockey_id = rp_jockey_ID)   
        insert_record(record)
        print(f"Place {rp_place} on race {rp_race_ID} has been added")
    else: print(f"Place {rp_place} on race {rp_race_ID} is already exist")


def insert_booking_rates(br_race_id, br_zwc, br_pdk, br_trj = None, br_tpl = None, br_kwn = None
                        , br_czw = None, br_spt = None):
    query_filter = ((db.Booking_rates.race_id == br_race_id) & (db.Booking_rates.zwc == br_zwc))
    if not is_exist(db.Booking_rates, query_filter):
        record = db.Booking_rates(race_id = br_race_id, zwc = br_zwc, pdk = br_pdk, trj = br_trj
                                  , tpl = br_tpl, kwn = br_kwn, czw = br_czw, spt = br_spt)
        insert_record(record)
        print(f'Booking rates for race; {br_race_id} with ZWC {br_zwc} has been added')
    else: print(f'Booking rates for race; {br_race_id} with zwc {br_zwc} is already exist')


#insert_jockey("Wojciech", "Tomala")
import pyodbc
import pandas as pd 

class DbService:
    def __init__(self):
        self.connection = pyodbc.connect(Trusted_Connection='yes', driver = '{SQL Server}'
                        ,server = 'DESKTOP-1SHBR4M\\SQLEXPRESS' , database = 'horse_buk_db')
        self.cursor = self.connection.cursor()
    
    def getData(self,query = "Select * from Horses"):
            return pd.read_sql(query,self.connection)
    
    def insert_horse(self,name,coat = "Null", gender = "Null", brith_year = "Null"
                     , breed = "Null", origin = "Null", father = "Null", mother = "Null"
                     , trainer = "Null", owner = "Null", stable = "Null", size = "Null"):
        
        if name: name = f"'{name}'"
        if coat != "Null": coat = f"'{coat}'"
        if gender != "Null": gender = f"'{gender}'"
        if breed != "Null": breed = f"'{breed}'"
        if origin != "Null": origin = f"'{origin}'"
        if size != "Null": size = f"'{size}'"
        
        query = f"INSERT INTO Horses VALUES ({name},{coat}, {gender}, {brith_year}, {breed}, {origin}, {father}, {mother}, {trainer}, {owner}, {stable}, {size})"
        self.execute_query(query)
    
    def insert_stable(self,name,adress):
        query = f"INSERT INTO stable VALUES ('{name}','{adress})"
        self.execute_query(query)
    
    def insert_owner(self,name,surname):
        query = f"INSERT INTO Owners VALUES ('{name}','{surname})"
        self.execute_query(query)

    def insert_trainer(self,name,surname):
        query = f"INSERT INTO Trainers VALUES ('{name}','{surname})"
        self.execute_query(query)
    
    def execute_query(self,query):
        self.cursor.execute(query)
        self.connection.commit()
    
        
service = DbService()
service.insert_horse("Janina", coat = "gniady")
print(service.getData())


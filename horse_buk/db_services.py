import pyodbc
import pandas as pd 

class DB_Service:
    def __init__(self):
        self.connection = pyodbc.connect(Trusted_Connection='yes', driver = '{SQL Server}'
                        ,server = 'DESKTOP-1SHBR4M\\SQLEXPRESS' , database = 'horse_buk_db')
        self.cursor = self.connection.cursor()
    
    def get_data(self,query = "Select * from Horses"):
        """sql query execution"""
        return pd.read_sql(query,self.connection)
        
    def save_to_xlsx(self, query, save_as = "results"):
        """getting and saving sql query results to xlsx"""
        save_as += ".xlsx"
        self.get_data(query).to_excel(save_as)
    
    def insert_horse(self,name,coat = "Null", gender = "Null", brith_year = "Null"
                     , breed = "Null", origin = "Null", father = "Null", mother = "Null"
                     , trainer = "Null", owner = "Null", stable = "Null", size = "Null"):
        """Inserting horse manually to database"""
        if name: name = f"'{name}'"
        if coat != "Null": coat = f"'{coat}'"
        if gender != "Null": gender = f"'{gender}'"
        if breed != "Null": breed = f"'{breed}'"
        if origin != "Null": origin = f"'{origin}'"
        if size != "Null": size = f"'{size}'"
        
        query = f"INSERT INTO Horses VALUES ({name},{coat}, {gender}, {brith_year}, {breed}, {origin}, {father}, {mother}, {trainer}, {owner}, {stable}, {size})"
        self.execute_query(query)
    
    def insert_stable(self,name,adress):
        """Inserting stable manually to database"""
        query = f"INSERT INTO stable VALUES ('{name}','{adress})"
        self.execute_query(query)
    
    def insert_owner(self,name,surname):
        """Inserting Owners manually to database"""
        query = f"INSERT INTO Owners VALUES ('{name}','{surname})"
        self.execute_query(query)

    def insert_trainer(self,name,surname):
        """Inserting Owners manually to database"""
        query = f"INSERT INTO Trainers VALUES ('{name}','{surname})"
        self.execute_query(query)
    
    def execute_query(self,query):
        """excution and commiting queries"""
        self.cursor.execute(query)
        self.connection.commit()
    
        
"""service = DB_Service()
service.insert_horse("Janina", coat = "gniady")
print(service.get_data())"""


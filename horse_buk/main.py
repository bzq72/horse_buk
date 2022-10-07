from db_insert import *
from data_acq_kw import Data_Acq_kw
from data_acq_pkwk import Data_Acq_pkwk
from db_services import DB_Service

o_kw = Data_Acq_kw()
o_pkwk = Data_Acq_pkwk()
service = DB_Service()

def help():
    """avaiable functions description"""
    help = """
        Avaiable functions:
            isSthNew - checking if there is new protocols
            updateDatabase - update database of info about last protocols
            importHorse/(horse name) - searching and importing data about specified horse 
            sql/(sqlquery) - e.g. sql/Select * from Horses - using sql queries on database
            sqlToExcel/(sqlquery)/outputFile - e.g. sqlToExcel/Select * from Horses/allHorses - saving results of sql queries to xlsx file outputFile
            update/(sqlquery) - e.g. update/UPDATE Horses SET gender = 'klacz' WHERE ID = 4669 - updating database records
            delete/(sqlquery) e.g. delete/DELETE FROM Horses WHERE ID = 4669 - deleting database records
            insert/(sqlquery) e.g. insert/INSERT INTO Horses (name) VALUES ('Janina') - inserting database records
            
            exit - to close application"""
    print(help)

def main():
    """main loop"""
    while True:
        func = input("Tell me what you what from me or check what can i do for you by tapping 'help'\n").split("/")
        match func[0]:
            case "exit": break
            case "help": help()
            case "importHorse": o_kw.get_horse_data(func[1])
            case "isSthNew": 
                if o_pkwk.is_sth_new():
                    print("There is new protocol on website")
                else:
                    print("There is nothing new")
            case "updateDatabase":
                o_pkwk.download_every_thing()
            case "sql":  
                print(service.get_data(func[1]))
            case "sqlToExcel":  
                service.save_to_xlsx(query=func[1],save_as=func[2])
                print(f"sql query results saved to {func[2]}.xlsx")
            case "update":  
                update = None
                while update not in ['y','n']:
                    update = input("Do you want to change records?\nThis operation cannot be undone! (y/n)")
                    if update == 'y':
                        service.execute_query(query=func[1])
                        print("Query has been executed")
                    elif update == 'n': break
            case "delete":  
                delete = None
                while delete not in ['y','n']:
                    delete = input("Do you want to delete records?\nThis operation cannot be undone! (y/n)")
                    if delete == 'y':
                        service.execute_query(query=func[1])
                        print("Query has been executed")
                    elif delete == 'n': break
            case "insert":  
                insert = None
                while insert not in ['y','n']:
                    insert = input("Do you want to insert records?\nThis operation cannot be undone! (y/n)")
                    if insert == 'y':
                        service.execute_query(query=func[1])
                        print("Query has been executed")
                    elif insert == 'n': break

        

    
if __name__ == '__main__':
    main()
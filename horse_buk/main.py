from db_insert import *
from data_acq_kw import data_acq_kw
from data_acq_pkwk import data_acq_pkwk

o_kw = data_acq_kw()
o_pkwk = data_acq_pkwk()



def help():
    help = """
            isSthNew - checking if there is new protocols
            updateDatabase - update database of info about last protocols
            importHorse/(horse name) - searching and importing data about specified horse 
            exit - to close application"""
    print(help)



def main():
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



        

    
if __name__ == '__main__':
    main()
# Horse buk
Terminal program to create and update database based on information from horse racing protocols and website koniewyscigowe.pl. In the future program will be predicting which horse should win the race. Main purpose of project is sharping programming skills and getting practical knowledge of working with data, object–relational mapping, webscrapping, working with PDF files and regex.

### Method used:
- 	 Data processing 
- 	 Object–relational mapping
- 	 Webscrapping
- 	 Regex
- 	 and more

### Technologies:
- 	 Python
- 	 Pandas, NumPy
- 	 selenium
- 	 BeautifulSoup
 - 	 SqlAlchemy 
 - 	 pyodbc
- 	 and more

## Project background:
Idea is creating program for predicting which horse will win race. To predict will be used machine learning methods and information extracted from horse racing protocols located on Polish Horse Racing Club website: pkwk.pl and from website which shares information about horses: koniewyscigowe.pl. 

Currently, program enables to get information from pkwk.pl, koniewyscigowe.pl and store them in database. It also has simple terminal user interface. For keeping data is used SQLEXPRESS on local server. Faster and easier data transformation Database<->Program is possible due to ORM library SqlAlchemy. Webscrapping is operated  by Selenium and BeautifulSoup. Getting information about races from protocols in PDF format is made by using regular expressions (module re).

Next goals:
- 	add possibility to dd information about server to UI;
- 	reorganise database (information about finishing distance should be assigned for each place, not info about finishing)
- 	create machine learning models


## User manual:
Terminal application has such available functions:
- 	isSthNew - checking if there is available  new protocols on pkwk.pl with comparison on last checked time. (Warning! If last time, data from protocols was not successfull or fully processed there will be information „No new version available”. However, there will be possibility to force this function to return „New version available” and behave like it is new version.
- 	updateDatabase - update database of info about last protocols – first triggered function is  „isSthNew” (look above) if there are new protocols, tthere are extracted and information from them are processed to database. During it, necessity to write some data from keyboard (for more information read "GetDataBase" in section "Troubleshooting")
- 	importHorse/(horse name) - searching and importing data about specified horse from koniewyścigowe.pl (for more information read "ImportHorses" in section "Troubleshooting")
- 	there is possibility to get/update/delete data from database using sqlqueries:
	- 	sql/(sqlquery) - e.g. sql/Select * from Horses - using sql queries on database
	- 	update/(sqlquery) - e.g. update/UPDATE Horses SET gender = 'klacz' WHERE ID = 4669 - updating database records		
	- 	delete/(sqlquery) e.g. delete/DELETE FROM Horses WHERE ID = 4669 - deleting database records
	- 	insert/(sqlquery) e.g. insert/INSERT INTO Horses (name) VALUES ('Janina') - inserting database records
	- 	qlToExcel/(sqlquery)/outputFile - e.g. sqlToExcel/Select * from Horses/allHorses - saving results of sql queries to XLSX file outputFile
- 	exit - to close application


## Project review:
### Database:
To handling database is used SQLEXPRESS and SqlAlchemy. 
#### Structure:
	Jakies obrazki z połączeniami

### Protocols:
Protocols are downloaded from website: https://www.pkwk.pl/language/pl/sprawozdania-wyscigowe/ in PDF format. Protocols example you can find: https://www.pkwk.pl/wp-content/uploads/2022/04/Wyniki_WARSZAWA_24-04-2022_Dzien_001.pdf. 
With the use of regular expression, protocols are extracted, and such data is saved to database:
- 	Day info:
	- 	date
	- 	track
	- 	track condition
	- 	weather
- 	Race info
	- 	horse group
	- 	horse age
	- 	distance
	- 	time
	- 	finish
	- 	booking rates
	- 	race place
		- 	place
		- 	horse 
		- 	jockey

Due to mistakes and differences in protocols, exception handling with breakpoints is used to help (by user) program find right information. Information which PDFs were completely and successfully processed is kept in database in table „Protocols”. More information about horses, which take a part in race is downloaded from koniewyścigowe.pl

![This is an image](https://i.postimg.cc/pdvcs6vm/protokol.jpg)


### Horses info:
Information about horse such as: name, coat, gender, birth date, breed, origin, father, mother, trainer, owner, stable, size are taken from website: https://koniewyscigowe.pl/ by webscrapping with the use of Selenium and BeautifulSoup. Getting horse data which take part in race can be made by few ways. First program is searching horse name in database, if he not finds he will search website for such horse (problems during such search are described in "ImportHorses" in section "Troubleshooting"). Another case when horse data is downloaded is looking for horse parents. Mainly horses website posses href to parents websites. 

![This is an image](https://i.postimg.cc/L8HWmWqj/Herbatka.jpg)

## Troubleshooting
### ImportHorses:
 - 	  Few horses can have same name, in this case we will get more than one searching results. As your horse will be chosen the youngest one, because main purpose of this program is taking care about participating horses in race, which can’t be old. 
 - 	 If there is no full-matching horse name, but name which you put is part of another horse named, this horse will be added.
 - 	 If there is no full-matching horse name and no part-marching horse no data will be added
 - 	 There is more exceptional situation, if you want to know more, please ask support: bryk.kam@gmail.com

### GetDataBase:
Horse racings protocols are not generated but written by people, so there is a lot of mistakes and differences between each protocol. It can happen that existing regex patterns are not matching for exceptional cases. In such situations' user will be asked to write data from keyboard, for example: horse name, jockey name etc. To cope this, lines where program have problem with recognizing data are showed above. 

### Selected programs features description:













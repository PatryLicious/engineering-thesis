import serial
import sqlite3


def insertVariableIntoTable(sql_connection, sql_cursor, tag_number, status_of_access, lock_status): # log data into the table
    try:
        went_correct = True
        sqlite_insert_with_param = """INSERT INTO lock_access_logs
                          (log_id, tag_number, status_of_access) 
                          VALUES (?, ?, ?, ?, ?);"""
        data_tuple = (readCurrentIDFromDatabase(sql_cursor) + 1, tag_number, status_of_access, lock_status)
        sql_cursor.execute(sqlite_insert_with_param, data_tuple)
        print("Data inserted into lock_access_logs table.")
        sql_connection.commit()
    except sqlite3.Error as e:
        print("Failed to insert data into lock_access_logs table.", e)
        went_correct = False
    finally:
        return went_correct


def createTable(sql_cursor): # create table in  db, in which the logs are going to be stored
    try:
        went_correct = True
        create_table = """CREATE TABLE IF NOT EXISTS
        lock_access_logs(log_id INTEGER PRIMARY KEY AUTOINCREMENT, tag_number INTEGER, status_of_access TEXT,
        lock_status TEXT, date_of_log TEXT)"""
        sql_cursor.execute(create_table)
        print("Table created or was already existing.")
    except sqlite3.Error as e:
        print("Failed to create lock_access_logs table.", e)
        went_correct = False
    finally:
        return went_correct


def readCurrentIDFromDatabase(sql_cursor):  # get highest id number from table
    try:
        sql_cursor.execute("SELECT log_id FROM lock_access_logs ORDER BY  log_id DESC")
        highest_id = int(sql_cursor.fetchone()[0])
        return highest_id
    except sqlite3.Error as e:
        print("Failed to get highest id number from lock_access_logs table.", e)


connection = sqlite3.connect("lock_data.db")  # create connection path to database
cursor = connection.cursor()  # create cursor for database
arduino_port = "COM4"  # serial port to which Arduino is connected via USB
baud_rate = 9600
ser = serial.Serial(arduino_port, baud_rate)
print("Connected to Arduino port:" + arduino_port)
isWorking = True
isWorking = createTable(cursor)

while isWorking:
    getData = ser.readline()
    dataString = getData.decode('utf-8')
    data = dataString[0:][:-2]
    encodedData = data.split(",")
    if len(encodedData) == 3:
        print(encodedData)
        isWorking = insertVariableIntoTable(connection, cursor, int(encodedData[0]), encodedData[1], encodedData[2])
        encodedData = []
        print(readCurrentIDFromDatabase(cursor))

if connection:
    connection.close()
    print("Connection with database closed.")

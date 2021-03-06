import os
import io
import sqlite3
import numpy as np


def adapt_array(arr):
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.read())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)

sqlite3.register_adapter(np.ndarray, adapt_array)
sqlite3.register_converter("ARRAY", convert_array)


class DataBase(object):
    def __init__(self, database_dir, database_file="edgematrix.db"):
        if not os.path.exists(database_dir):
            os.makedirs(database_dir, exist_ok=True)
        database = os.path.join(database_dir, database_file)
        if not os.path.exists(database):
            self.conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            self.create_database()
        else:
            self.conn = sqlite3.connect(database, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

    def create_database(self):
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE PAIRS
                        (CELL_ID INT NOT NULL,
                        VEHICLE_ID INT NOT NULL,
                        CLASS_ID INT  NOT NULL,
                        TYPE_SPACE TEXT NOT NULL,
                        PARKING_GROUND TEXT NOT NULL,
                        INACTIVE_STEPS INT NOT NULL,
                        START_TIME  timestamp NOT NULL,
                        END_TIME timestamp,
                        PRIMARY KEY (CELL_ID, VEHICLE_ID, CLASS_ID, TYPE_SPACE, PARKING_GROUND));""")

        cursor.execute("""CREATE TABLE PARKING_SPACES
                        (PARKING_GROUND TEXT NOT NULL,
                        CELL_ID INT NOT NULL,
                        TYPE_SPACE TEXT NOT NULL,
                        COORDINATE ARRAY NOT NULL,
                        PRIMARY KEY (PARKING_GROUND, CELL_ID))""")
        self.conn.commit()

    def add_pairs(self, pairs_info):
        cursor = self.conn.cursor()
        cursor.executemany("INSERT OR REPLACE INTO PAIRS VALUES (?, ?, ?, ?, ?, ?, ?, ?)", pairs_info)
        self.conn.commit()

    def add_parking_spaces(self, cells_info):
        cursor = self.conn.cursor()
        cursor.executemany("INSERT INTO PARKING_SPACES VALUES (?, ?, ?, ?)", cells_info)

    def get_active_pairs(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM PAIRS WHERE INACTIVE_STEPS = 0")
        records = cursor.fetchall()
        return records

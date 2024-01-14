import sqlite3

class DataBase():
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_db()

    def create_db(self):
        try:
            query = ('CREATE TABLE IF NOT EXISTS users('
                     'id INTEGER PRIMARY KEY,'
                     'user_mark TEXT);')
            self.cursor.execute(query)
            self.connection.commit()

        except sqlite3.Error as Error:
            print("Oшибка при создании", Error)


    def add_mark(self, user_mark):
        self.cursor.execute(f"INSERT INTO users (user_mark) VALUES (?)", (user_mark,))
        self.connection.commit()

    def select_marks(self):
        query = 'SELECT user_mark FROM users;'
        marks = self.cursor.execute(query)
        return marks.fetchall()




    def __del__(self):
        self.cursor.close()
        self.connection.close()


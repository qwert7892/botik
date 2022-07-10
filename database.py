import sqlite3


class Db:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()

    def create_profile(self, tg_username, name, city, role, year, description, superpower, photo):
        with self.connection:
            return self.cursor.execute("INSERT INTO `profile_list` (`tg_usename`,`name`,"
                                       "`city`,'role','year',`description`, `superpower`, 'photo') VALUES(?,?,?,?,?,?,?,?)",
                                       (tg_username, name, city, role, year, description, superpower, photo))

    def profile_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `profile_list` WHERE `tg_usename` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def delete(self, username):
        with self.connection:
            return self.cursor.execute("DELETE FROM `profile_list` WHERE `tg_usename` = ?", (username,))

    def get_info(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `profile_list` WHERE `tg_usename` = ?", (user_id,)).fetchall()

    def get_info_user(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT 'description' FROM `profile_list` WHERE `tg_usename` = ?",
                                       (user_id,)).fetchone()

    def is_admin(self, username):
        with self.connection:
            return self.cursor.execute("SELECT 'admin_status' FROM 'profile_list' WHERE 'tg_usename' = ?",
                                       (username,)).fetchall()

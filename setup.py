# Ref: https://www.pytorials.com/face-recognition-using-opencv-part-2/

# Setup database
import sqlite3

conn = sqlite3.connect('database.db')
db = conn.cursor()

sql = """
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    `name` TEXT UNIQUE
);
"""
db.executescript(sql)

conn.commit()
conn.close()

print("SETUP DONE")

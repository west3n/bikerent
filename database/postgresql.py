import psycopg2

db = psycopg2.connect(
    host="92.53.127.97",
    database="default_db",
    user="gen_user",
    password="Tim262Tim262"
)

cur = db.cursor()

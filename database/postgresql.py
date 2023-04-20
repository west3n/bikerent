import psycopg2

db = psycopg2.connect(
    host="188.225.47.62",
    database="default_db",
    user="gen_user",
    password="Tim262Tim262"
)

cur = db.cursor()

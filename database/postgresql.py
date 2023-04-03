import psycopg2

db = psycopg2.connect(
    host="194.26.138.250",
    database="default_db",
    user="gen_user",
    password="Golova123"
)

cur = db.cursor()

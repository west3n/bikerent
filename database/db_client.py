from database.postgresql import db, cur


async def create_table():
    cur.execute("""
    CREATE TABLE client (
        id SERIAL PRIMARY KEY,
        name TEXT,
        contact TEXT UNIQUE NOT NULL,
        tg_id BIGINT,
        photo_id BYTEA,
        photo_license BYTEA
    )""")
    db.commit()


async def add_client(data):
    name = data.get('client_name')
    contact = data.get('client_contact')
    query = "INSERT INTO client (name, contact) VALUES (%s, %s)"
    values = (name, contact,)
    cur.execute(query, values)
    db.commit()


async def get_client_id(data):
    contact = data.get('client_contact')
    query = "SELECT id FROM client WHERE contact=%s"
    values = (contact,)
    cur.execute(query, values)
    result = cur.fetchone()
    return result

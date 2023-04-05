from database.postgresql import db, cur


async def create_table():
    cur.execute("""
    CREATE TABLE client (
        id SERIAL PRIMARY KEY,
        name TEXT,
        contact TEXT,
        tg_id BIGINT
    )""")
    db.commit()

asyncio.run(create_table())
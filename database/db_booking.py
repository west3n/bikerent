import asyncio

from database.postgresql import db, cur


async def create_table():
    cur.execute("""
        CREATE TABLE booking (
            id SERIAL PRIMARY KEY,
            bike INTEGER REFERENCES bike (id) ON DELETE CASCADE,
            start_date DATE,
            rental_period INTEGER,
            discount INTEGER DEFAULT 0,
            client INTEGER REFERENCES client (id) ON DELETE CASCADE,
            address TEXT,
            delivery_time TEXT,
            delivery_price INTEGER DEFAULT 0
        );
    """)
    cur.execute("""
        ALTER TABLE booking
        ALTER COLUMN delivery_time TYPE TIMESTAMP USING to_timestamp(delivery_time, 'DD.MM.YYYY HH24:MI');
    """)
    db.commit()

asyncio.run(create_table())

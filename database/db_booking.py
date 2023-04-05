from database.postgresql import db, cur
import asyncio
from datetime import datetime, date


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
            delivery_price INTEGER DEFAULT 0,
            price BIGINT
        );
    """)
    cur.execute("""
        ALTER TABLE booking
        ALTER COLUMN delivery_time TYPE TIMESTAMP USING to_timestamp(delivery_time, 'DD.MM.YYYY HH24:MI');
    """)
    db.commit()


async def add_booking(data):
    bike_id = int(data.get('bike'))
    date_str = data.get('start_day')
    date_parts = date_str.split('_')[1:]
    year = datetime.now().year
    month, day = map(int, date_parts)
    date_obj = date(year, month, day)
    rental_period = data.get('rental_period')
    if not rental_period.isdigit():
        if rental_period == '1_day':
            rental_period = 1
        elif rental_period == '1_week':
            rental_period = 7
        elif rental_period == '1_month':
            rental_period = 30
    client_id = data.get('client_id')
    address = data.get('address')
    delivery_time = data.get('delivery_time')
    time_obj = datetime.strptime(delivery_time, '%H:%M').time()
    datetime_obj = datetime.combine(date_obj, time_obj)
    formatted_datetime = datetime_obj.strftime('%Y-%m-%d %H:%M')
    delivery_price = data.get('delivery_price')
    price = data.get('price')
    try:
        discount = data.get('discount')
        if discount == "yes":
            discount = 1
        else:
            discount = 0
    except:
        discount = 1
    cur.execute("""
            INSERT INTO booking
            (bike, start_date, rental_period, discount, client, address, delivery_time, delivery_price, price)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (bike_id, date_obj, rental_period, discount, client_id, address, formatted_datetime, delivery_price, price))
    db.commit()


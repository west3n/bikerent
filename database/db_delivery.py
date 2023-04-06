from database.postgresql import db, cur
from database.db_booking import get_client_id
import asyncio


async def create_table():
    cur.execute('''
        CREATE TABLE delivery (
            id SERIAL PRIMARY KEY,
            bike INTEGER REFERENCES bike(id) ON DELETE CASCADE,
            client INTEGER REFERENCES client(id) ON DELETE CASCADE,
            booking INTEGER REFERENCES booking(id) ON DELETE SET NULL,
            leftside_photo BYTEA,
            frontside_photo BYTEA,
            rightside_photo BYTEA,
            backside_photo BYTEA,
            passport_number_client TEXT,
            client_with_passport_photo BYTEA,
            payment_method TEXT
        )
    ''')
    db.commit()


async def add_new_delivery(data):
    bike = int(data.get('bike_id'))
    booking_id = int(data.get('booking_id'))
    client_id = await get_client_id(booking_id)
    client_id = client_id[0]
    leftside_photo = data.get('leftside_photo')
    frontside_photo = data.get('frontside_photo')
    rightside_photo = data.get('rightside_photo')
    backside_photo = data.get('backside_photo')
    passport_number_client = data.get('passport_number')
    client_with_passport_photo = data.get('client_with_passport_photo')
    payment_method = data.get('payment_method')
    query = '''
            INSERT INTO delivery (bike, client, booking, leftside_photo, frontside_photo, rightside_photo,
                                  backside_photo, passport_number_client, client_with_passport_photo, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
    cur.execute(query, (bike, client_id, booking_id, leftside_photo, frontside_photo, rightside_photo,
                        backside_photo, passport_number_client, client_with_passport_photo, payment_method))
    db.commit()





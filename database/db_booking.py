from database.postgresql import db, cur
from datetime import datetime, date
from database import db_bike, db_client


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
    discount = data.get('discount')
    comment = data.get('booking_comment')
    cur.execute("""
            INSERT INTO booking
            (bike, start_date, rental_period, discount, client, address, delivery_time, delivery_price, price, comment)
            VALUES
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
        bike_id, date_obj, rental_period, discount, client_id, address, formatted_datetime, delivery_price, price,
        comment))
    result = cur.fetchone()[0]
    db.commit()
    return result


async def check_booking(bike_id):
    cur.execute("""SELECT * FROM booking WHERE bike=%s""", (bike_id,))
    result = cur.fetchall()
    return result


async def status_booking(booking_id):
    cur.execute("""SELECT * FROM booking WHERE id=%s""", (booking_id,))
    result = cur.fetchone()
    return result


async def delete_booking(booking_id):
    cur.execute("DELETE FROM booking WHERE id=%s", (booking_id,))
    db.commit()


async def get_client_id(booking_id):
    cur.execute("SELECT client FROM booking WHERE id=%s", (booking_id,))
    result = cur.fetchone()
    return result


async def get_booking_data_by_client_id(client_id):
    cur.execute("SELECT * FROM booking WHERE client=%s", (client_id,))
    result = cur.fetchall()
    return result


async def all_bookings():
    cur.execute("SELECT * FROM booking")
    result = cur.fetchall()
    return result

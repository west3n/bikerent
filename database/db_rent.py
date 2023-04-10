from datetime import timedelta

from database.postgresql import db, cur
from database.db_booking import status_booking


def create_table():
    cur.execute(f"CREATE TABLE rent ("
                f"id SERIAL PRIMARY KEY,"
                f"bike integer REFERENCES bike (id) ON DELETE CASCADE,"
                f"client integer REFERENCES client (id) ON DELETE CASCADE,"
                f"date_start date,"
                f"date_finish date)")
    db.commit()


async def add_new_rent(booking_id):
    info = await status_booking(booking_id)
    bike_id = info[1]
    client_id = info[5]
    start_date = info[2]
    end_date = (info[2] + timedelta(days=info[3])).strftime("%Y-%m-%d")
    cur.execute("INSERT INTO rent (bike, client, date_start, date_finish) VALUES (%s, %s, %s, %s)",
                (bike_id, client_id, start_date, end_date))
    db.commit()


async def get_all_rent(bike_id):
    cur.execute("SELECT * FROM rent WHERE bike=%s", (bike_id,))
    result = cur.fetchall()
    return result


async def get_all_rent_info(bike_id):
    cur.execute("SELECT * FROM rent WHERE bike=%s", (bike_id,))
    result = cur.fetchone()
    return result


async def get_bike_id(rent_id):
    cur.execute("SELECT bike FROM rent WHERE id=%s", (rent_id,))
    result = cur.fetchone()
    return result


async def all_rent():
    cur.execute("SELECT * FROM rent")
    result = cur.fetchall()
    return result


async def finish_rent(rent_id):
    cur.execute("DELETE FROM rent WHERE id=%s", (rent_id,))
    db.commit()


async def gen_end_date(rent_id):
    cur.execute("SELECT date_finish FROM rent WHERE id=%s", (rent_id,))
    result = cur.fetchone()
    return result
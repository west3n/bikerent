from datetime import timedelta

from database.postgresql import db, cur
from database.db_booking import status_booking, delete_booking


def create_table():
    cur.execute(f"CREATE TABLE rent ("
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




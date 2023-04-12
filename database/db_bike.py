from database.postgresql import cur, db


async def create_table():
    cur.execute(f"CREATE TABLE IF NOT EXISTS bike ("
                f"id SERIAL PRIMARY KEY,"
                f"brand TEXT,"
                f"model TEXT,"
                f'year INT,'
                f"purchase_price BIGINT,"
                f"millage INT,"
                f"abs_cbs BOOLEAN,"
                f"keyless BOOLEAN,"
                f"plate_no VARCHAR(15),"
                f"color TEXT,"
                f"gps BOOLEAN,"
                f"style TEXT,"
                f"docs BOOLEAN,"
                f"exhaust TEXT,"
                f"photo BYTEA,"
                f"status TEXT)")
    db.commit()


async def create_new_bike(data):
    brand = data.get('brand')
    model = data.get('model')
    year = data.get('year')
    purchase_price = data.get('purchase_price')
    millage = data.get('millage')
    abs_cbs = data.get('abs_cbs')
    style = data.get('style')
    if abs_cbs == "yes":
        abs_cbs = True
    else:
        abs_cbs = False
    keyless = data.get('keyless')
    if keyless == "yes":
        keyless = True
    else:
        keyless = False
    plate_no = data.get('plate_no')
    color = data.get('color')
    gps = data.get('gps')
    if gps == "yes":
        gps = True
    else:
        gps = False
    docs = data.get('docs')
    if docs == "yes":
        docs = True
    else:
        docs = False
    exhaust = data.get('exhaust')
    photo = data.get('photo')
    status = data.get('status')
    query = ("""
            INSERT INTO bike 
                (brand, model, year, purchase_price, millage, abs_cbs, keyless, plate_no, color, 
                gps, style, docs, exhaust, photo, status) 
            VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """)
    values = (brand, model, year, purchase_price, millage, abs_cbs, keyless, plate_no,
              color, gps, style, docs, exhaust, photo, status)
    cur.execute(query, values)
    db.commit()


async def db_update_bike(bike_id, data):
    set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
    query = f"UPDATE bike SET {set_clause} WHERE id = %s"
    values = list(data.values())
    values.append(bike_id)
    cur.execute(query, tuple(values))
    db.commit()


async def delete_bike(bike_id):
    query = "DELETE FROM bike WHERE id = %s"
    cur.execute(query, (bike_id,))
    db.commit()


async def get_bike_info():
    query = "SELECT id, model, plate_no FROM bike"
    cur.execute(query)
    results = cur.fetchall()
    return results


async def get_bike_booking_status():
    status = 'booking'
    query = "SELECT id, model, plate_no FROM bike WHERE status=%s"
    cur.execute(query, (status, ))
    results = cur.fetchall()
    return results


async def get_bike(bike_id):
    query = "SELECT id, model, plate_no FROM bike WHERE id=%s"
    values = (bike_id,)
    cur.execute(query, values)
    results = cur.fetchone()
    return results


async def get_photo(bike_id):
    query = "SELECT photo FROM bike WHERE id=%s"
    cur.execute(query, (bike_id,))
    result = cur.fetchone()
    return result


async def get_more_bike_info(bike_id):
    query = "SELECT * FROM bike WHERE id=%s"
    cur.execute(query, (bike_id,))
    results = cur.fetchone()
    return results


async def get_bike_status(bike_id):
    query = "SELECT status FROM bike WHERE id=%s"
    cur.execute(query, (bike_id,))
    results = cur.fetchone()
    return results


async def change_bike_status_to_booking(bike_id):
    query = "UPDATE bike SET status='booking' WHERE id=%s"
    cur.execute(query, (bike_id,))
    db.commit()


async def change_bike_status_to_free(bike_id):
    query = "UPDATE bike SET status='free' WHERE id=%s"
    cur.execute(query, (bike_id,))
    db.commit()


async def update_millage(millage, bike_id):
    query = "UPDATE bike SET millage = %s WHERE id=%s"
    cur.execute(query, (millage, bike_id,))
    db.commit()


async def get_millage(bike_id):
    query = "SELECT millage FROM bike WHERE id=%s"
    cur.execute(query, (bike_id,))
    result = cur.fetchone()
    return result[0]

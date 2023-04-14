from database.postgresql import cur, db


def create_table():
    cur.execute(f"CREATE TABLE service ("
                f"id SERIAL PRIMARY KEY,"
                f"bike_id INTEGER REFERENCES bike ON DELETE CASCADE,"
                f"status TEXT,"
                f"cost BIGINT)")
    db.commit()


async def create_oil_service_table():
    cur.execute("CREATE TABLE oil_services ("
                "id SERIAL PRIMARY KEY,"
                "bike_id INTEGER REFERENCES bike (id) ON DELETE CASCADE,"
                "oil_need_change BOOLEAN DEFAULT FALSE,"
                "last_oil_change_mileage INTEGER DEFAULT 0)")
    db.commit()


async def insert_oil_service_table(bike_id):
    cur.execute(f"INSERT INTO oil_services (bike_id, last_oil_change_mileage) "
                f"SELECT id, millage FROM bike WHERE id=%s", (bike_id, ))
    db.commit()


async def take_data_from_oil_service(bike_id):
    cur.execute("SELECT oil_need_change, last_oil_change_mileage FROM oil_services WHERE bike_id=%s", (bike_id,))
    result = cur.fetchone()
    return result


async def update_oil_need_change_data(bike_id):
    cur.execute("UPDATE oil_services SET oil_need_change = true WHERE bike_id = %s AND oil_need_change = false",
                (bike_id,))
    db.commit()


async def update_oil_need_change_data_false(bike_id):
    cur.execute("UPDATE oil_services SET oil_need_change = false WHERE bike_id = %s AND oil_need_change = true",
                (bike_id,))


async def update_bike_service_status_exist(bike_id):
    cur.execute("SELECT * FROM service WHERE bike_id = %s",
                (bike_id,))
    result = cur.fetchone()
    return result


async def update_bike_service_status(bike_id):
    exist = await update_bike_service_status_exist(bike_id)
    if not exist:
        cur.execute("INSERT INTO service (bike_id, status)  VALUES (%s, %s)", (bike_id, 'oil change'))
        db.commit()
    else:
        cur.execute("UPDATE service SET status = 'oil change' WHERE bike_id = %s",
                    (bike_id,))
        db.commit()


async def get_all_service():
    cur.execute("SELECT * FROM service")
    result = cur.fetchall()
    return result


async def db_create_new_task(bike_id, task):
    cur.execute("INSERT INTO service (bike_id, status)  VALUES (%s, %s)", (bike_id, task))
    db.commit()


async def get_bike_id(service_id):
    cur.execute("SELECT bike_id FROM service WHERE id=%s", (service_id,))
    result = cur.fetchone()
    return result

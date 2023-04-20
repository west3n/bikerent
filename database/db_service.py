from database.postgresql import cur, db


async def insert_oil_service_table(bike_id):
    cur.execute(f"INSERT INTO oil_services (bike_id, last_oil_change_mileage) "
                f"SELECT id, millage FROM bike WHERE id=%s", (bike_id,))
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
        cur.execute("INSERT INTO service (bike_id, status)  VALUES (%s, %s) RETURNING id", (bike_id, 'oil change'))
        result = cur.fetchone()[0]
        db.commit()
        return result
    else:
        cur.execute("UPDATE service SET status = 'oil change' WHERE bike_id = %s RETURNING id",
                    (bike_id,))
        result = cur.fetchone()[0]
        db.commit()
        return result


async def get_open_service():
    cur.execute("SELECT * FROM service WHERE open=true")
    result = cur.fetchall()
    return result


async def db_create_new_task(bike_id, task):
    cur.execute("INSERT INTO service (bike_id, status)  VALUES (%s, %s) RETURNING id", (bike_id, task))
    result = cur.fetchone()[0]
    db.commit()
    return result


async def get_bike_id(service_id):
    cur.execute("SELECT bike_id FROM service WHERE id=%s", (service_id,))
    result = cur.fetchone()
    return result


async def delete_service(service_id):
    cur.execute("DELETE FROM service WHERE id=%s", (service_id,))
    db.commit()


async def get_client_damage_service():
    cur.execute("SELECT * FROM service WHERE status='client damage'")
    result = cur.fetchall()
    return result


async def get_not_opened_service():
    cur.execute("SELECT * FROM service WHERE open=false")
    result = cur.fetchall()
    return result


async def update_open_task(start_date,service_id):
    cur.execute("UPDATE service SET open=true, start_date=%s WHERE id=%s", (start_date,service_id,))
    db.commit()


async def get_service_for_bike(bike_id):
    cur.execute("SELECT id, start_date, status FROM service WHERE open=true AND bike_id=%s",(bike_id,))
    result = cur.fetchall()
    return result
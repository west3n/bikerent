from database import db_bike
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


async def get_all_service():
    cur.execute("SELECT * FROM service")
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


async def send_service_notification():
    query = """
            SELECT *
            FROM service
        """
    cur.execute(query)
    results = cur.fetchall()
    message = f"SERVICE TASKS NOT CLOSED:\n"
    if results:
        for result in results:
            bike = await db_bike.get_bike(result[1])
            message += f"\n- Service task #{result[0]}\n" \
                       f"Bike #{bike[0]}: {bike[1]}, {bike[2]}\n" \
                       f"Task: {result[2]}\n"

    else:
        message = 'Today very good day:\n' \
                  'No service tasks!'

    return message

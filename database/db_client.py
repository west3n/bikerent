from database.postgresql import db, cur
import datetime


async def add_client(data):
    name = data.get('client_name')
    contact = data.get('client_contact')
    query = "INSERT INTO client (name, contact) VALUES (%s, %s)"
    values = (name, contact,)
    cur.execute(query, values)
    db.commit()


async def get_client_id(data):
    contact = data.get('client_contact')
    query = "SELECT id FROM client WHERE contact=%s"
    values = (contact,)
    cur.execute(query, values)
    result = cur.fetchone()
    return result


async def get_client_contact(client_id):
    cur.execute("SELECT contact FROM client WHERE id=%s", (client_id,))
    result = cur.fetchone()
    return result


async def get_tg_id(client_id):
    cur.execute("SELECT tg_id FROM client WHERE id=%s", (client_id,))
    result = cur.fetchone()
    return result


async def get_client_name(client_id):
    cur.execute("SELECT name FROM client WHERE id=%s", (client_id,))
    result = cur.fetchone()
    return result


async def update_after_delivery(data, client_id):
    photo_id = data.get('passport_photo')
    photo_license = data.get('license_photo')
    insta = data.get('instagram_account')
    phone = data.get('phone_number')
    contact = await get_client_contact(int(client_id))
    contact = f'Info from booking: {contact[0]}\n'
    contact += f'Instagram: {insta}\n'
    contact += f'Phone number (info from deliveryman): {phone}'

    cur.execute("UPDATE client SET contact = %s, photo_id = %s, photo_license = %s WHERE id=%s",
                (contact, photo_id, photo_license, client_id))
    db.commit()


async def update_after_finish_rent(client_id):
    contact = await get_client_contact(int(client_id))
    contact = f'Rent info: {contact[0]}\n'
    contact += f'Finish rent: {datetime.datetime.now()}'
    cur.execute("UPDATE client SET contact = %s WHERE id=%s", (contact, client_id,))
    db.commit()

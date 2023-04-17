from database.postgresql import db, cur
from database.db_booking import get_client_id


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
    add_photo = data.get("add_photo")
    add_photo_2 = data.get("add_photo_2")
    add_photo_3 = data.get("add_photo_3")
    add_photo_4 = data.get("add_photo_4")
    add_photo_5 = data.get("add_photo_5")
    add_photo_6 = data.get("add_photo_6")
    add_photo_7 = data.get("add_photo_7")
    add_photo_8 = data.get("add_photo_8")
    query = '''
            INSERT INTO delivery (bike, client, booking, leftside_photo, frontside_photo, rightside_photo,
                                  backside_photo, passport_number_client, client_with_passport_photo, payment_method,
                                  add_photo, add_photo2, add_photo3, add_photo4, add_photo5, add_photo6, 
                                  add_photo7, add_photo8)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
    cur.execute(query, (bike, client_id, booking_id, leftside_photo, frontside_photo, rightside_photo,
                        backside_photo, passport_number_client, client_with_passport_photo, payment_method,
                        add_photo, add_photo_2, add_photo_3, add_photo_4, add_photo_5, add_photo_6,
                        add_photo_7, add_photo_8))
    db.commit()


async def test_delivery():
    cur.execute("SELECT photo_id, photo_license FROM client WHERE id=51")
    result = cur.fetchone()
    return result

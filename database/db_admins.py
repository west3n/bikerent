from database.postgresql import db, cur


async def create_table():
    cur.execute(f"CREATE TABLE IF NOT EXISTS admins ("
                f"tg_id BIGINT UNIQUE NOT NULL,"
                f"name VARCHAR(25) NOT NULL,"
                f"status VARCHAR(15) NOT NULL)")
    db.commit()


async def check_status(tg_id):
    cur.execute("SELECT status FROM admins WHERE tg_id=%s", (tg_id,))
    result = cur.fetchone()
    return result


async def create_admin(data):
    cur.execute("INSERT INTO admins (tg_id, name, status) VALUES (%s, %s, %s)",
                (data.get('tg_id'), data.get('name'), data.get('status'),))
    db.commit()


async def all_admins():
    cur.execute("""SELECT * FROM admins WHERE status IN (%s, %s)""", ("manager", "deliveryman"))
    result = cur.fetchall()
    return result


async def delete_admin(tg_id):
    cur.execute("DELETE FROM admins WHERE tg_id=%s", (tg_id,))
    db.commit()


async def update_admin(data):
    cur.execute("UPDATE admins SET status=%s WHERE tg_id=%s", (data.get('status'), data.get('tg_id'),))
    db.commit()

from database.postgresql import db, cur


def create_table_service():
    cur.execute(f"CREATE TABLE service ("
                f"id SERIAL PRIMARY KEY,"
                f"bike_id INTEGER REFERENCES bike ON DELETE CASCADE,"
                f"start_date DATE,"
                f"open BOOLEAN DEFAULT FALSE,"
                f"status TEXT,"
                f"cost BIGINT)")
    db.commit()


def create_oil_service_table():
    cur.execute("CREATE TABLE oil_services ("
                "id SERIAL PRIMARY KEY,"
                "bike_id INTEGER REFERENCES bike (id) ON DELETE CASCADE,"
                "oil_need_change BOOLEAN DEFAULT FALSE,"
                "last_oil_change_mileage INTEGER DEFAULT 0)")
    db.commit()


def create_table_rent():
    cur.execute(f"CREATE TABLE rent ("
                f"id SERIAL PRIMARY KEY,"
                f"bike integer REFERENCES bike (id) ON DELETE CASCADE,"
                f"client integer REFERENCES client (id) ON DELETE CASCADE,"
                f"date_start date,"
                f"date_finish date)")
    db.commit()


def create_table_delivery():
    cur.execute('''
        CREATE TABLE delivery (
            id SERIAL PRIMARY KEY,
            bike INTEGER REFERENCES bike(id) ON DELETE CASCADE,
            client INTEGER REFERENCES client(id) ON DELETE CASCADE,
            booking INTEGER REFERENCES booking(id) ON DELETE SET NULL,
            leftside_photo BYTEA,
            frontside_photo BYTEA,
            rightside_photo BYTEA,
            backside_photo BYTEA,
            passport_number_client TEXT,
            client_with_passport_photo BYTEA,
            payment_method TEXT,
            add_photo BYTEA,
            add_photo2 BYTEA,
            add_photo3 BYTEA,
            add_photo4 BYTEA,
            add_photo5 BYTEA,
            add_photo6 BYTEA,
            add_photo7 BYTEA,
            add_photo8 BYTEA
        )
    ''')
    db.commit()


def create_table_client():
    cur.execute("""
    CREATE TABLE client (
        id SERIAL PRIMARY KEY,
        name TEXT,
        contact TEXT UNIQUE NOT NULL,
        tg_id BIGINT,
        photo_id BYTEA,
        photo_license BYTEA
    )""")
    db.commit()


def create_table_booking():
    cur.execute("""
        CREATE TABLE booking (
            id SERIAL PRIMARY KEY,
            bike INTEGER REFERENCES bike (id) ON DELETE CASCADE,
            start_date DATE,
            rental_period INTEGER,
            discount INTEGER DEFAULT 0,
            client INTEGER REFERENCES client (id) ON DELETE CASCADE,
            address TEXT,
            delivery_time TEXT,
            delivery_price INTEGER DEFAULT 0,
            price BIGINT,
            comment TEXT
        );
    """)
    cur.execute("""
        ALTER TABLE booking
        ALTER COLUMN delivery_time TYPE TIMESTAMP USING to_timestamp(delivery_time, 'DD.MM.YYYY HH24:MI');
    """)
    db.commit()


def create_table_bike():
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


def create_description_table():
    cur.execute("CREATE TABLE bike_description ("
                "bike_id INTEGER,"
                "description TEXT,"
                "FOREIGN KEY (bike_id) REFERENCES bike(id) ON DELETE CASCADE)")
    db.commit()


def create_table_admins():
    cur.execute(f"CREATE TABLE IF NOT EXISTS admins ("
                f"tg_id BIGINT UNIQUE NOT NULL,"
                f"name VARCHAR(25) NOT NULL,"
                f"status VARCHAR(15) NOT NULL)")
    db.commit()


def table_creation():
    create_table_bike()
    create_table_client()
    create_table_admins()
    create_table_booking()
    create_table_rent()
    create_table_delivery()
    create_description_table()
    create_table_service()
    create_oil_service_table()


table_creation()

import psycopg2


def createdb(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients(
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(150) NOT NULL,
            last_name VARCHAR(150) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL
        );
        """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS client_phones(
            id SERIAL PRIMARY KEY,
            client_id INTEGER NOT NULL,
            phone_number VARCHAR(30) UNIQUE NOT NULL,
            FOREIGN KEY (client_id) REFERENCES clients(id)
        );
        """)

    conn.commit()


def add_client(conn, first_name, last_name, email, phones=None):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clients (first_name, last_name, email)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (first_name, last_name, email)
    )
    client_id = cur.fetchone()[0]
    
    if phones:
        for phone in phones:
            cur.execute(
                """
                INSERT INTO client_phones (client_id, phone_number)
                VALUES (%s, %s)
                """,
                (client_id, phone)
            )

    conn.commit()


def add_phone(conn, client_id, phone_number):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) FROM clients WHERE id = %s
        """,
        (client_id,)
    )

    if cur.fetchone()[0] == 0:
        raise ValueError(f"Client with id {client_id} does not exist")

    cur.execute(
        """
        INSERT INTO client_phones (client_id, phone_number)
        VALUES (%s, %s)
        """,
        (client_id, phone_number)
    )

    conn.commit()


def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    cur = conn.cursor()
    fields = []
    values = []
    if first_name:
        fields.append("first_name = %s")
        values.append(first_name)
    if last_name:
        fields.append("last_name = %s")
        values.append(last_name)
    if email:
        fields.append("email = %s")
        values.append(email)

    if not fields:
        return

    query = "UPDATE clients SET " + ", ".join(fields) + " WHERE id = %s"
    values.append(client_id)
    cur.execute(query, tuple(values))
    conn.commit()


def delete_phone(conn, client_id, phone_number):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) FROM clients WHERE id = %s
        """,
        (client_id,)
    )

    if cur.fetchone()[0] == 0:
        raise ValueError(f"Client with id {client_id} does not exist")

    cur.execute(
        """
        DELETE FROM client_phones WHERE client_id = %s AND phone_number = %s
        """,
        (client_id, phone_number)
    )

    conn.commit()


def delete_client(conn, client_id):
    cur = conn.cursor()
    cur.execute(
        """
        SELECT COUNT(*) FROM clients WHERE id = %s
        """,
        (client_id,)
    )

    if cur.fetchone()[0] == 0:
        raise ValueError(f"Client with id {client_id} does not exist")

    cur.execute(
        """
        DELETE FROM client_phones WHERE client_id = %s
        """,
        (client_id,)
    )

    cur.execute(
        """
        DELETE FROM clients WHERE id = %s
        """,
        (client_id,)
    )

    conn.commit()


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    cur = conn.cursor()
    query = "SELECT * FROM clients WHERE "
    conditions = []
    params = []
    if first_name:
        conditions.append("first_name = %s")
        params.append(first_name)
    if last_name:
        conditions.append("last_name = %s")
        params.append(last_name)
    if email:
        conditions.append("email = %s")
        params.append(email)
    if phone:
        query += "id IN (SELECT client_id FROM client_phones WHERE phone_number = %s)"
        params.append(phone)
    else:
        query += " AND ".join(conditions)
    
    cur.execute(query, params)
    result = cur.fetchall()
    if not result:
        print("Клиент не найден.")
    else:
        print("Информация о клиенте:")
        for row in result:
            print(f"ID: {row[0]}\nИмя: {row[1]}\nФамилия: {row[2]}\nEmail: {row[3]}")


if __name__ == "__main__":
    with psycopg2.connect(database="clients_db", user="postgres", password="12345") as conn:
        createdb(conn)
        add_client(conn, 'Boris', 'Ivanov', 'borisivanov@mail.ru')
        add_phone(conn, 1, '79301506287')
        change_client(conn, 1, first_name='Ivan')
        delete_phone(conn, 1, '79301506287')
        delete_client(conn, 1)
        find_client(conn, 'Ivan')


conn.close()
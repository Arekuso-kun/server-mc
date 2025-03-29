import psycopg2

from config import ConfigManager

config_manager = ConfigManager("config.ini")

USER = config_manager.get_value("Credentials", "user")
PASSWORD = config_manager.get_value("Credentials", "password")
HOST = config_manager.get_value("Credentials", "host")
PORT = config_manager.get_value("Credentials", "port")
DBNAME = config_manager.get_value("Credentials", "dbname")


def get_running_status():
    """Fetch the running status from the database."""

    print("Fetching running status from the database...")

    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )
    cur = conn.cursor()

    cur.execute("SELECT running FROM status WHERE id = 1;")
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None


def get_secret_text():
    """Fetch the secret text from the database."""

    print("Fetching secret text from the database...")

    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )
    cur = conn.cursor()

    cur.execute("SELECT text FROM secret WHERE id = 1;")
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None


def update_running_status(new_status: bool):
    """Update the running status in the database."""

    print(f"Updating running status to {new_status}...")

    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )
    cur = conn.cursor()

    cur.execute("UPDATE status SET running = %s WHERE id = 1;", (new_status,))
    conn.commit()

    cur.close()
    conn.close()

    print(f"Updated running status to {new_status}")


def get_host_name():
    """Fetch the host_name from the database."""

    print("Fetching host_name from the database...")

    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )
    cur = conn.cursor()

    cur.execute("SELECT host_name FROM status WHERE id = 1;")
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None


def update_host_name(new_host_name: str):
    """Update the host_name in the database."""

    print(f"Updating host_name to '{new_host_name}'...")

    conn = psycopg2.connect(
        user=USER, password=PASSWORD, host=HOST, port=PORT, dbname=DBNAME
    )
    cur = conn.cursor()

    cur.execute("UPDATE status SET host_name = %s WHERE id = 1;", (new_host_name,))
    conn.commit()

    cur.close()
    conn.close()

    print(f"Updated host_name to '{new_host_name}'")

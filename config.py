import snowflake.connector

def get_snowflake_connection():
    conn = snowflake.connector.connect(
        user='ASAA',
        password='Maghreb1234',
        account='lsyveyx-vd01067',
        database='CENTRE_MEDECINE',
        schema='CENTREM',
    )
    return conn

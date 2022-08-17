import pymysql
from pandarallel import pandarallel
import pandas as pd
import configHelper

pandarallel.initialize(verbose=0)

config = configHelper.read_config()
data_length_threshold = config.getint("Settings", "data_length_threshold")


def connect_to_db():
    """ Connette al database """
    try:
        db = pymysql.connect(
            host="35.205.34.237",
            port=3306,
            user="root",
            password="smarthome",
            database="smarthomedb1",)
        return db
    except Exception as e:
        print(e)
        return None


def get_data_between_dates(category, start_date, end_date, start_hour, end_hour):
    """ Restituisce un dataframe con i dati tra le date e le ore specificate """
    start_datetime = f"{start_date} {start_hour}"
    if end_hour == "":
        sql = f"SELECT time, {category} FROM home WHERE time BETWEEN '{start_datetime}' AND '{end_date} 23:59:59'"
    else:
        end_datetime = f"{end_date} {end_hour}"
        sql = f"SELECT time, {category} FROM home WHERE time BETWEEN '{start_datetime}' AND '{end_datetime}'"
    try:
        with connect_to_db() as db:
            with db.cursor() as cursor:
                cursor.execute(sql)
                data = pd.DataFrame(cursor.fetchall(), columns=["time", category])

                def parse_date(x):
                    return pd.to_datetime(x, format="%Y-%m-%d %H:%M:%S")

                def parse_value(x):
                    return pd.to_numeric(x, errors="coerce")

                # se la lunghezza del dataframe supera la soglia, viene diviso in più parti e gestito da più thread
                if len(data) < data_length_threshold:
                    data["time"] = data["time"].apply(parse_date)
                    data[category] = data[category].apply(parse_value)
                    return data, category
                else:
                    data["time"] = data["time"].parallel_apply(parse_date)
                    data[category] = data[category].parallel_apply(parse_value)
    except Exception as e:
        print(e)
        return None, None, None
    return data, category


def get_data_between_dates_for_chatbot(category, start_date, end_date):
    """ Restituisce i dati grezzi dal database tra le date specificate """
    sql = f"SELECT time, {category} FROM home WHERE time BETWEEN '{start_date}' AND '{end_date}' ORDER BY time"
    if start_date == end_date:
        sql = f"SELECT time, {category} FROM home WHERE time LIKE '{start_date}%' ORDER BY time"
    try:
        with connect_to_db() as db:
            with db.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
    except Exception as e:
        print(e)
        return None, None
    return data, category


def get_data_between_ids(start_id, end_id):
    """ Restituisce i dati grezzi dal database tra gli id specificati """
    sql = f"SELECT * FROM home WHERE id BETWEEN {start_id} AND {end_id}"
    try:
        with connect_to_db() as db:
            with db.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
    except Exception as e:
        print(e)
        return None, e
    return data, None


def get_categories():
    """ Restituisce una lista delle colonne dal database """
    categories = []
    try:
        with connect_to_db() as db:
            with db.cursor() as cursor:
                cursor.execute("SHOW COLUMNS FROM home")
                categories = [row[0] for row in cursor.fetchall()]
    except Exception as e:
        print(e)
        return None
    return categories


def get_dates():
    """ Restituisce una lista di date e ore dal database """
    try:
        with connect_to_db() as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT time FROM home")
                data = cursor.fetchall()
                hours = sorted(set([row[0].split(" ")[1] for row in data]))
                dates = sorted(set([row[0].split(" ")[0] for row in data]))
    except Exception as e:
        print(e)
        return None, None
    return dates, hours


def get_ids():
    """ Restituisce una lista di ID dal database """
    try:
        with connect_to_db() as db:
            with db.cursor() as cursor:
                cursor.execute("SELECT id FROM home")
                ids = sorted([row[0] for row in cursor.fetchall()])
    except Exception as e:
        print(e)
        return None, e
    return ids, None

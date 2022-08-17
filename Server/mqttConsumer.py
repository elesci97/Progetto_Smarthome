import paho.mqtt.client as mqtt
import pymysql
pymysql.install_as_MySQLdb()
from MySQLdb import connect

import configHelper



config = configHelper.read_config()



class dbConnection:
    def __init__(self):
        self.db = connect(
            host="35.205.34.237",
            port=3306,
            user="root",
            password="smarthome",
            database="smarthomedb1",
        )


        with self.db.cursor() as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS home (id INT AUTO_INCREMENT PRIMARY KEY)"
            )
        print("Connesso al database")
        self.queriesCount = 0

    def disconnect(self):
        print("Disconnesso dal database")
        self.db.close()


    def columnExists(self, column):
        with self.db.cursor() as cursor:
            cursor.execute("SHOW COLUMNS FROM home")
            columns = cursor.fetchall()
        return column in [column[0] for column in columns]

    def on_mqtt_message(self,client, userdata, msg):
        msg = msg.payload.decode("utf-8")
        msg = msg.split(", ")
        msg = [item.split("=") for item in msg]
        #print(msg)
        columns = [
            item[0].replace(" ", "").replace("[", "_").replace("]", "") for item in msg
        ]
        values = [item[-1] for item in msg]
        for column in columns:
            if not self.columnExists(column):
                with self.db.cursor() as cursor:
                    cursor.execute(f"ALTER TABLE home ADD COLUMN {column} VARCHAR(255)")
        columns = ", ".join(columns)
        values = str(values).replace("[", "").replace("]", "")
        self.writeToDb(columns, values)

    def writeToDb(self, columns, values):
           stmt = f"INSERT INTO home ({columns}) VALUES ({values})"
           self.queriesCount += 1
           with self.db.cursor() as cursor:
            cursor.execute(stmt)
           print(f"Scritte {self.queriesCount} righe sul database", end="\r", flush=True)
           self.db.commit()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("home")
    elif rc == 5:
        print(f"Connessione rifiutata: nome utente o password errati. (RC {rc})")
    else:
        print(f"Connessione rifiutata. (RC {rc})")


username = config.get("mqtt", "username")
password = config.get("mqtt", "password")
broker_address = config.get("mqtt", "host")
port = config.getint("mqtt", "port")
client = mqtt.Client()
client.on_connect = on_connect
client.username_pw_set(username, password)
client.connect(broker_address, port)
try:
    db = dbConnection()
    client.on_message = db.on_mqtt_message
    client.loop_forever()
except KeyboardInterrupt:
    db.disconnect()
    print("Uscita")
except Exception as e:
    db.disconnect()
    print(e)

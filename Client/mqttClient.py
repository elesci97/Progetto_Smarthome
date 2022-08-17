import paho.mqtt.client as mqtt
import csvReader
from os import path
import time
import configHelper

config = configHelper.read_config()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"Connesso! (RC {rc})")
    elif rc == 5:
        print(f"Connessione rifiutata: nome utente o password errati. (RC {rc})")
    else:
        print(f"Connessione rifiutata. (RC {rc})")


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


username = config.get("mqtt", "username")
password = config.get("mqtt", "password")
broker_address = config.get("mqtt", "host")
port = config.getint("mqtt", "port")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username, password)
client.connect(broker_address, port)
client.loop_start()
messages = csvReader.read_parse_csv("./data/home.csv")
totalMessages = len(messages)
resume_id = 0
if path.exists("./resume"):
    with open("./resume", "r") as resume:
        resume_id = resume.read()
if resume_id:
    resume_id = int(resume_id)
    print(f"Continuando dall'id {resume_id}")
    messages = messages[resume_id:]
else:
    resume_id = 0
    print("File 'resume' non trovato o file non valido. Inizio dall'id 0")
for message in messages:
    with open("./resume", "w") as resume:
        current_id = (resume_id + messages.index(message)) + 1
        resume.write(str(current_id))
    mqttMessage = ", ".join(f"{k}={v}" for k, v in message.items())
    client.publish("home", mqttMessage)
    #print(mqttMessage)
    time.sleep(0.1)
print("Finished sending messages")

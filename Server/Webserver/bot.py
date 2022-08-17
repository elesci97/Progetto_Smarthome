import dbUtils
from telethon import TelegramClient, Button
from telethon.events import NewMessage, CallbackQuery

api_id = 14913763
api_hash = "1d8028ae4a3dea2f70e35f60320fe98f"

getter = 0

client = TelegramClient(api_id=api_id, api_hash=api_hash, session="anon")

@client.on(NewMessage)
async def handler(e):
    global getter
    if getter >0:
        if getter == 1:
            category = e.text.split(" ")[0]
            date_1 = e.text.split(" ")[1]
            date_2 = e.text.split(" ")[2]
            values, category = dbUtils.get_data_between_dates_for_chatbot(category, date_1, date_2)
            if not values:
                values = "Nessun dato."
            await e.reply(f"{category} tra {date_1} e {date_2}\n\n{values}", buttons=[[Button.inline("Menù Principale", "home")]])
    if e.text == "/start":
        getter = 0
        await e.reply("Benvenuto nel database di SmartHome, utilizza i pulsanti sottostanti per navigare le funzioni.", buttons=[[Button.inline("Mostra Categorie", "show_categories"), Button.inline("Filtra con Data", "data_filter")]])

@client.on(CallbackQuery)
async def handler(e):
    global getter
    if e.data == b"show_categories":
        categories = dbUtils.get_categories()
        categories = ", ".join(categories[2:])
        await e.edit(categories, buttons=[[Button.inline("Menù Principale", "home")]])
    elif e.data == b"home":
        getter = 0
        await e.reply("Benvenuto nel database di SmartHome, utilizza i pulsanti sottostanti per navigare le funzioni.", buttons=[[Button.inline("Mostra Categorie", "show_categories"), Button.inline("Filtra con Data", "data_filter")]])
    elif e.data == b"data_filter":
        getter = 1
        await e.edit("Digita la categoria e le date separandole con uno spazio l'una dall'altra", buttons=[[Button.inline("Menù Principale", "home")]])

client.start()
client.run_until_disconnected()

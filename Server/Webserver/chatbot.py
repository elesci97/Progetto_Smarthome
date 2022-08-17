import dbUtils


def process_message(message):
    message = message.lower()
    if message == "mostra categorie":
        categories = dbUtils.get_categories()
        categories = ", ".join(categories[2:])
        return categories, None, None
    message = message.split(" ")
    if message[0] == "mostra":
        category = message[1]
        if len(message) > 4:
            if "tra" in message:
                start_date = message[3]
                end_date = message[5]
                values, category = dbUtils.get_data_between_dates_for_chatbot(
                    category, start_date, end_date
                )
                if not values:
                    values = "Nessun dato."
                    return (
                        f"{category} tra {start_date} e {end_date}: {values}",
                        None,
                        None,
                    )
                return f"{category} tra {start_date} e {end_date}", values, category
        if "in" in message:
            date = message[3]
            values, category = dbUtils.get_data_between_dates_for_chatbot(
                category, date, date
            )
            if not values:
                values = "Nessun dato."
                return f"{category} in {date}: {values}", None, None
            return f"{category} in {date}", values, category
    return (
        "Il comando non è stato riconosciuto o è presente un errore di sintassi.",
        None,
        None,
    )

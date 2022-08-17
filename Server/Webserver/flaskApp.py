from flask import Flask, render_template, request, redirect
from graphs import get_img
import chatbot
import dbUtils
import os
import users

app = Flask(__name__)
app.config["IMG_FOLDER"] = os.path.join("static", "img")
app.config["USERNAME"] = "admin"
app.config["PASSWORD"] = "password"

print("Caricamento dal database (1/2)...")
categories = dbUtils.get_categories()
print("Fatto.\nCaricamento dal database (2/2)...")
dates, hours = dbUtils.get_dates()
print("Fatto.\nAvvio del server Flask.")


@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if users.is_logged_in(request.remote_addr):
        return render_template("index.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == app.config["USERNAME"] and password == app.config["PASSWORD"]:
            ip = request.remote_addr
            users.login(ip)
            return render_template("index.html")
        else:
            error = "Invalid credentials"
    return render_template("login.html", error=error)


@app.route("/graphs", methods=["GET", "POST"])
def graphs():
    if not users.is_logged_in(request.remote_addr):
        return redirect("/")
    error = None
    if request.method == "POST":
        start_date = request.form.get("start_date", None)
        start_hour = request.form.get("start_hour", None)
        end_date = request.form.get("end_date", None)
        end_hour = request.form.get("end_hour", None)
        category = request.form.get("category", None)
        success, average, median, mode = get_img(category, start_date, end_date, start_hour, end_hour)
        if success:
            img = os.path.join(app.config["IMG_FOLDER"], "graph.png")
            return render_template(
                "graphs.html",
                categories=categories[2:],
                dates=dates,
                hours=hours,
                img=img,
                average=average,
                median=median,
                mode = mode

            )
        else:
            error = "Qualcosa è andato storto. Probabilmente l'intervallo di tempo inserito non è valido."
    return render_template(
        "graphs.html", error=error, categories=categories[2:], dates=dates, hours=hours
    )


@app.route("/chatbot", methods=["GET", "POST"])
def chat():
    if not users.is_logged_in(request.remote_addr):
        return redirect("/")
    if request.method == "POST":
        message = request.form.get("message", None)
        answer, values, category = chatbot.process_message(message)
        return render_template(
            "chatbot.html", answer=answer, values=values, category=category
        )
    return render_template("chatbot.html")


@app.route("/database", methods=["GET", "POST"])
def show_database():
    ids = None
    if not users.is_logged_in(request.remote_addr):
        return redirect("/")
    if not ids:
        ids, error = dbUtils.get_ids()
        totalIDs = len(ids)
        ids = [ids[i : i + 100] for i in range(0, len(ids), 100)]
        for i in range(len(ids)):
            ids[i] = [ids[i][0], ids[i][-1]]
        id_ranges = ["-".join(map(str, x)) for x in ids]
    if error:
        return render_template("database.html", error=error)
    if request.method == "POST":
        id_range = request.form.get("ids")
        start_id, end_id = id_range.split("-")
        data, error = dbUtils.get_data_between_ids(start_id, end_id)
        if error:
            return render_template("database.html", error=error)
        return render_template(
            "database.html",
            data=data,
            start_id=start_id,
            end_id=end_id,
            totalIDs=totalIDs,
            ids=id_ranges,
            categories=categories,
        )
    default_ids = id_ranges[0].split("-")
    start_id = default_ids[0]
    end_id = default_ids[1]
    data, error = dbUtils.get_data_between_ids(start_id, end_id)
    return render_template(
        "database.html",
        data=data,
        start_id=start_id,
        end_id=end_id,
        totalIDs=totalIDs,
        ids=id_ranges,
        categories=categories,
        error=error,
    )


if __name__ == "__main__":
     app.run(host='0.0.0.0', port=8080, debug=True)

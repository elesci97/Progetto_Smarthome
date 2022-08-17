import dbUtils
from io import BytesIO
import matplotlib
import statistics


matplotlib.use("Agg")

from matplotlib import pyplot as plt


def get_img(category, start_date, end_date, start_hour, end_hour):
    data, category = dbUtils.get_data_between_dates(
        category, start_date, end_date, start_hour, end_hour
    )
    if data is None:
        return False, None
    try:
        average = sum(data[category]) / len(data)
    except ZeroDivisionError:
        return False, None
    average = round(average, 2)
    median = statistics.median(data[category])
    mode = statistics.mode(data[category])
    start_datetime = (
        f"{start_date}, {start_hour if start_hour != '' else 'Tutto il giorno'}"
    )
    end_datetime = f"{end_date}, {end_hour if end_hour != '' else 'Tutto il giorno'}"
    plot = data.plot(
        x="time",
        y=category,
        title=f"{category} (da {start_datetime} a {end_datetime})",
        figsize=(10, 5),
    )
    fig = plot.get_figure()
    fig.savefig("./static/graph.png")
    return True, average, median, mode

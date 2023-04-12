import datetime
import json
from endpoints import Url
import matplotlib.dates
from matplotlib import pyplot as plt
import workout
import numpy as np
import random
import requests
from user import get_access_token


def plot_graph(x_data, y_data, date_range):
    # Get start and end date
    # date_range = matplotlib.dates.date2num(date_range)
    plt.clf()
    start = date_range[0]
    end = date_range[-1]

    # Convert date time
    dates = matplotlib.dates.date2num(x_data)

    # Plot x and y
    plt.plot(dates, y_data, color="#000000")

    # Plot trend line

    # Add extra dates to x axis
    n_x = []
    n_y = []
    for date in matplotlib.dates.date2num(date_range):
        x = date
        y = workout.linear_regression(dates, y_data, date)
        n_x.append(x)
        n_y.append(y)
    plt.plot(n_x, n_y, color="#5542ff", linestyle="dashed")

    # Set x and y boundaries
    plt.xlim([start, end])
    plt.gcf().autofmt_xdate()
    # Label
    plt.ylabel("KG")

    return plt.gcf()


if __name__ == "__main__":
    # Get exercises from server

    response = workout.get_exercise_history(31)

    exercises_json = json.loads(response.content.decode("utf-8"))
    eh = []
    for e in exercises_json:
        eh.append(workout.ExerciseHistory(e))

    # Order exercises
    eh = sorted(eh, key=lambda e: e.date_completed)

    eh = []
    for i in range(10):
        eh.append(workout.ExerciseHistory(
            {
                "date_completed": datetime.date(
                    datetime.date.today().year,
                    datetime.date.today().month,
                    datetime.date.today().day - 10 + i
                ),
                "weight_used": 5 + random.randint(0, 10)
            }
        ))

    # Create x and y data
    x = []
    y = []

    # Get highest weight used in each workout
    for e in eh:
        if e.date_completed not in x:
            x.append(e.date_completed)
            y.append(e.weight_used)
        else:
            original_index = x.index(e.date_completed)
            current_weight = y[original_index]
            if e.weight_used > current_weight:
                y[original_index] = e.weight_used

    ranges = []
    for i in range(15):
        ranges.append(
            datetime.date(
            datetime.date.today().year,
            datetime.date.today().month,
            datetime.date.today().day - 10 + i
        ))

    plot_graph(x, y, ranges)

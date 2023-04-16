import datetime
import json
import matplotlib.dates
from matplotlib import pyplot as plt
import workout
import random


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

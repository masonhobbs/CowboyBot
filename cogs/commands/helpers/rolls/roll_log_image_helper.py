from datetime import datetime
from io import BytesIO

import discord
from db.tables.roll_logs import RollLogs
import io
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib as mpl
from PIL import Image

class RollLogImageHelper():

    def __init__(self, user_name: str, logs: list[RollLogs]):
        self.user_name = user_name
        self.logs = logs

    def generate_graph_image(self, graph_type: str) -> Image:
        fig = Figure(figsize=(5,4), dpi=100)
        canvas = FigureCanvasAgg(fig)

        ax = fig.add_subplot()
        roll_dates = []
        lucky_y_axis_count = []
        lucky_count = 0
        unlucky_y_axis_count = []
        unlucky_count = 0

        for log in self.logs:
            if (log.WasLucky):
                lucky_count += 1
            else:
                unlucky_count += 1
            roll_dates.append(log.RollDate)
            lucky_y_axis_count.append(lucky_count)
            unlucky_y_axis_count.append(unlucky_count)

        ax.plot(roll_dates, lucky_y_axis_count,label="Lucky Total", color="green")
        ax.plot(roll_dates, unlucky_y_axis_count,label="Unlucky Total", color="red")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xticks([roll_dates[0], roll_dates[-1]])
        ax.legend()
        ax.set_title(self.user_name + " - " + graph_type + " Roll History")
        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())
        im = Image.fromarray(rgba)
        return im
    
    def generate_all_stats_graph_image(self, graph_type: str) -> Image:
        fig = Figure(figsize=(5,4), dpi=100)
        canvas = FigureCanvasAgg(fig)

        ax = fig.add_subplot()
        roll_dates = []
        lucky_y_axis_count = []
        lucky_count = 0
        unlucky_y_axis_count = []
        unlucky_count = 0

        mapped_dates = map(lambda log: log.RollDate, self.logs)
        unique_dates = list(set(mapped_dates))
        sorted_dates_list = sorted(unique_dates, key=lambda t: datetime.strptime(t, '%m/%d/%Y'))
        for day in sorted_dates_list:
            roll_dates.append(day)
            relevant_logs = list(
                filter(
                    lambda log: log.RollDate == day,
                    self.logs
                )                
            )
            for log in relevant_logs:
                if (log.WasLucky):
                    lucky_count += 1
                else:
                    unlucky_count += 1

            lucky_y_axis_count.append(lucky_count)
            unlucky_y_axis_count.append(unlucky_count)

        ax.plot(roll_dates, lucky_y_axis_count,label="Lucky Total", color="green")
        ax.plot(roll_dates, unlucky_y_axis_count,label="Unlucky Total", color="red")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_xticks([roll_dates[0], roll_dates[-1]])
        ax.legend()
        ax.set_title(self.user_name + " - " + graph_type + " Roll History")
        canvas.draw()
        rgba = np.asarray(canvas.buffer_rgba())
        im = Image.fromarray(rgba)
        return im

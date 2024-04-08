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
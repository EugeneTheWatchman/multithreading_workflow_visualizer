from matplotlib import pyplot as plt
import numpy as np
from logreader import LogReader

class DiagramPlotter:
    def __init__(self, logReader: LogReader, process_color_maper, max_num_of_piles_of_records_per_file = 4, numeber_of_records_to_skip = 0):
        self.process_color_maper = process_color_maper

        self.max_num_of_piles_of_records_per_file = max_num_of_piles_of_records_per_file
        self.logReader = logReader

        self.minmax = np.array([np.inf, -np.inf])
        self.ticks = []
        self.scroll_speed = 3

        self.figure = plt.figure(figsize=(6,9))
        self.axes = self.figure.add_gridspec(right=0.7, top=0.95, bottom=0.05, left=0.07).subplots()

    def draw_all(self):
        self.__draw_points_and_lines()
        self.__draw_slider()
        self.__draw_button()
        self.__set_axis_paramets()


        plt.show()

        # self.logReader.close_files()

    def __set_axis_paramets(self):
        self.axes.set_ylim(self.minmax)
        self.axes.set_yticks(self.ticks)
        self.axes.set_xticks(range(1, self.logReader.number_of_logs + 1))
        self.axes.grid(color='#DDDDDD')

    def __draw_button(self):
        # просто очищает оси
        # нужно чтобы перестал лагать график
        # по-хорошему, нужно бы сохранять последние несколько семплов точек, чтобы их перерисовывать, но я даже не уверен, что этой кнопкой часто будут пользоваться
        button_axes = self.figure.add_axes([0.75, 0.9, 0.2, 0.05])
        self.button = plt.Button(button_axes, 'Clear axes', )
        def on_clicked(event):
            self.axes.clear()
            self.__set_axis_paramets()
            self.figure.canvas.draw_idle()

        self.button.on_clicked(on_clicked)


    def __draw_slider(self):
        min, max = self.minmax

        # slider_axes = self.axes.inset_axes([1.1, 0, 0.25, 1])
        slider_axes = self.figure.add_axes([0.8, 0.05, 0.1, 0.8])
        self.slider = plt.Slider(slider_axes, 'прокрутка времени', valmin=min, valmax=max,
                            valinit=0, valstep=1, orientation='vertical',
                            closedmax=True, closedmin=True)

        # self.__prev_slider_value = 0

        def on_update(slider_value: float|int):
            self.__prev_slider_value = slider_value
            # self.axes.clear()

            upper_lim = self.slider.valmax + slider_value - self.slider.valmin
            self.axes.set_ylim([slider_value, upper_lim])
            if upper_lim > self.minmax[1]:
                self.max_num_of_piles_of_records_per_file += 1
                self.__draw_points_and_lines()
            elif slider_value <= self.minmax[0]:
                return

            if slider_value == self.slider.valmax:
                self.slider.valmax += self.scroll_speed
                self.slider.valmin += self.scroll_speed
                self.slider.ax.set_ylim(self.slider.valmin, self.slider.valmax)
                self.slider.set_val(slider_value)
            elif slider_value == self.slider.valmin:
                self.slider.valmax -= self.scroll_speed
                self.slider.valmin -= self.scroll_speed
                self.slider.ax.set_ylim(self.slider.valmin, self.slider.valmax)
                self.slider.set_val(slider_value)

            # self.figure.canvas.draw_idle()
            self.figure.canvas.flush_events()

        self.slider.on_changed(on_update)
        # slider.valmax = 200

    def __draw_points_and_lines(self):
        min, max = self.minmax
        min += 1; max -= 1
        ticks = []
        while self.logReader.get_max_number_of_records_given_by_each_file() \
            < self.max_num_of_piles_of_records_per_file:
            log_records = self.logReader.get_next_set_of_numbers()
            if len(log_records) == 0:
                break

            for offset, records in log_records.items():
                lines = {}
                for mark, time in records:
                    ticks.append(time)

                    if min > time: min = time
                    if max < time: max = time

                    marker, color, size = self.choose_color_and_marker(mark)
                    self.axes.scatter(offset, time, color=color, marker=marker, s=size)

                    stage, proces_name = mark.split(' ')
                    lines.setdefault(proces_name, []).append(time)
                for proces_name in lines.keys():
                    # if proces_name not in self.process_color_maper.keys(): continue
                    points = lines[proces_name]
                    self.axes.plot([offset] * len(points), points, '-', linewidth=1.5, color=f'{self.process_color_maper.get(proces_name,"none")}')


        self.minmax = np.array([min-1, max+1])
        self.ticks = list(set(ticks + self.ticks))
        self.axes.set_yticks(self.ticks)

    def choose_color_and_marker(self, mark):
        marker = 's'
        max = 255
        n = 5
        color = None
        size = 45

        if mark == 'BEFORE RS':
            n = 4
        elif mark == 'START SYNC':
            n = 3
        elif mark == 'END SYNC':
            marker = '^'
            n = 2
        elif mark == 'START WORK':
            color ='r'
            size = 65
            n = 1
        elif mark == 'END WORK':
            n = 0

        if color is None:
            color = '#' + hex(int(max * n / 5))[2:] * 3

        return marker, color, size
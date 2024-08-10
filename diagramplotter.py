from matplotlib import pyplot as plt
import numpy as np
from logreader import LogReader

class DiagramPlotter:
    def __init__(self, logReader: LogReader, max_num_of_piles_of_records_per_file = 4, numeber_of_records_to_skip = 0):
        self.max_num_of_piles_of_records_per_file = max_num_of_piles_of_records_per_file
        self.logReader = logReader

    def plot(self):
        total_blue_parallel_work = 0
        max = 0
        min = np.inf
        ticks = []
        while self.logReader.get_max_number_of_records_given_by_each_file() \
            < self.max_num_of_piles_of_records_per_file:
            log_records = self.logReader.get_next_set_of_numbers()
            if len(log_records) == 0:
                break

            for offset, records in log_records.items():
                lines = {}
                # prev_red_square = 0
                for mark, time in records:
                    time = int(time)
                    ticks.append(time)
                    if min > time: min = time
                    if max < time: max = time

                    marker, color = self.choose_color_and_marker(mark)
                    plt.scatter(offset, time, color=color, marker=marker, markersize=10)

                    stage, proces_name = mark.split(' ')
                    lines.get(proces_name, []).append(time)
                    # calculating gain from multithreading
                    # if 'START WORK' in mark:
                    #     prev_red_square = time
                    # elif 'END SYNC' in mark:
                    #     diff = prev_red_square - time
                    #     if diff > 0:
                    #         print(time)
                    #         total_blue_parallel_work += diff
                for proces_name in lines.keys():
                    points =  lines[proces_name]
                    plt.plot([offset] * len(points), points, 'r-', linewidth=2)

                plt.xlim([-50, 50])

        # print(f'{total_blue_parallel_work=}')
        # print(f'{sum(self.logReader.number_of_records_given_by_each_file)=}')

        self.logReader.close_files()
        plt.yticks(list(set(ticks)))
        plt.xticks(range(self.logReader.number_of_logs))
        plt.grid()
        plt.show()

    def choose_color_and_marker(self, mark):
        marker = 's'
        max = 255
        n = 5
        color = 'w'

        if mark == 'BEFORE RS':
            n = 4
        elif mark == 'START SYNC':
            n = 3
        elif mark == 'END SYNC':
            marker = '^'
            n = 2
        elif mark == 'START WORK':
            color ='r'
            n = 1
        elif mark == 'END WORK':
            n = 0

        if color == 'w':
            color = '#' + hex(int(max * n / 5))[2:] * 3

        return marker, color
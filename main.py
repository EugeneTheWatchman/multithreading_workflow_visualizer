import io

from matplotlib import pyplot as plt
import numpy as np
import os

class LogReader(object):
    def __init__(self, path=None):
        self.__get_log_files()
        self.number_of_logs = len(self.log_files)

        self.number_of_records_given_by_each_file = []
        self.logs_records_buffer: [[(str, int),],] = []

        self.top_layer_time_buffer = []
        self.top_layer_mark_buffer = []
        for file in self.log_files:
            mark, time = file.readline().split(';')
            time = int(time)
            self.top_layer_time_buffer.append(time)
            self.top_layer_mark_buffer.append(mark)

            self.logs_records_buffer.append([(mark, time)])
            self.number_of_records_given_by_each_file.append(0)
        self.max_number_of_records_per_log = 1 # попытка в оптимизацию

    def __read_next_line_by_time(self):
        # finding least value
        min_element = np.min(self.top_layer_time_buffer)
        min_elements_indexes = np.where(self.top_layer_time_buffer == min_element)[0]
        # если вдруг несколько минимальных элементов
        # исходим из предположения, что уменьшаться значения времени не могут
        for index in min_elements_indexes:
            line = self.log_files[index].readline().split(';')
            if len(line) < 2:
                break
            mark, time = line
            time = int(time)
            self.top_layer_mark_buffer[index] = mark
            self.top_layer_time_buffer[index] = time

            # добавляем новопрочитанное значение
            self.logs_records_buffer[index].append((mark, time))
        else:
            self.max_number_of_records_per_log += 1

    def __is_set_complete(self):
        if self.max_number_of_records_per_log < 5: return []

        lenghts = list(map(len, self.logs_records_buffer))
        self.max_number_of_records_per_log = max(lenghts)
        if self.max_number_of_records_per_log < 5: return []

        enought_lenght_indexes = np.where(np.array(lenghts) >= 5)[0]

        return enought_lenght_indexes

    def get_next_set_of_numbers(self) -> dict:
        output = {}
        for _ in range(100): # try counts
            enought_lenght_indexes = self.__is_set_complete()
            self.__read_next_line_by_time()
            if len(enought_lenght_indexes) > 0:
                break
        else: return output

        for index in enought_lenght_indexes:
            output[index] = self.logs_records_buffer[index][:5]
            self.logs_records_buffer[index][:5] = []
            self.number_of_records_given_by_each_file[index] += 1
        return output

    def __del__(self):
        self.close_files()

    def __is_log_file(self, name: str) -> bool:
        return 'thread' in name

    def __get_log_files(self, path=os.getcwd()):
        self.log_files = [open('/'.join([path, f]), 'r')
                          for f in os.listdir(path)
                          if (os.path.isfile('/'.join([path, f]))
                              and self.__is_log_file(f))]

    def close_files(self):
        for file in self.log_files:
            file.close()

    def get_number_of_records_given_by_each_file(self):
        return max(self.number_of_records_given_by_each_file)

class Plotter:
    def __init__(self, logReader, max_num_of_piles_of_records_per_file = 4, numeber_of_records_to_skip = 0):
        self.max_num_of_piles_of_records_per_file = max_num_of_piles_of_records_per_file
        self.logReader = logReader

    def plot(self):
        total_blue_parallel_work = 0
        max = 0
        min = np.inf
        ticks = []
        while self.logReader.get_number_of_records_given_by_each_file() \
            < self.max_num_of_piles_of_records_per_file:
            log_records = self.logReader.get_next_set_of_numbers()
            if len(log_records) == 0:
                break

            for offset, records in log_records.items():
                SYNCpoints = []
                ENDpoints = []
                prev_red_square = 0
                for mark, time in records:
                    time = int(time)
                    ticks.append(time)
                    if min > time: min = time
                    if max < time: max = time

                    marker, color = self.choose_color_and_marker(mark)
                    plt.scatter(offset, time, color=color, marker=marker)
                    if 'SYNC' in mark:
                        SYNCpoints.append(time)
                    if 'END' in mark:
                        ENDpoints.append(time)
                    if 'START WORK' in mark:
                        prev_red_square = time
                    elif 'END SYNC' in mark:
                        diff = prev_red_square - time
                        if diff > 0:
                            print(time)
                            total_blue_parallel_work += diff
                plt.plot([offset] * len(SYNCpoints), SYNCpoints, 'r-', linewidth=1)
                plt.plot([offset] * len(ENDpoints), ENDpoints, 'b-', linewidth=1.5)

                plt.xlim([-50, 50])

        print(f'{total_blue_parallel_work=}')
        print(f'{sum(logReader.number_of_records_given_by_each_file)=}')

        logReader.close_files()
        plt.yticks(list(set(ticks)))
        plt.xticks(range(logReader.number_of_logs))
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


if __name__ == "__main__":
    logReader = LogReader()
    plotter = Plotter(logReader, 50)
    plotter.plot()



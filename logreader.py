import os
import numpy as np
class LogReader:
    def __init__(self, path=os.getcwd()):
        self.__get_log_files(path)
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

    def __get_log_files(self, path):
        self.log_files = [open('/'.join([path, f]), 'r')
                          for f in os.listdir(path)
                          if (os.path.isfile('/'.join([path, f]))
                              and self.__is_log_file(f))]

    def close_files(self):
        for file in self.log_files:
            file.close()

    def get_number_of_records_given_by_each_file(self):
        return max(self.number_of_records_given_by_each_file)

import os
import time
import glob
import pandas as pd
from memory_profiler import memory_usage
from csvsdataset.csvsdataset import CsvsDataset
from csvsdataset.whereami import TESTDATA


def create_csvsdataset():
    folder_path = TESTDATA
    file_pattern = '*test_data*.csv'
    x_columns_pattern = r'col_[012]'
    y_column = r'col_3'
    dataset = CsvsDataset(folder_path, file_pattern, x_columns_pattern=x_columns_pattern, y_column=y_column)
    return dataset


def create_and_load_csvsdataset():
    dataset = create_csvsdataset()
    all_data = [dataset[i] for i in range(len(dataset))]


def create_and_query_csvsdataset():
    dataset = create_csvsdataset()
    all_data = [dataset[i] for i in range(500)]


def create_and_query_csvsdataset_twice():
    dataset = create_csvsdataset()
    all_data = [dataset[i] for i in range(500)]
    all_data = [dataset[i] for i in range(500)]


def create_and_query_csvsdataset_thrice():
    dataset = create_csvsdataset()
    all_data = [dataset[i] for i in range(500)]
    all_data = [dataset[i] for i in range(12000,12500)]



def load_pandas():
    folder_path = TESTDATA
    file_pattern = os.path.join(folder_path, '*test_data*.csv')
    all_data = pd.concat(pd.read_csv(file, usecols=lambda col: col.startswith('col_')) for file in glob.glob(file_pattern))
    data = all_data.values


def measure_performance(func):
    start_time = time.perf_counter()
    mem_usage = memory_usage((func, ), max_usage=True)
    end_time = time.perf_counter()
    print(f"{func.__name__}: Execution time: {end_time - start_time:.3f} seconds, Memory usage: {mem_usage:.2f} MiB")


if __name__ == "__main__":
    measure_performance(create_csvsdataset)
    measure_performance(load_pandas)
    #measure_performance(create_and_load_csvsdataset)
    measure_performance(create_and_query_csvsdataset)
    measure_performance(create_and_query_csvsdataset_twice)
    measure_performance(create_and_query_csvsdataset_thrice)

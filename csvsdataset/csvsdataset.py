import os
import glob
import pandas as pd
from torch.utils.data import Dataset
from collections import OrderedDict
import re


class CsvsDataset(Dataset):

    def __init__(self, folder_path, file_pattern,
                        x_columns=None, x_columns_pattern=None,
                        y_column=None, y_columns=None, y_columns_pattern=None, cache_capacity=3):
        self.file_paths = sorted(glob.glob(os.path.join(folder_path, file_pattern)))
        if len(self.file_paths)==0:
            raise ValueError('Expression {file_pattern} has no matches in {folder_path}')
        self.num_rows_per_file = [self._get_num_rows(file) for file in self.file_paths]
        self.total_rows = sum(self.num_rows_per_file)

        # Get the column names from the first file
        first_file = self.file_paths[0]
        all_columns = pd.read_csv(first_file, nrows=0).columns

        # Filter the columns based on the x and y patterns
        if x_columns is None:
            x_regex = re.compile(x_columns_pattern)
            self.x_columns = sorted(filter(x_regex.match, all_columns))
        else:
            self.x_columns = x_columns
            for x_col in x_columns:
                if x_col not in all_columns:
                    raise ValueError('Cannot find '+x_col)

        if y_column is not None:
            y_columns = [y_column]
        if y_columns is None:
            y_regex = re.compile(y_columns_pattern)
            self.y_columns = sorted(filter(y_regex.match, all_columns))
        else:
            self.y_columns = y_columns

        self.cumulative_rows = self._calculate_cumulative_rows()
        self.cache = OrderedDict()
        self.cache_capacity = cache_capacity

    @staticmethod
    def _get_num_rows(file_path):
        with open(file_path, 'r') as f:
            num_lines = sum(1 for _ in f) - 1  # Subtract 1 for the header row
        return num_lines

    def _calculate_cumulative_rows(self):
        cumulative_rows = [0]
        for file_path in self.file_paths:
            num_rows = sum(1 for _ in open(file_path)) - 1  # -1 to exclude header row
            cumulative_rows.append(cumulative_rows[-1] + num_rows)
        return cumulative_rows

    def _get_file_and_row_indices(self, index):
        file_idx = next(i for i, num_rows in enumerate(self.cumulative_rows) if num_rows > index) - 1
        row_idx = index - self.cumulative_rows[file_idx]
        return file_idx, row_idx

    def __getitem__(self, index):
        file_index, row_index = self._get_file_and_row_indices(index)

        # Check cache
        if file_index in self.cache:
            df = self.cache[file_index]
        else:
            # Read the file and cache it
            file_path = self.file_paths[file_index]
            df = pd.read_csv(file_path)
            self.cache[file_index] = df

            # Evict the least recently used item from the cache if it exceeds the cache capacity
            if len(self.cache) > self.cache_capacity:
                _ = self.cache.popitem(last=False)

        x_data = df.loc[row_index, self.x_columns].to_numpy()
        y_data = df.loc[row_index, self.y_columns].to_numpy()

        return x_data, y_data

    def __len__(self):
        return self.cumulative_rows[-1]  # Total number of rows across all files

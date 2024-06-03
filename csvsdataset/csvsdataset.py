import os
import glob
import pandas as pd
from torch.utils.data import Dataset
from collections import OrderedDict
import re


class CsvsDataset(Dataset):

    def __init__(self, folder_path, file_pattern, x_columns=None, x_columns_pattern=None,
                 y_column=None, y_columns=None, y_columns_pattern=None, cache_capacity=3,
                 sort_x_columns=False, sort_y_columns=False):
        """
              Initializes the CsvsDataset class, which handles a dataset spread across multiple CSV files.

              Parameters:
                  folder_path (str): The path to the folder containing the CSV files.
                  file_pattern (str): The pattern to match the CSV files in the folder.
                  x_columns (list, optional): Specific columns to be used as input features. Defaults to None.
                  x_columns_pattern (str, optional): Regex pattern to match the input feature columns. Used if x_columns is None. Defaults to None.
                  y_column (str, optional): Specific column to be used as the target feature. Defaults to None.
                  y_columns (list, optional): Specific columns to be used as target features. Defaults to None.
                  y_columns_pattern (str, optional): Regex pattern to match the target feature columns. Used if y_columns is None. Defaults to None.
                  cache_capacity (int, optional): The number of CSV files to keep in memory cache. Defaults to 3.
                  sort_x_columns bool:  If True, this will sort the columns in a natural order defined below (e.g. x1, x2, x10, x11,...)
                  sort_y_columns bool:  If True, this will sort the columns in a natural order defined below (e.g. x1, x2, x10, x11,...)

              Raises:
                  ValueError: If no files match the file_pattern in the folder_path.
        """


        self.file_paths = sorted(glob.glob(os.path.join(folder_path, file_pattern)))
        if len(self.file_paths) == 0:
            raise ValueError(f'Expression {file_pattern} has no matches in {folder_path}')

        self.num_rows_per_file = [self._get_num_rows(file) for file in self.file_paths]
        self.total_rows = sum(self.num_rows_per_file)

        first_file = self.file_paths[0]
        all_columns = pd.read_csv(first_file, nrows=0).columns

        # Determine the input feature columns
        if x_columns is None:
            x_regex = re.compile(x_columns_pattern)
            self.x_columns = list(filter(x_regex.match, all_columns))
            if sort_x_columns:
                self.x_columns = sorted(self.x_columns, key=natural_sort_key)
        else:
            self.x_columns = x_columns
            for x_col in x_columns:
                if x_col not in all_columns:
                    raise ValueError(f'Cannot find {x_col}')

        # Determine the target feature columns
        if y_column is not None:
            y_columns = [y_column]
        if y_columns is None:
            y_regex = re.compile(y_columns_pattern)
            self.y_columns = list(filter(y_regex.match, all_columns))
            if sort_y_columns:
                self.y_columns = sorted(self.y_columns, key=natural_sort_key)
        else:
            self.y_columns = y_columns

        self.cumulative_rows = self._calculate_cumulative_rows()
        self.cache = OrderedDict()
        self.cache_capacity = cache_capacity

    @staticmethod
    def _get_num_rows(file_path, chunksize=10 ** 6):
        row_count = 0
        for chunk in pd.read_csv(file_path, chunksize=chunksize, usecols=[0]):
            row_count += len(chunk)
        return row_count

    def _calculate_cumulative_rows(self):
        cumulative_rows = [0]
        for file_path in self.file_paths:
            num_rows = self._get_num_rows(file_path)
            cumulative_rows.append(cumulative_rows[-1] + num_rows)
        return cumulative_rows

    def _get_file_and_row_indices(self, index):
        if index < 0 or index >= self.total_rows:
            raise IndexError("Index out of bounds")
        file_idx = next((i for i, num_rows in enumerate(self.cumulative_rows) if num_rows > index), None)
        if file_idx is None:
            raise IndexError("Index out of bounds")
        file_idx -= 1
        row_idx = index - self.cumulative_rows[file_idx]
        return file_idx, row_idx

    def __getitem__(self, index):
        file_index, row_index = self._get_file_and_row_indices(index)
        if (df := self.cache.get(file_index)) is None:
            file_path = self.file_paths[file_index]
            df = pd.read_csv(file_path)
            self.cache[file_index] = df
            if len(self.cache) > self.cache_capacity:
                self.cache.popitem(last=False)

        x_data = df.iloc[row_index][self.x_columns].to_numpy().astype(float)
        y_data = df.iloc[row_index][self.y_columns].to_numpy().astype(float)
        return x_data, y_data

    def __len__(self):
        return self.cumulative_rows[-1]


def natural_sort_key(s, _nsre=re.compile('([0-9]+)')):
    """
    A helper function to generate a sort key for natural sorting.

    Natural sorting ensures that strings containing numbers are sorted in a way
    that humans expect. For example, 'file10' comes after 'file2' rather than
    'file1', 'file10', 'file2', etc.

    Parameters:
    s (str): The input string to be sorted.
    _nsre (re.Pattern): A compiled regular expression pattern used to find numbers in the string.

    Returns:
    list: A list of integers and lowercase text segments from the input string.

    Example:
    >>> sorted(['file1', 'file10', 'file2'], key=natural_sort_key)
    ['file1', 'file2', 'file10']
    """
    # Split the string by the regular expression pattern, which separates numbers from text.
    # The resulting list contains alternating segments of text and numbers.
    return [int(text) if text.isdigit() else text.lower() for text in re.split(_nsre, s)]


# Example usage:
if __name__ == "__main__":
    filenames = ['file1', 'file10', 'file2']
    print("Before sorting:", filenames)
    sorted_filenames = sorted(filenames, key=natural_sort_key)
    print("After sorting:", sorted_filenames)

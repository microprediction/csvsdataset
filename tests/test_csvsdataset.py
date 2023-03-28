from csvsdataset.csvsdataset import CsvsDataset
from csvsdataset.whereami import TESTDATA
import os


def test_csvsdataset():
    folder_path = TESTDATA
    print(f"TESTDATA folder: {folder_path}")
    print(f"Files in TESTDATA folder: {os.listdir(folder_path)}")

    file_pattern = '*test_data*.csv'
    x_columns_pattern = r'col_\d+'
    y_column = 'col_2'

    dataset = CsvsDataset(folder_path=folder_path, file_pattern=file_pattern,
                          x_columns_pattern=x_columns_pattern, y_column=y_column,
                          cache_capacity=1)

    print(f"Number of files in dataset: {len(dataset.file_paths)}")
    print(f"Total number of rows in dataset: {len(dataset)}")

    assert len(dataset) > 0, "The dataset should not be empty"
    x_data, y_data = dataset[0]
    assert x_data.shape[0] == 500, "The x_data should have 500 columns"
    assert y_data.shape[0] == 1, "The y_data should have 1 column"

    # Test cache functionality
    assert 1 not in dataset.cache, "Index 0 should not be in the cache initially"
    x_data, y_data = dataset[3000]
    x_data, y_data = dataset[3033]
    x_data, y_data = dataset[3038]
    assert 0 not in dataset.cache


if __name__=='__main__':
    test_csvsdataset()

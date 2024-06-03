import pytest
import pandas as pd
import re
from csvsdataset import CsvsDataset, natural_sort_key
from csvsdataset.whereami import TESTDATA
import os

@pytest.fixture
def dataset():
    folder_path = TESTDATA
    file_pattern = '*test_data*.csv'
    x_columns_pattern = r'col_\d+'
    y_column = 'col_2'
    return CsvsDataset(folder_path=folder_path, file_pattern=file_pattern,
                       x_columns_pattern=x_columns_pattern, y_column=y_column, cache_capacity=1)

def test_initialization(dataset):
    assert len(dataset.file_paths) > 0, "The dataset should have at least one file"
    assert len(dataset) > 0, "The dataset should not be empty"

def test_column_selection(dataset):
    first_file = dataset.file_paths[0]
    df = pd.read_csv(first_file)
    x_columns = [col for col in df.columns if re.match(r'col_\d+', col)]
    print(f"Expected x_columns: {x_columns}")
    print(f"Actual x_columns: {dataset.x_columns}")
    assert dataset.x_columns == x_columns, "X columns should match the pattern"
    assert dataset.y_columns == ['col_2'], "Y column should be 'col_2'"

def test_column_selection_with_sorting():
    folder_path = TESTDATA
    file_pattern = '*test_data*.csv'
    x_columns_pattern = r'col_\d+'
    y_column = 'col_2'
    dataset = CsvsDataset(folder_path=folder_path, file_pattern=file_pattern,
                          x_columns_pattern=x_columns_pattern, y_column=y_column,
                          cache_capacity=1, sort_x_columns=True, sort_y_columns=True)

    first_file = dataset.file_paths[0]
    df = pd.read_csv(first_file)
    x_columns = sorted([col for col in df.columns if re.match(r'col_\d+', col)], key=natural_sort_key)
    print(f"Expected sorted x_columns: {x_columns}")
    print(f"Actual sorted x_columns: {dataset.x_columns}")
    assert dataset.x_columns == x_columns, "Sorted X columns should match the pattern"
    assert dataset.y_columns == ['col_2'], "Y column should be 'col_2'"

def test_getitem_shape(dataset):
    x_data, y_data = dataset[0]
    assert x_data.shape[0] == len(dataset.x_columns), "X data shape should match the number of X columns"
    assert y_data.shape[0] == len(dataset.y_columns), "Y data shape should match the number of Y columns"

def test_cache_functionality(dataset):
    initial_cache_length = len(dataset.cache)
    dataset[0]  # Access first element to trigger cache
    assert len(dataset.cache) == initial_cache_length + 1, "Cache should have one item after first access"
    dataset[1000]  # Access another element
    assert len(dataset.cache) == initial_cache_length + 1, "Cache should still have one item (capacity=1)"
    dataset[0]  # Access first element again
    assert len(dataset.cache) == initial_cache_length + 1, "Cache should still have one item after re-accessing"

def test_large_index_access(dataset):
    index = len(dataset) - 1
    x_data, y_data = dataset[index]
    assert x_data.shape[0] == len(dataset.x_columns), "X data shape should match the number of X columns for large index"
    assert y_data.shape[0] == len(dataset.y_columns), "Y data shape should match the number of Y columns for large index"

def test_invalid_index_access(dataset):
    with pytest.raises(IndexError):
        _ = dataset[len(dataset)]  # Accessing out of bounds index should raise IndexError

def test_file_not_found():
    with pytest.raises(ValueError):
        _ = CsvsDataset(folder_path='invalid_path', file_pattern='*.csv', x_columns_pattern=r'col_\d+', y_column='col_2')

def test_no_matching_files():
    with pytest.raises(ValueError):
        _ = CsvsDataset(folder_path=TESTDATA, file_pattern='no_matching_files*.csv', x_columns_pattern=r'col_\d+', y_column='col_2')

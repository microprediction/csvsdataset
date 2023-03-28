# csvsdataset

`csvsdataset` is a Python library designed to simplify the process of working with multiple CSV files as a single dataset. The primary functionality is provided by the `CsvsDataset` class in the `csvsdataset.py` module.

## Installation

To install the `csvsdataset` library, simply run:

```bash
pip install csvsdataset
```

## Usage

        from csvsdataset.csvsdataset import CsvsDataset
        
        # Initialize the CsvsDataset instance
        dataset = CsvsDataset(folder_path="path/to/your/csv/folder",
                              file_pattern="*.csv",
                              x_columns=["column1", "column2"],
                              y_column="target_column")
        
        # Iterate over the dataset
        for x_data, y_data in dataset:
            # Your processing code here
            pass
        
        # Access a specific item in the dataset
        x_data, y_data = dataset[42]

### Memory frugality
Only data from a small number of csv files are maintained in memory. The
rest is discarded on a LRU basis. This class is intended for use
when a very large number of data files exist which cannot be loaded into
memory conveniently. 

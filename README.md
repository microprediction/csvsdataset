# csvsdataset

`csvsdataset` is a Python library designed to simplify the process of working with multiple CSV files as a single dataset. The primary functionality is provided by the `CsvsDataset` class in the `csvsdataset.py` module.

This was written by ChatGPT4 as mentioned [here](https://www.linkedin.com/posts/petercotton_chatgpt4-opensource-python-activity-7047184874163597312-JTr3?utm_source=share&utm_medium=member_desktop). Issues will be cut and paste into a session. It is an experiment in semi-autonomous code maintenance.

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

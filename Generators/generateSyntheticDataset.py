import pandas as pd

inputDataFramePath = './Input CSV Metadata/20240101_metadata.csv'
original_df = pd.read_csv(inputDataFramePath, delimiter=';')
header = original_df.columns.tolist()
firstRow = original_df.iloc[0].values

num_tables = 1000
num_columns = 100
num_rows = 100000

data = []
for table_index in range(num_tables):
    firstRowCopy = firstRow.copy()
    firstRowCopy[0] = f'TEST_TABLE{table_index}'
    for columns in range(num_columns):
        firstRowCopy[5] = f'COLUMN{columns}'
        data.append(firstRowCopy.copy())

synthetic_dataset = pd.DataFrame(data, columns=header)
outputPath = './Input CSV Metadata/syntheticDataset100K.csv'
synthetic_dataset.to_csv(outputPath, index=False, sep=';')

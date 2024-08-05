import pandas as pd
import yaml
from typing import Dict, List
import time

def read_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path, sep=';')

def map_data_type(data_type: str) -> str:
    type_mapping = {
        'VARCHAR2': 'string',
        'NUMBER': 'decimal(38,0)',
        'DATE': 'date',
    }
    return next((standard for key, standard in type_mapping.items() if key in data_type), 'string')

def process_table(df: pd.DataFrame, source: Dict) -> List[Dict]:
    table_name = df.iloc[0]['table_name']
    # Process columns using apply
    columns = df.apply(lambda row: {
        "name": row['COLUMN_NAME'].lower(),
        "data_type": map_data_type(row['DATA_TYPE']),
        **({"date_format": row['DATA_FORMAT']} if pd.notna(row['DATA_FORMAT']) else {}),
        **({"is_nullable": True} if row['NULLABLE'] == 'Y' else {})
    }, axis=1).tolist()
    
    # Return the processed table information
    return {
        "name": table_name,
        "source": source,
        "columns": columns,
        "primary_key": ["unid"],
        "cdc_column": "dml_flag",
        "cdc_type": "soft"
    }

def create_sources_and_anchors(df: pd.DataFrame) -> Dict:
    tables = []
    sources = {}
    source_groups = df.groupby(['FILE_NAME', 'DECIMAL_SEPARATOR', 'FILE_TYPE'])
    for source_id, ((file_name, decimal_separator, file_type), group) in enumerate(source_groups, start=1):
        source_key = f"source{source_id}"
        source_data = {
            "load_type": "delta",
            "file_pattern": file_name,
            "partition_pattern": r'(\d+(?:\.\d+)?)_(?:\d+\D+)$',
            "params": {
                "decimal_separator": decimal_separator,
                "format": file_type.lower()
            }
        }
        sources[source_key] = source_data
        for table_name, table_group in group.groupby('table_name'):
            table_info = process_table(table_group, source=source_data)
            tables.append(table_info)

    return tables

def generate_metadata_yaml(df: pd.DataFrame) -> str:
    tables = create_sources_and_anchors(df)
    # Create the metadata structure
    metadata = {
        "version": 2,
        "name": "dwh",
        "tables": tables
    }
    yaml_content = yaml.dump(metadata, sort_keys=False, default_flow_style=False)
    return yaml_content

def generate_gdpr_yaml(df: pd.DataFrame) -> str:
    df = df.astype({'GDPR_FLAG': str, 'COLUMN_NAME': str})
    gdpr = [
        {
            "name": table_name,
            "personal_data": {
                "hash": df[df['GDPR_FLAG'].str.strip().str.upper() == 'TRUE']['COLUMN_NAME'].str.lower().tolist()
            }
        }
        for table_name, df in df.groupby('table_name')
        if not df[df['GDPR_FLAG'].str.strip().str.upper() == 'TRUE'].empty
    ]
    gdpr_content = yaml.dump(gdpr, sort_keys=False)
    return gdpr_content

def save_yaml(file_path: str, content: str) -> None:
    with open(file_path, 'w') as file:
        file.write(content)
        
def save_time_speeds(file_path: str, time_list: list, algorithm: str, dataset: str) -> None:
    with open(file_path, 'a') as file:
        file.write("\n")
        file.write(f"Algorithm: {algorithm}\n")
        file.write(f"Dataset: {dataset}\n")
        file.write("Time speeds (in seconds):\n")
        for time_elapsed in time_list:
            file.write(f"{time_elapsed}\n")

def main(csv_file_path: str, metadata_yaml_path: str, gdpr_yaml_path: str) -> None:
    df = read_csv(csv_file_path)
    time_list = []
    
    for _ in range(10):
        beginTime = time.time()
        metadata_yaml = generate_metadata_yaml(df)
        gdpr_yaml = generate_gdpr_yaml(df)
        timeElapsed = time.time() - beginTime
        time_list.append(timeElapsed)
    print(time_list)
        
    algorithm = "Pandas"
    dataset = "32 rows, 2 tables"
    save_time_speeds('timeSpeeds.txt', time_list, algorithm, dataset)
    # save_yaml(metadata_yaml_path, metadata_yaml)
    # save_yaml(gdpr_yaml_path, gdpr_yaml)
    
    
# Example usage
if __name__ == "__main__":
    main('./Input CSV Metadata/20240101_metadata.csv', 'metadataPandas.yaml', 'gdprPandas.yaml')
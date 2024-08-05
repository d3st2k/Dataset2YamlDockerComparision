import pandas as p
import yaml

majorVersion = 2
minorVersion = 0

version = f'{majorVersion}.{minorVersion}'
folderPath = "schema_versions"
outputFileName = f'schema%{version}'
outputFileType = "yaml"
schema = {
    "title": "YAML Schema",
    "description": "A metaschema generated from an example dataset.",
    "attributes": []
}
data = p.read_csv("BankChurners.csv")

# Global variables
required_attributes = [
    "CLIENTNUM",
    "Attrition_Flag",
    "Gender",
    "Dependent_count",
    "Education_Level",
    "Marital_Status",
    "Income_Category",
    "Card_Category",
    "Credit_Limit"
]

# Functions
def infer_type(data_type):
    return type(data_type).__name__

def apply_gdpr(column):
    if column in ["name", "Card_Category", "passport number", "income", "cultural profile", "internet Protocol"]:
        return True

def setConstraints(column):
    constraints = {}
    if column == "full name":
        constraints = {
            "required": True,
            "description": "Name of the person",
            "minimum_length": 1,
            "maximum_length": 100
        }
    elif column == "Customer_Age":
        constraints = {
            "range": "integer",
            "required": True,
            "minimum_length": 1,
            "maximum_length": 100,
            "minimun_value": 18,
            "maximum_value": 65
        }
    elif column in required_attributes:
        constraints = {
            "required": True,
            "minimum_length": 1,
            "maximum_length": 100
        }
    return constraints

def process_data(column, dataValue):
    dataType = infer_type(dataValue)
    gdpr = apply_gdpr(column)
    constraints = setConstraints(column)
    return [dataType, gdpr, constraints]

# Generating yaml constraints
for column in data.columns: 
    [dataType, gdpr, constraints] = process_data(column, data[column].iloc[0])
    columnSchema = {
        "name": column,
        "type": dataType,
        "constraints": constraints,
        "gdpr": gdpr
    }
    schema["attributes"].append(columnSchema)

# Dumping the schema dictionary to a yaml file and writing it out
with open(f'{folderPath}/{outputFileName}.{outputFileType}', 'w') as file:
    yaml.dump(schema, file, sort_keys=False, version=(majorVersion, minorVersion))


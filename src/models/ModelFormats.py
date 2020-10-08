from enum import Enum

class ModelFormats(Enum):
    DICT = "dict"
    DF = "dataframe"
    JSON = "json"
    SAVE = "save"
    SAVE_CSV = "save_json"
    SAVE_JSON = "save_csv"
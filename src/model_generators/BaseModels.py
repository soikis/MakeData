# TODO documentation
from collections import Counter
import pandas as pd
import numpy as np
import json

DICT = "dict"
DF = "dataframe"
JSON = "json"
SAVE = "save" # TODO save for every type



class BaseModel():

    model_counter = Counter()

    def __init__(self, model_gens, seed=None, name=None):
        
        self.gens_dict = {gen.name: gen for gen in model_gens}

        my_name = self.__class__.__name__
        if name is not None:
            self.name = name
        else:
            self.name = f"{my_name}{BaseModel.model_counter[my_name]}"

        BaseModel.model_counter[my_name] += 1

    def __call__(self, *args, **kwargs):
        return self.generate_data(*args, **kwargs)

    def generate_data(self, k, return_type=DICT, split_samples=True, index_key=None):
        generated_data = {name: generator(k) for name, generator in self.gens_dict.items()}

        for data_col in generated_data.values():
            if not isinstance(data_col, tuple):
                raise TypeError(f"") # TODO do this and give every single on of them

        if return_type == DICT:
            if split_samples:
                return BaseModel._invert_dict(generated_data, k, index_key)

            return generated_data

        if return_type == DF:
            if index_key is not None:
                return pd.DataFrame.from_dict(generated_data).set_index(index_key)
            return pd.DataFrame.from_dict(generated_data)

        if return_type == JSON:
            if split_samples:
                return json.dumps(BaseModel._invert_dict(generated_data, k, index_key), ensure_ascii=False)

            return json.dumps(generated_data, ensure_ascii=False)

    @staticmethod
    def _invert_dict(orig_dict, k, index_key):
        samples_generator = zip(*orig_dict.values())
        keys = orig_dict.keys()

        if index_key is None:
            index_check_function = True
            index_values = range(k)
        else:
            index_check_function = lambda k: k != index_key
            index_values = orig_dict[index_key]

        return_dict = {index: {key: value for key, value in zip(keys, sample_values) if index_check_function} 
                        for index, sample_values in zip(index_values, samples_generator)}

        return return_dict

    
    def reset_seeds(self, seed):
        for name in self.gens_dict:
            self.generate_data[name].reset_seed(seed)

from collections import Counter
import pandas as pd
import numpy as np
import json
from .ModelFormats import ModelFormats
from collections import OrderedDict


class BaseModel():
    """A basic data generation model.

       A basic data model to generate data from. It is comparable to django's models or, if you don't know it,
       a pandas DataFrame, or SQL table.

        Parameters
        ----------
        generators : list of GeneratorObjects
            A list of ``GeneraotrObject``s that the model will use for data generation. For every single data sample generated,
            the model will use every ``GeneratorObject`` in the order they were introduced in the list.
        seed : int or float or str, optional
            A random seed to use on all of the generators. If a generator already has a seed, it will overwrite it if ``overwrite_seeds=True``.
        overwrite_seeds : bool, optional
            If true, overwrite all of the generators random seeds, else, add a seed to ones that don't have any seed.
            **BE CAREFULL, CHANING A ``GeneratorObject``'S SEED IS AN INPLACE ACTION**
        name : str, optional
            The name of the model, if not provided, it will be infered from the number of models existing in the project.

        Attributes
        ----------
        model_counter : collections.Counter
            A counter used to keep track of how many ``Model``s of each type are created.
        gens_dict : collections.OrderedDict
            A dictinoary that is used to access all the generators that exist inside this model.
        name : str, optional
            The name of a ``Model``.

        Examples
        --------
        Using ``BaseModel`` to create a simple person generator and overwriting all of the generator's seeds:

        >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
        >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
        >>> from data_generators.formatted_generators.NameGenerator import NameGenerator
        >>> from models.BaseModels import BaseModel
        >>> nameGen = NameGenerator(locale="en_INTER", default_format_name="ffl", name="FullName")
        >>> ageGen = IntegerGenerator(18, 38, name="Age",seed=2)
        >>> birthdayGen = DateGenerator("1-1-1990", "31-12-1999", name="Birthday")
        >>> personModel = BaseModel([nameGen, ageGen, birthdayGen], seed=42, overwrite_seeds=True, name="PersonModel")
        >>> personModel(5)
        {0: {'FullName': 'Alexa Stillwell', 'Age': 19, 'Birthday': '22-11-1990'}, 
        1: {'FullName': 'Landry Bloor', 'Age': 33, 'Birthday': '26-09-1997'}, 
        2: {'FullName': 'Janiyah Penney', 'Age': 31, 'Birthday': '17-07-1996'}, 
        3: {'FullName': 'Christina Cordrey', 'Age': 26, 'Birthday': '22-05-1994'}, 
        4: {'FullName': 'Yaretzi Boone', 'Age': 26, 'Birthday': '30-04-1994'}}
    """

    model_counter = Counter()

    def __init__(self, generators, seed=None, overwrite_seeds=False, name=None):
        
        self.gens_dict = OrderedDict()
        for gen in generators:
            if seed is not None:
                if overwrite_seeds:
                    gen.reset_seed(seed)
                else:
                    if gen.seed is None:
                        gen.reset_seed(seed)
            self.gens_dict[gen.name] = gen

        my_type = self.__class__.__name__
        if name is not None:
            self.name = name
        else:
            self.name = f"{my_type}{BaseModel.model_counter[my_type]}"

        BaseModel.model_counter[my_type] += 1

    
    def __call__(self, *args, **kwargs):
        """Call self.generate_data to generate data."""
        return self.generate_data(*args, **kwargs)

    def generate_data(self, k, return_type=ModelFormats.DICT, split_samples=True, index_key=None, drop_index=True, index_attempts=1, save_path=None):
        """Generate k samples from this model.

            Parameters
            ----------
            k : int
                How many samples to generate
            return_type : str, optional
                What type of data to return, if returning anything at all. Look at the see also section to look for more details.
            split_samples : bool, optional
                Wheter to split the generated data to individual sampels (like a DataFrame) or to keep them in distinguished lists.
            index_key : str, optional
                A name of a generator to use as a key/index. The ``name`` attribute of the ``GeneratorObject`` will be used.
            drop_index : bool, optional
                If ``True``,  remove ``index_key`` from the data sample, else, keep it as index as data. If no ``index_key`` is used, it is irrelevant.
            index_attempts : int 
                How many times to try to generate a unique index/key before raising an exception.
            save_path : str
                If 'return_type' is about saving data, this is the path to the file you want to save it in.

            See Also
            --------
            ModelFormats : An Enum class that has all the possible values for ``return_type``, use this class when you choose a ``return_type`` value.

            Examples
            --------
            Make a model that generates data for how many likes a person did on a certain date and set the names as index:

            >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> from data_generators.formatted_generators.NameGenerator import NameGenerator
            >>> from models.BaseModels import BaseModel
            >>> nameGen = NameGenerator(locale="en_INTER", default_format_name="ffl", name="FullName")
            >>> likesGen = IntegerGenerator(0, 100, name="Age")
            >>> dayGen = DateGenerator("1-1-2019", "31-12-2019", name="DayOfYear")
            >>> personModel = BaseModel([nameGen, likesGen, dayGen], seed=42, overwrite_seeds=True, name="LikesModel")
            >>> personModel(5, index_key="FullName", index_attempts=20)
            {'Alexa Stillwell': {'Age': 8, 'DayOfYear': '02-02-2019'}, 
            'Landry Bloor': {'Age': 77, 'DayOfYear': '09-10-2019'}, 
            'Janiyah Penney': {'Age': 65, 'DayOfYear': '27-08-2019'}, 
            'Christina Cordrey': {'Age': 43, 'DayOfYear': '09-06-2019'}, 
            'Yaretzi Boone': {'Age': 43, 'DayOfYear': '07-06-2019'}}
        """
        # TODO add uniqueness to generators
        generated_data = {name: generator(k) for name, generator in self.gens_dict.items()}

        if index_key is not None:
            attempts_counter = 0
            while len(set(generated_data[index_key])) != k and attempts_counter < index_attempts:
                generated_data[index_key] = self.gens_dict[index_key](k)
            if len(set(generated_data[index_key])) != k:
                raise IndexError(f"Couldn't create a unique index with 'GeneratorObject' named {index_key}, " \
                                f"even after {index_attempts}, make sure it can generate enough data (has big enough range, big enough data source etc.)")

        for data_col in generated_data.values():
            if not isinstance(data_col, tuple):
                raise TypeError(f"Data generated by 'GeneratorObject' with name '{data_col}' is not of type 'tuple', " \
                                    "if it is a generotr you wrote, check that the 'GeneratorObject' returns a tuple.")

        if return_type == ModelFormats.DICT:
            if split_samples:
                return BaseModel._invert_dict(generated_data, index_key, drop_index)
            return generated_data

        if return_type == ModelFormats.DF:
            if index_key is not None:
                return pd.DataFrame.from_dict(generated_data).set_index(index_key, drop=drop_index)
            return pd.DataFrame.from_dict(generated_data)

        if return_type == ModelFormats.JSON:
            if split_samples:
                return json.dumps(BaseModel._invert_dict(generated_data, index_key, drop_index), ensure_ascii=False)
            return json.dumps(generated_data, ensure_ascii=False)
        
        if return_type == ModelFormats.SAVE_CSV:
            if save_path is None:
                raise ValueError("'save_path' can't be None if you intend to save a file.")
            if index_key is not None:
                pd.DataFrame.from_dict(generated_data).set_index(index_key, drop=drop_index).to_csv(save_path)
            pd.DataFrame.from_dict(generated_data).to_csv(save_path)
        
        if return_type == ModelFormats.SAVE_JSON:
            if save_path is None:
                raise ValueError("'save_path' can't be None if you intend to save a file.")
            if split_samples:
                json.dump(BaseModel._invert_dict(generated_data, index_key, drop_index), fp=save_path, ensure_ascii=False)
            json.dump(generated_data, fp=save_path, ensure_ascii=False)

    @staticmethod
    def _invert_dict(orig_dict, index_key=None, drop_index=True):
        """Split a column based model to individual samples (similar to a pandas DataFrame).

            Parameters
            ----------
            orig_dict : dict
                The original dictionary to transpose.
            index_key : str, optional
                A name of a generator to use as a key/index. The ``name`` attribute of the ``GeneratorObject`` will be used.
            drop_index : bool, optional
                If ``True``,  remove ``index_key`` column from the data sample, else, keep it as index as data.
        """
        samples_generator = zip(*orig_dict.values())
        keys = orig_dict.keys()

        if index_key is None:
            index_check_function = lambda k: True
            return_dict = {index: {key: value for key, value in zip(keys, sample_values) if index_check_function(key)} 
                        for index, sample_values in enumerate(samples_generator)}
        else:
            index_check_function = lambda k: k != index_key
            return_dict = {index: {key: value for key, value in zip(keys, sample_values) if index_check_function(key)} 
                        for index, sample_values in zip(orig_dict[index_key], samples_generator)}
        
        return return_dict

    
    def reset_seeds(self, seed):
        """Reset the seed for **all** (overwrites existing ones) of this models ``GeneratorObject``s.

            Parameters
            ----------
            seed : int or float or str, optional
                A random seed to use on **all** of the generators.

            See Also
            --------
            data_generators.BaseGenerators.reset_seed : An important note about resetting seed values - you shouldn't or at least be careful about it.

            Examples
            --------
            >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> from data_generators.formatted_generators.NameGenerator import NameGenerator
            >>> from models.BaseModels import BaseModel
            >>> nameGen = NameGenerator(locale="en_INTER", default_format_name="ffl", name="FullName")
            >>> ageGen = IntegerGenerator(18, 38, name="Age",seed=2)
            >>> birthdayGen = DateGenerator("1-1-1990", "31-12-1999", name="Birthday")
            >>> personModel = BaseModel([nameGen, ageGen, birthdayGen], seed=42, overwrite_seeds=True, name="PersonModel")
            >>> personModel(5)
            {0: {'FullName': 'Alexa Stillwell', 'Age': 19, 'Birthday': '22-11-1990'}, 
            1: {'FullName': 'Landry Bloor', 'Age': 33, 'Birthday': '26-09-1997'}, 
            2: {'FullName': 'Janiyah Penney', 'Age': 31, 'Birthday': '17-07-1996'}, 
            3: {'FullName': 'Christina Cordrey', 'Age': 26, 'Birthday': '22-05-1994'}, 
            4: {'FullName': 'Yaretzi Boone', 'Age': 26, 'Birthday': '30-04-1994'}}
            >>> personModel = BaseModel([nameGen, ageGen, birthdayGen], seed=42, overwrite_seeds=True, name="PersonModel")
            >>> personModel.reset_seeds(2)
            >>> personModel(5)
            {0: {'Full Name': 'Holland Shibley', 'Age': 34, 'Birthday': '16-05-1998'}, 
            1: {'Full Name': 'Raegan Hoge', 'Age': 23, 'Birthday': '13-08-1992'}, 
            2: {'Full Name': 'Aubree Bolte', 'Age': 20, 'Birthday': '04-02-1991'}, 
            3: {'Full Name': 'Amina Freel', 'Age': 23, 'Birthday': '25-12-1992'}, 
            4: {'Full Name': 'Adrianna Maulden', 'Age': 26, 'Birthday': '19-02-1994'}}
        """
        for generator in self.gens_dict.values():
            generator.reset_seed(seed)

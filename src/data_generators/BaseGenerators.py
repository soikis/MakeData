from re import findall, compile as recompile
from os.path import join as syspath_join
from json import load as json_load
from inspect import isfunction
from numpy.random import default_rng
from .GeneratorDecorators import GeneratingFunction
from collections import Counter
from .GeneratorExceptions import FormatError, EmptySourceError, NoDefaultFormatError, FormatNotFoundError
from utils.FunStr.FunStr import parameters_list


class GeneratorObject():
    """The basic generator class.

        .. note::
            This class is intended for inheritence purposes only.

        .. note::
            The naming convention of a new ``GeneratorObject`` is TypeOrName(Singular[Integer-v|Integers-x]) + Generator, like: ``FormattedGenerator``.
            TODO move this

        .. note::
        A ``GeneratorObject`` will return a tuple, meaning it will generate an immutable result.

        Parameters
        ----------
        seed : int or float or str, optional
            The random seed used to seed the ``random_generator`` of a ``GeneratorObject``.
        name : str, optional
            The name of a ``GeneratorObject``

        Attributes
        ----------
        generators_counter : collections.Counter
            A counter used to keep track of how many ``GeneratorObject``s of each type are created.
        random_generator : numpy.random.default_rng
            The random generator used by all of the inheriting classes (``numpy.random.default_rng``).
        name : str, optional
            The name of a ``GeneratorObject``

        Examples
        --------
        Using a ``GeneratorObject`` as a callable to generate data and giving it a name and a random seed:

        >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
        >>> gen = HumanNameGenerator(locale="en_INTER", default_format_name="lmf", name="names",seed=42)
        >>> gen(5)
        ['Bodley Saint', 'Rumbley Evan', 'Nettle Demetrius', 'Hickcox Judah', 'Herbertson Everett']
        >>> gen.name
        names
    """
    generators_counter = Counter()

    def __init__(self, seed=None, name=None):

        self.seed = seed

        if seed is not None:
            self.random_generator = default_rng(seed)
        else:
            self.random_generator = default_rng()

        # If name is not provided - generate one based on the generator's type and the generators_counter value of it.
        my_type = self.__class__.__name__
        if name is not None:
            self.name = name
            self.generated_name = False
        else:
            self.name = f"{my_type}{GeneratorObject.generators_counter[my_type]}"
            self.generated_name = True # TODO add to documentation
        GeneratorObject.generators_counter[my_type] += 1

    def reset_seed(self, seed):
        """**Recreate** this ``GeneratorObject``'s ``random_generator`` with a seed.

            .. warning:: 
                Only use this method if you absolutely have to. 
            It will change the ``random_generator`` of the instance which might generate values you did not expect (no, not because they are random, ha-ha).

            Parameters
            ----------
            seed : {None, int, array_like[ints], numpy.random.SeedSequence, numpy.random.BitGenerator, numpy.random.Generator}
                The seed to set the new ``random_generator`` with.
            
            See Also
            --------
            model_generators.BaseModels.set_seeds : Reset the seeds of all the ``GeneratorObject``s in the model. # TODO move this to point the other way around.
            
            Examples
            --------
            Changing the random generator seed:

            <numpy.random._pcg64.PCG64 object at 0x0000023CC54EA300>
            >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
            >>> gen = IntegerGenerator((0,5), seed=42)
            >>> gen.random_generator._bit_generator
            <numpy.random._pcg64.PCG64 object at 0x0000023CC54EAEB0>
            >>> gen.reset_seed(21)
            >>> gen.random_generator._bit_generator
            <numpy.random._pcg64.PCG64 object at 0x0000023CC54EAEB0>
        """
        self.seed = seed
        self.random_generator = default_rng(seed)

    @GeneratingFunction
    def __call__(self, k, *args, **kwargs):
        """A helper method to make it possible to generate data straight from the object.
            
            Simply calls this ``GeneratorObject``'s ``generate_data`` method.

            Parameters
            ----------
            k : int
                Sample count to generate.
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments.

            Returns
            -------
            list
                All the samples concatenated to a list.
                The returned list is returned from ``generate_data``
            
            See Also
            --------
            GeneratorDecorators.GeneratingFunction : Convert a result of a function to a list.
            
            Examples
            --------
            Generating 5 ints with ``IntegerGenerator``:

            >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
            >>> gen = IntegerGenerator(-5, 5, seed=42)
            >>> gen(5)
            [-5, 2, 1, -1, -1]
        """
        return self.generate_data(k, *args, **kwargs)

    def _data_generator(self, k, *args, **kwargs):
        """Generate data for this ``GeneratorObject``.

            .. warning:: 
                All children of ``GeneratorObject`` need to implement this method or pass it to the next one.
            
            This is where the data generation logic sits.
            Logic can be as simple as in ``IntegerGenerator`` or complex as in ``DateGenerator``"""
        raise NotImplementedError

    def generate_data(self, k, *args, **kwargs):
        """Execute any general logic for ``GeneratorObject`` before calling it's ``_data_generator``.
            
            .. note:: 
                When implementing this method, wrap it with a @GeneratingFunction decorator to avoid any unexpected behaviours.

            .. warning:: 
                All children of ``GeneratorObject`` need to implement this method or pass it to the next one.

            This method handles the general logic of the ``GeneratorObject`` before it's (or it's child's) ``_data_generator`` actually generates the data.
            If there is no general logic, just call ``_data_generator`` 
            
            .. warning:: 
                If you do not implement this method with at least calling ``_data_generator``, you won't be able to use __call__ unless you overwrite it too.
                Meaning, you want be able to generate data by simply writing ``GeneratorObject(k)``.

            This can be used for example in places such as the ``FromJSONSimpleGenerator``, 
            where it is used to set the format and break the sentence for the _data_generator. TODO change this part when I finish FunStr

            Examples
            --------
            What would happen if ``NumericGenerator``, didn't implement generate_data.
            >>> from data_generators.numeric_generators.BaseGenerators import NumericGenerator
            >>> gen = NumericGenerator(0,5)
            >>> gen(2)
            Traceback (most recent call last):
                ......
            NotImplementedError
            >>> 
        """
        raise NotImplementedError

class FormattedGenerator(GeneratorObject):
    """A base class for all the ``GeneratorObject``s that use formatting.

        .. note::
            This class is intended for inheritence purposes only.

        A ``GeneratorObject`` that uses formatting might be as complicated as a sentence ``GeneratorObject`` and as simple as a money ``GeneratorObject``,
        which will be different from ``IntegerGenerator`` or 'FloatGenerator' because it will contain a currency sign (exmp. $) or currency name (exmp. ILS).

        Parameters
        ----------
        default_format : str, optional
            The default format to use in this ``GeneratorObject``. **(An actual format, not name of format)**
            Will be used as the format in every generation, if none is specified.
        default_format_name : str, optional
            The default format to use in this ``GeneratorObject`` **by name**.
            Either use 'default_format', or 'default_format_name', otherwise an ValueError is raised.
        generate_format_symbols : bool, optional
            If True, try to generate symbols for all the formats.
            May be used with a given parameter 'ignore_errors' that will be passed to the generating function from '**kwargs'.
        default_must : bool, optional
            If true, and ``default_format`` doesn't exist in the object raise NoDefaultFormatError.
            Use it when a default format is necessary, regardless of existing ``formats`` dict.
        *args
                Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
            May contain 'ignore_errors' -> bool which will be used with '_create_formats_symbols'
        
        Attributes
        ----------
        formats : dict
            A dictionary of the available formats for this ``GeneratorObject``.
            Where 'name_of_format': (``FunStr`` or 'format') are the 'key':'value', respectively.
            Look at the See Also section to understand ``FunStr``s.
            If you use a 'format'  it can be something like a date format e.g. "%d-%m-%Y" (Depending on what you generate ofcourse).
            **Do not set a format manuallly e.g. ``GeneratorObject.formats["name"] = "format"``, it might break the integrity of the ``GeneratorObject``**
            # TODO add a function to add format.
        formats_symbols : dict, optional
            A dictionary with a mapping between an abbreviations of a format and it's full name.
            Where 'abbreviation': 'name_of_format' are the 'key':'value', respectively.
        default_format : str, optional
            A default 'FunStr' or format.
        
        See Also
        --------
        data_generators.formatted_generators.DateGenerator: An example of a generator that uses a specialized format.
    """
    def __init__(self, default_format=None, default_format_name=None, generate_format_symbols=False, default_must=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # TODO check everything about default formats
        self.formats = getattr(self, "formats", dict())
        if "default" in self.formats:
            raise ValueError("Can't use the name 'default' in the formats dict, it is a reserved name.")
        self.formats_symbols = getattr(self, "formats_symbols", dict())
        if generate_format_symbols:
            self._create_formats_symbols(kwargs.pop("ignore_errors", False))

        if default_format is not None and default_format_name is not None:
            raise ValueError(f"Either set 'default_format' or 'default_format_name', not both.")
        if default_format is not None:
            self.default_format = default_format
        if default_format_name is not None:
            self.default_format = self.get_format(default_format_name)
        
        if default_must:
            try:
                self.default_format
            except AttributeError:
                raise NoDefaultFormatError(self)

    def _create_formats_symbols(self, ignore_errors=False):
        """Create symbols for every format that doesn't have a symbol.

            Takes the first letter after every _ aswell as first letter of the format name.

            Parameters
            ----------
            ignore_errors : bool, optional
                If True, instead of raising an error when an existing symbol is generated, continue to the next symbol, else raise ValueError.

            Raises
            ------
            ValueError
                If a generated symbol already exists and 'ignore_errors' is False.
        """
        not_symbolised_formats = (f[0] for f in self.formats_names if f[1] == "")
        for frmt in not_symbolised_formats:
            symbol = "".join(s[0] for s in frmt.split("_"))
            if symbol not in self.formats_symbols:
                self.formats_symbols[symbol] = frmt
            elif not ignore_errors:
                # TODO maybe make it iterate for removing a single letter and checking agai, only if didn't find, generate error.
                raise ValueError(f"Can't create symbol '{symbol}' for format '{frmt}' since a symbol like that already exists.")

    @property
    def formats_names(self):
        """A sorted list of tuples of all the formats names and their abbreviations.

            Returns
            -------
            list
                A 'list' of 'tuples' where 'tuple[0]' is a format name and 'tuple[1]' is a symbol.
            
            Examples
            --------
            Getting the format names of a ``GeneratorObject``:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = HumanNameGenerator(locale="en_US")
            >>> gen.formats_names
            [('female_first_and_last', 'ffl'), ('init_female_first_and_last', 'iffl'), 
            ('init_male_first_and_last', 'imfl'), ('last_and_female_first', 'lff'), 
            ('last_and_male_first', 'lmf'), ('male_first_and_last', 'mfl')]
        """
        res = []
        for form in self.formats.keys():
            try:
                abrv_index = list(self.formats_symbols.values()).index(form)
            except ValueError:
                res.append((form, ""))
                continue
            abrv_key = list(self.formats_symbols.keys())[abrv_index]
            res.append((form, abrv_key))
        return sorted(res, key=lambda f: f[0])

    @property
    def formats_templates(self):
        """A list of the actual formats sorted by their names.

            Returns
            -------
            list
                A 'list' of formats sorted by their names.
            
            Examples
            --------
            Getting the format names of a ``GeneratorObject``:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = HumanNameGenerator(locale="en_US")
            >>> gen.formats_templates
            ['{female_first_names} {last_names}', '{female_first_names[0]}. {last_names}', 
            '{male_first_names[0]}. {last_names}', '{last_names} {female_first_names}', 
            '{last_nammes} {male_first_names}', '{male_first_names} {last_names}']
        """
        return [self.formats[format_name[0]] for format_name in self.formats_names]

    # TODO change everything to use get_format
    def get_format(self, name="default"):
        """The format for this ``GeneratorObject`` using 'name'.
            
            Parameters
            ----------
            name: str, optional
                The name of the format, either a symbol or a name.
                By default it will get the 'default_format' of a ``GeneratorObject``. 
                Be careful, some generators might not have a default format.

            Returns
            -------
            str
                The format corresponding to name.
            NoneType
                None.
            
            Raises
            ------
            NoDefaultFormatError
                If no format corresponding the given name is found.

            Examples
            --------
            Get the default format of a DateGenerator:

            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> gen = DateGenerator(datetime(2020, 10, 6), datetime(2020, 10, 8))
            >>> gen.get_fromat
            "%d-%m-%Y"
        """
        if name == "default":
            try:
                return self.default_format
            except AttributeError:
                raise NoDefaultFormatError(self)
        
        elif name is not None and isinstance(name, str):
            if name in self.formats_symbols:
                name = self.formats_symbols[name]
                return self.formats[name]
            elif name in self.formats:
                return self.formats.get(name, None)

        raise FormatNotFoundError(name, self)
    
    def _data_generator(self, k, format_used, *args, **kwargs):
        """formatted data generator"""
        raise NotImplementedError
    
    # TODO Allow for multi-variable replacement by using FunStr
    @GeneratingFunction
    def generate_data(self, k, format_name="default", *args, **kwargs):
        """Get the generation format and call generator function.

            Parameters
            ----------
            k : int
                How many samples to generate.
            format_name : str, optional
                **Name** of the format to use when generating data.
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments.

            Returns
            -------
            list
                All the generated values concatenated to a single list.

            Examples
            --------
            Using ``generate_data`` without a format to generate data using it's ``default_format``:

            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> gen = DateGenerator(datetime(2020, 10, 6), datetime(2020, 10, 8), seed=42)
            >>> gen.generate_data(5)
            ['06-10-2020', '07-10-2020', '07-10-2020', '06-10-2020', '06-10-2020']

            Setting ``default_data`` using ``default_format`` and using ``generate_data`` to generate data:

            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> gen = DateGenerator(datetime(2020, 10, 6), datetime(2020, 10, 8), default_format="%Y-%m-%d %H:%M:S", seed=42)
            >>> gen.generate_data(5)
            ['2020-10-06 04:17:02', '2020-10-07 13:08:59', '2020-10-07 07:25:09', '2020-10-06 21:03:58', '2020-10-06 20:47:05']
        """
        format_used = self.get_format(format_name)

        return self._data_generator(k=k, format_used=format_used, *args, **kwargs)

class FileSourcedGenerator(FormattedGenerator):
    """A base class for all the ``GeneratorObject``s that use data from files.

        A ``GeneratorObject`` might be read from multiple file types such as *.json*,*.csv*,*.txt* etc..

        Parameters
        ----------
        file_parser : file parsing function
            The ``function`` of a file parser. (Just the function, without brackets)
        locale : str
            The locale for this file. Will be used to automatically find the locale file.
        file_path : bool, optional
            The path to the file to draw data from.
            **Only ``locale`` or ``file_path`` can be used, not both.**
        *args
                Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
        
        Attributes
        ----------
        locale : str, optional
            The locale of the generator.
        source_path: str
            The path to the source of the generator. The value is generated using file_path or locale.
        data: dict
            The data used for generation.

        Raises
        ------
        ValueError
            If both or none of ``locale`` and ``file_path`` are used.
            
        See Also
        --------
        TODO conventions for locale files
    """
    def __init__(self, file_parser, locale=None, file_path=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if locale is not None and file_path is not None:
            raise ValueError(f"Only one of the variables locale-{locale} and file_path-{file_path} can be specified.")

        if locale is not None:
            self.locale = locale

            generator_name = self.__class__.__name__
            self.source_path = syspath_join("DataSources", f"{generator_name}", f"{self.locale}.json")
            
            if self.generated_name:
                self.name = generator_name + "_" + locale

        elif file_path is not None:
            self.source_path = file_path
        else:
            raise ValueError(f"One of locale-{locale} or file_path-{file_path} must be instantiated.")
        
        
        with open(self.source_path, "r") as source:
            self.data = file_parser(source)
        if not self.data:
            raise EmptySourceError()

    def _data_generator(self, k, format_used, *args, **kwargs):
        """Generate k samples with a given format.

            Parameters
            ----------
            k : int
                How many samples to generate.
            format_used : str
               The str to generate data based on. TODO maybe FunStr
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments.

            Returns
            -------
            list
                All the generated values concatenated to a single list.
        """
        # TODO add choice for replacement for uniqueness
        generated_data = []
        
        data_keys = parameters_list(format_used)

        # TODO when FunStr will be done, it will return k formats and then we need to rewrite this function so it will fit this case. Such as get data for every single format.
        # Generating all values for the formatting.
        all_dataset = []
        for key in data_keys:
            all_dataset.append(self.random_generator.choice(self.data[key], size=k))
        
        # Formatting
        for data_point in zip(*all_dataset):
            data_point_parameters = {k: v for k, v in zip(data_keys, data_point)}
            generated_data.append(format_used.format(**data_point_parameters))

        return generated_data

    # TODO Allow for multi-variable replacement by using FunStr
    @GeneratingFunction
    def generate_data(self, k, format_name="default", *args, **kwargs):
        """Get the generation format and call generator function.

            Parameters
            ----------
            k : int
                How many samples to generate.
            format_name : str, optional
                **Name** of the format to use when generating data.
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments.

            Returns
            -------
            list
                All the generated values concatenated to a single list.

            Raises
            ------
            EmptySourceError
                If ``data`` is empty for some reason.

            Examples
            --------
            Using ``generate_data`` to generate data with specific format name:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = HumanNameGenerator(locale="en_INTER", seed=42)
            >>> gen.generate_data(5, "iffl")
            ['A. Stillwell', 'L. Bloor', 'J. Penney', 'C. Cordrey', 'Y. Boone']

            Setting ``default_data`` using ``default_format_name`` and using ``generate_data`` to generate data with ``default_format``:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = HumanNameGenerator(locale="en_INTER", default_format_name="lff", seed=42)
            >>> gen.generate_data(5)
            ['Bodley Belle', 'Rumbley Ivy', 'Nettle Armani', 'Hickcox Alaina', 'Herbertson Arianna']
        """
        if not self.data:
            raise EmptySourceError()
        
        # TODO maybe change format_used to formatting.
        format_used = self.get_format(format_name)

        return self._data_generator(k,format_used, *args, **kwargs)   

class LocalizedFileSourceGenerator(FileSourcedGenerator): # TODO add this thing and make documentation. aswell as delete from filesourcegenrator
    pass

class FromJSONGenerator(FileSourcedGenerator):
    """A formatted generator that uses a .json file for it's source.

        All of the methods, parameters and attributes for this ``GeneratorObject`` are listed in FileSourcedGenerator.

        See Also
        --------
        FileSourcedGenerator : All the relevant functions and explenations of __init__ are detailed there.
    """
    def __init__(self, **kwargs):
        super().__init__(json_load, **kwargs)

class NumericGenerator(GeneratorObject):
    """A base class for all numeric ``GeneratorObject``s.

        .. note::
            This class is intended for inheritence purposes only.

        If you want to create for example a phone number generator,
        **don't** use this generator, even though you are trying to generate numbers,
        they have a structured format, so you need to use ``FormattedGenerator`` for example.

        Parameters
        ----------
        low : numeric type
            Minimum value for the generator.
        high : numeric type
            Maximum number for the generator.
        *args
                Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
        
        Attributes
        ----------
        low : numeric type
            Minimum value for the generator.
        high : numeric type
            Maximum number for the generator.
        
        Raises
        ------
        ValueError
            If ``low``>``high``
        
        Examples
        --------
        Generating data with a generator that inherits from NumericGenerator:

        >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
        >>> gen = IntegerGenerator(-7, 10, seed=42)
        >>> gen(5)
        [-6, 6, 4, 0, 0]

        See Also
        --------
    """
    def __init__(self, low, high, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if low > high:
            raise ValueError(f"The minimum value={low} can't be bigger than the maximum value={high} of the generator {low}>{high}")
        self.low = low
        self.high = high
        
    def _data_generator(self, k):
        """numeric data generator"""
        raise NotImplementedError

    @GeneratingFunction
    def generate_data(self, k, *args, **kwargs):
        """Call the generator function.

            Parameters
            ----------
            k : int
                How many samples to generate.
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments.

            Returns
            -------
            list
                All the generated values concatenated to a single list.

            Examples
            --------
            Using ``generate_data`` to generate data:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = IntegerGenerator(-7, 10, seed=42)
            >>> gen.generate_data(5)
            [-6, 6, 4, 0, 0]


        """
        # TODO add choice for replacement for uniqueness
        return self._data_generator(k, *args, **kwargs)

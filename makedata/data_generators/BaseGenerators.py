from re import findall, compile as recompile
from os.path import isfile, isdir, join as syspath_join
from json import load as json_load
from inspect import isfunction
from numpy.random import default_rng
from .GeneratorDecorators import GeneratingFunction
from collections import Counter
from .GeneratorExceptions import FormatError, EmptySourceError, NoDefaultFormatError, FormatNotFoundError
from string import Formatter
import os
from re import compile as recompile, match


# This compiled regex is used to clean parameter names in 'FormattedGenerator' formats, such as param[0]->param.
FORMAT_KEY_CLEANING = recompile(r"[a-zA-Z_][\d\w]*")


class GeneratorObject():
    """The basic generator class.

        .. note::
            * The naming convention of a new ``GeneratorObject`` is TypeOrName(Singular[Integer-v|Integers-x]) + Generator, like: ``FormattedGenerator``.
            * This class is intended for inheritence purposes only.
            * A ``GeneratorObject`` will return a tuple, meaning it will generate an immutable result.
        
        .. warning::
            When implementing a new ``GeneratorObject`` that outputs data (not something you inherit from),
            you must overwrite the _data_generator method, aswell as give it a @GeneratingFunction decorator. If you won't it might break functionallity.

        Parameters
        ----------
        seed : int or float or str, optional
            The random seed used to seed the ``random_generator`` of a ``GeneratorObject``.
        name : str, optional
            The name of a ``GeneratorObject``

        Attributes
        ----------
        generators_counter : collections.Counter
            A counter used to keep track of how many ``GeneratorObject`` of each type are created.
        random_generator : numpy.random.default_rng
            The random generator used by all of the inheriting classes (``numpy.random.default_rng``).
        name : str
            The name of a ``GeneratorObject``
        is_generated_name : bool
            True if the name was generated by the constructor, False if it was provided.

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
            self.is_generated_name = False
        else:
            self.name = f"{my_type}{GeneratorObject.generators_counter[my_type]}"
            self.is_generated_name = True
        GeneratorObject.generators_counter[my_type] += 1

    def reset_seed(self, seed):
        """**Recreate** this ``GeneratorObject``'s ``random_generator`` with a seed.

            .. warning:: 
                Only use this method if you absolutely have to.

            It will change the ``random_generator`` of the instance which might generate values you did not expect (no, not because they are random, ha-ha).

            Parameters
            ----------
            seed : None or int or array_like[ints] or numpy.random.SeedSequence, numpy.random.BitGenerator
                The seed to set the new ``random_generator`` with.
            
            Examples
            --------
            Changing the random generator seed:

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
        
            Simply calls this ``GeneratorObject``'s ``_preprocess_data`` method.

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
                The returned list is returned from ``_preprocess_data``
            
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
        return self._preprocess_data(k, *args, **kwargs)

    @GeneratingFunction
    def _data_generator(self, k, *args, **kwargs):
        """Generate data for this ``GeneratorObject``.

            .. note:: 
                When implementing this method, wrap it with a @GeneratingFunction decorator to avoid any unexpected behaviours.

            .. warning:: 
                All children of ``GeneratorObject`` need to implement this method or pass it to the next one or a NotImplementedError will be raised.
            
            This is where the data generation logic sits.
            Logic can be as simple as in ``IntegerGenerator`` or complex as in ``DateGenerator``
        """
        raise NotImplementedError

    def _preprocess_data(self, k, *args, **kwargs):
        """Execute any general logic for ``GeneratorObject`` before calling it's ``_data_generator``.
            
            .. warning:: 
                All children of ``GeneratorObject`` need to implement this method or pass it to the next one.

            This method handles the general logic of the ``GeneratorObject`` before it's (or it's child's) ``_data_generator`` actually generates the data.
            If there is no general logic, just call ``_data_generator`` 
            
            .. warning:: 
                If you do not implement this method with at least calling ``_data_generator``, you won't be able to use __call__ unless you overwrite it too.
                Meaning, you want be able to generate data by simply writing ``GeneratorObject(k)``.

            This can be used for example in places such as the ``FileSourceGenerator``, 
            where it is used to set the format and break the sentence for the ``_data_generator``.

            Examples
            --------
            What would happen if ``NumericGenerator``, didn't implement _preprocess_data.
            >>> from data_generators.numeric_generators.BaseGenerators import NumericGenerator
            >>> gen = NumericGenerator(0,5)
            >>> gen(2)
            Traceback (most recent call last):
                ......
            NotImplementedError
        """
        raise NotImplementedError

class FormattedGenerator(GeneratorObject):
    """A base class for all the ``GeneratorObject`` that use formatting.

        .. note::
            This class is intended for inheritence purposes only.

        A ``GeneratorObject`` that uses formatting might be as complicated as a sentence ``GeneratorObject`` and as simple as a money ``GeneratorObject``,
        which will be different from ``IntegerGenerator`` or ``FloatGenerator`` because it will contain a currency sign (exmp. $) or currency name (exmp. ILS).

        Parameters
        ----------
        default_format : str, optional
            | The default format to use in this ``GeneratorObject``. **(An actual format, not name of format)**
            | Will be used as the format in every generation, if none is specified.
        default_format_name : str, optional
            | The default format to use in this ``GeneratorObject`` **by name**.
            | Either use ``default_format``, or ``default_format_name``, otherwise an ValueError is raised.
        generate_format_symbols : bool, optional
            | If True, try to generate symbols for all the formats.
            | May be used with a given parameter ``ignore_errors`` that will be passed to the generating function from ``kwargs``.
        default_must : bool, optional
            | If true, and ``default_format`` doesn't exist in the object raise NoDefaultFormatError.
            | Use it when a default format is necessary, regardless of existing ``formats`` dict.
        ignore_errors : bool, optional
            | If ``True``, instead of raising an error when an existing symbol is generated, continue to the next symbol, else raise ``ValueError``.
            | Has no effect if ``generate_format_symbols`` is ``False``.
        *args
            Variable length argument list
        **kwargs
            | Arbitrary keyword arguments. 
        
        Raises
        ------
        NoDefaultFormatError
            If ``default_must`` is True, and no default format is found or set.

        Attributes
        ----------
        formats : dict
            | A dictionary of the available formats for this ``GeneratorObject``,
            | where 'name_of_format': 'format' are the 'key':'value', respectively.
            | 'format' any string formatting you use.
            | **Do not set a format manuallly e.g. ``GeneratorObject.formats["name"] = "format"``, it might break the integrity of the ``GeneratorObject``**
        formats_symbols : dict, optional
            | A dictionary with a mapping between a symbol (abbreviation) of a format and it's full name.
            | Where 'symbol': 'name_of_format' are the 'key':'value', respectively.
        default_format : str, optional
            A string format.
        
        See Also
        --------
        data_generators.formatted_generators.DateGenerator: An example of a generator that uses a specialized format.
    """

    def __init__(self, default_format=None, default_format_name=None, generate_format_symbols=False, default_must=False, ignore_errors=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get the formats from the child class, to understand more, read about python inheritence and class attributes.
        self.formats = getattr(self, "formats", dict())

        # If in a child class, the formats dict contains the format name "default", raise an exception.
        if "default" in self.formats:
            raise ValueError("Can't use the name 'default' in the formats dict, it is a reserved name.")
        
        # Get the format symbols from the child class.
        self.formats_symbols = getattr(self, "formats_symbols", dict())
        if generate_format_symbols:
            self._create_formats_symbols(ignore_errors)

        if default_format is not None and default_format_name is not None:
            raise ValueError(f"Either set 'default_format' or 'default_format_name', not both.")
        
        # Try to set a default format.
        elif default_format is not None:
            self.default_format = default_format
            self.has_default = True
        elif default_format_name is not None:
            self.default_format = self.get_format(default_format_name)
            self.has_default = True

        else:
            self.has_default = False
        
        # If 'default_must' is True, make sure there is a default format, else raise NoDefaultFormatError.
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
                If ``True``, instead of raising an error when an existing symbol is generated, continue to the next symbol, else raise ``ValueError``.

            Raises
            ------
            ValueError
                If a generated symbol already exists and 'ignore_errors' is ``False``.
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
        f_names = []
        for frmt in self.formats.keys():
            try:
                abrv_index = list(self.formats_symbols.values()).index(frmt)
            except ValueError:
                f_names.append((frmt, ""))
                continue
            symbol = list(self.formats_symbols.keys())[abrv_index]
            f_names.append((frmt, symbol))
        return sorted(f_names, key=lambda f: f[0])

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
                If no default format is found.
            FormatNotFoundError
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
        
        elif isinstance(name, str):
            try:
                if name in self.formats_symbols:
                    name = self.formats_symbols[name]
                return self.formats[name]
            except KeyError:
                raise FormatNotFoundError(name, self)

        raise FormatNotFoundError(name, self)

    def _data_generator(self, k, format_used, *args, **kwargs):
        """formatted data generator
        """
        raise NotImplementedError
    
    def _preprocess_data(self, k, format_name="default", *args, **kwargs):
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
            Using ``_preprocess_data`` without a format to generate data using it's ``default_format``:

            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> gen = DateGenerator(datetime(2020, 10, 6), datetime(2020, 10, 8), seed=42)
            >>> gen(5)
            ['06-10-2020', '07-10-2020', '07-10-2020', '06-10-2020', '06-10-2020']

            Setting ``default_format`` using ``default_format`` parameter in the constructor:

            >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
            >>> gen = DateGenerator(datetime(2020, 10, 6), datetime(2020, 10, 8), default_format="%Y-%m-%d %H:%M:S", seed=42)
            >>> gen(5)
            ['2020-10-06 04:17:02', '2020-10-07 13:08:59', '2020-10-07 07:25:09', '2020-10-06 21:03:58', '2020-10-06 20:47:05']
        """
        format_used = self.get_format(format_name)

        return self._data_generator(k=k, format_used=format_used, *args, **kwargs)

class FileSourceGenerator(FormattedGenerator):
    """A base class for all the ``GeneratorObject`` that use data from files.

        A ``GeneratorObject`` might be read from multiple file types such as *.json*,*.csv*,*.txt* etc..

        Parameters
        ----------
        file_parser : function
            The ``function`` of a file parser. (Just the function, without brackets)
        file_path : bool, optional
            The path to the file to draw data from.
            **Only ``locale`` or ``file_path`` can be used, not both.**
        *args
            Variable length argument list.
        **kwargs
            Arbitrary keyword arguments. 
        
        Attributes
        ----------
        source_path : str
            The path to the source of the generator. The value is generated using file_path or locale.
        data : dict
            The data used for generation.

        Raises
        ------
        ValueError
            If both or none of ``locale`` and ``file_path`` are used.
            
        See Also
        --------
        TODO conventions for locale files
    """
    def __init__(self, file_parser, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(file_path, str) :
            self.source_path = file_path
        else:
            raise ValueError(f"File path has to be specified")
        
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
                The str to generate data based on.
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

        data_keys = [match(FORMAT_KEY_CLEANING, fname)[0] for _, fname, _, _ in Formatter().parse(format_used) if fname != ""]

        # Generating all values for the formatting.
        all_dataset = []
        for key in data_keys:
            all_dataset.append(self.random_generator.choice(self.data[key], size=k))
        
        # Formatting
        for data_point in zip(*all_dataset):
            data_point_parameters = {k: v for k, v in zip(data_keys, data_point)}
            generated_data.append(format_used.format(**data_point_parameters))

        return generated_data

    def _preprocess_data(self, k, format_name="default", *args, **kwargs):
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
            Generate data with specific format name:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = HumanNameGenerator(locale="en_INTER", seed=42)
            >>> gen(5, "iffl")
            ['A. Stillwell', 'L. Bloor', 'J. Penney', 'C. Cordrey', 'Y. Boone']

            Setting ``default_format`` using ``default_format_name`` and generating 5 samples:

            >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
            >>> gen = HumanNameGenerator(locale="en_INTER", default_format_name="lff", seed=42)
            >>> gen(5)
            ['Bodley Belle', 'Rumbley Ivy', 'Nettle Armani', 'Hickcox Alaina', 'Herbertson Arianna']
        """
        if not self.data:
            raise EmptySourceError()
        
        # TODO maybe change format_used to formatting.
        format_used = self.get_format(format_name)

        return self._data_generator(k,format_used, *args, **kwargs)   

class LocaleFileSourceGenerator(FileSourceGenerator):
    """A base class for all the ``GeneratorObject`` that use data from the library files (using the library naming convention).

        Parameters
        ----------
        locale : str
            The locale for this file. Will be used to automatically find the locale file.
        *args
            Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
        
        Attributes
        ----------
        locale : str, optional
            The locale of the generator.

        Raises
        ------
        ValueError
            If a valid file_path is given to the constructor.
        TypeError
            If ``locale`` is not an str.
            
        See Also
        --------
        GeneratorObject  : All functinality derived from ``GeneratorObject``.
        FormattedGenerator : All functinality derived from ``FormattedGenerator``.
        FileSourceGenerator : All functinality derived from ``FileSourceGenerator``.
        TODO conventions for locale files
    """
    def __init__(self, locale, *args, **kwargs):
        if isinstance(locale, str):
            self.locale = locale

            generator_name = self.__class__.__name__
            source_path = syspath_join(os.path.normpath("makedata\data_generators\data_sources"), f"{generator_name}", f"{self.locale}.json")
        else:
            raise TypeError(f"Locale '{locale}' has to be an str, but is '{type(locale)}''")
        
        if isfile(kwargs.get("file_path", "")) or isdir(kwargs.get("file_path", "")):
            raise ValueError(f"Only one of 'file_path' or 'locale' can be set, but you have set both.")

        super().__init__(json_load, file_path=source_path, *args, **kwargs)

        if self.is_generated_name:
                self.name = generator_name + "_" + locale

class FromJSONGenerator(FileSourceGenerator):
    """A formatted generator that uses a .json file for it's source.

        All of the methods, parameters and attributes for this ``GeneratorObject`` are listed in ``FileSourceGenerator``.

        See Also
        --------
        GeneratorObject  : All functinality derived from ``GeneratorObject``.
        FormattedGenerator : All functinality derived from ``FormattedGenerator``.
        FileSourceGenerator : All functinality derived from ``FileSourceGenerator``.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(json_load, *args, **kwargs)

class NumericGenerator(GeneratorObject):
    """A base class for all numeric ``GeneratorObject``.

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
        """numeric data generator
        """
        raise NotImplementedError

    def _preprocess_data(self, k, *args, **kwargs):
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
        Generating 5 random integers:

        >>> from data_generators.entity_generators.HumanNameGenerator import HumanNameGenerator
        >>> gen = IntegerGenerator(-7, 10, seed=42)
        >>> gen.(5)
        [-6, 6, 4, 0, 0]
        """
        # TODO add choice for replacement for uniqueness
        return self._data_generator(k, *args, **kwargs)

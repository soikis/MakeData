class GeneratorError(Exception):
    """Base exception for all ``GeneratorObject`` related exceptions.

            Parameters
            ----------
            gen : GeneratorObject
                ``GeneratorObject`` that raised the error.
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments. 

            Attributes
            ----------
            gen : GeneratorObject
                ``GeneratorObject`` that raised the error.
            gen_type : str
                Type of ``gen`` in string format.
            gen_name : str
                Name of ``gen`` from it's ``name`` attribute.
            msg : str
                Error message describing the error.
    """
    def __init__(self, gen, *args, **kwargs):
        self.gen = gen
        self.gen_type = self.gen.__class__.__name__
        self.gen_name = self.gen.name
        super().__init__(self.create_msg(*args, **kwargs), *args, **kwargs)

    def create_msg(self):
        NotImplementedError

class FormatError(GeneratorError):
    """Raise this error when a ``GeneratorObject`` that uses formatting couldn't **use** the specified formatting.

            Parameters
            ----------
            formatting : str
                Formatting that was used in the ``GeneratorObject``
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments. 

            Attributes
            ----------
            formatting : str
                Formatting that was used in the ``GeneratorObject``
            
            See Also
            --------
            FormatNotFoundError : Raise this error if a ``GeneratorObject`` couldn't **find** the specified **format name**.
    """
    def __init__(self, formatting, *args, **kwargs):
        if isinstance(formatting, str):
            self.formatting = formatting
        else:
            raise TypeError(f"Parameter 'formatting' of type {type(formatting)} has to be of type 'str'.")
        super().__init__(*args, **kwargs)

    def create_msg(self):
        msg = f"The format '{self.formatting}' is not a valid format for generator of type " \
                f"{self.gen_type} with name {self.gen_name}."
        return msg

class FormatNotFoundError(GeneratorError):
    """Raise this error when a ``GeneratorObject`` that uses formatting couldn't **find** the specified format name.

            Parameters
            ----------
            format_name : str
                Format name that was not found in this ``GeneratorObject``.
            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments. 

            Attributes
            ----------
            format_name : str
                Format name that was not found in this ``GeneratorObject``.
            
            See Also
            --------
            FormatError : Raise this error if a ``GeneratorObject`` couldn't **use** the specified formatting.
    """
    def __init__(self, format_name, *args, **kwargs):
        self.format_name = format_name
        super().__init__(*args, **kwargs)

    def create_msg(self):
        msg = f"The format '{self.format_name}' is not an available symbol or a format name for 'GeneratorObject' of type " \
                f"'{self.gen_type}' with name '{self.gen_name}'."
        return msg

class NoDefaultFormatError(GeneratorError):
    """Raise this error when a ``GeneratorObject`` that uses formatting couldn't find the specified format.

            *args
                Variable length argument list
            **kwargs
                Arbitrary keyword arguments. 

            Attributes
            ----------
            format_name : str
                Format name that was not found in this ``GeneratorObject``.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_msg(self):
        msg = f"The 'GeneratorObject' with name '{self.gen_name}' of type '{self.gen_type}' doesn't have a default format. " \
                    "You can either set it in the constroctor or specify one when generating data."
        return msg

class EmptySourceError(GeneratorError):
    """Raise this error when a ``GeneratorObject`` that uses a data source has an empty source.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def create_msg(self):
        msg = f"'GeneratorObject' of type>{self.gen_type} with name>{self.gen_name} has an empty data source."
        return msg
    
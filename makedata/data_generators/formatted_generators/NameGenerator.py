from ..BaseGenerators import LocaleFileSourceGenerator

class NameGenerator(LocaleFileSourceGenerator):
    """Generator to generate k human names by format.

        There are the default formats, but more can be added.
        
        See Also
        --------
        :class:`makedata.data_generators.BaseGenerators.FormattedGenerator` : All the available functionalities derived from ``FormattedGenerator``.
        :class:`makedata.data_generators.BaseGenerators.FileSourcedGenerator` : All the available functionalities derived from ``FileSourcedGenerator``.
        :class:`makedata.data_generators.BaseGenerators.LocaleFileSourceGenerator` : All the available functionalities derived from ``LocaleFileSourceGenerator``.

        Examples
        --------
        Using a ``NameGenerator`` to generate 5 names with different formats:
        
        >>> from data_generators.formatted_generators.NameGenerator import NameGenerator
        >>> gen = NameGenerator(locale="en_INTER", default_format_name="iffl", seed=42)
        >>> gen(5)
        ('A. Stillwell', 'L. Bloor', 'J. Penney', 'C. Cordrey', 'Y. Boone')
        
        Generating 5 more names with a different format from the default:

        >>> gen(5, format_name="lff")
        ('Bodley Belle', 'Rumbley Ivy', 'Nettle Armani', 'Hickcox Alaina', 'Herbertson Arianna')
    """
    formats = {"male_first_and_last": "{male_first_names} {last_names}",
                "female_first_and_last": "{female_first_names} {last_names}",
                "last_and_male_first": "{last_names} {male_first_names}",
                "last_and_female_first": "{last_names} {female_first_names}",
                "init_male_first_and_last": "{male_first_names[0]}. {last_names}",
                "init_female_first_and_last": "{female_first_names[0]}. {last_names}"}
    
    formats_symbols = {"mfl": "male_first_and_last", "ffl": "female_first_and_last",
                            "lmf": "last_and_male_first", "lff": "last_and_female_first",
                            "imfl": "init_male_first_and_last", "iffl": "init_female_first_and_last"}
    

    def __init__(self, *args, **kwargs):
        # If 'generate_format_symbols' is not defined, set it to True.
        if kwargs.get("generate_format_symbols", False):
            kwargs["generate_format_symbols"] = True
        super().__init__(*args, **kwargs)
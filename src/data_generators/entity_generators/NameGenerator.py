# TODO documentation
from ..BaseGenerators import FromJSONGenerator

class NameGenerator(FromJSONGenerator):
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
        super().__init__(generate_format_symbols=True, *args, **kwargs)
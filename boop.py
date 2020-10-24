from makedata.data_generators.formatted_generators.DateGenerator import DateGenerator
from makedata.data_generators.formatted_generators.NameGenerator import NameGenerator
from datetime import datetime
from dateutil.tz import gettz
from makedata.models.BaseModels import BaseModel


def main():
    nameGen = NameGenerator(locale="en_INTER", name="Full Name", seed=42)
    print(nameGen(3, format_name="male_first_and_last"))
    print(nameGen(3, format_name="female_first_and_last"))
    print(nameGen(3, format_name="last_and_male_first"))
    print(nameGen(3, format_name="last_and_female_first"))
    print(nameGen(3, format_name="init_male_first_and_last"))
    print(nameGen(3, format_name="init_female_first_and_last"))
    print(nameGen(3, format_name="mfl"))
    print(nameGen(3, format_name="ffl"))
    print(nameGen(3, format_name="lmf"))
    print(nameGen(3, format_name="lff"))
    print(nameGen(3, format_name="imfl"))
    print(nameGen(3, format_name="iffl"))
    
    

if __name__ == "__main__":
    main()

#"{male_first_name} {last-name} {date2}{female_first_names[0].split-it(var='something',var2="something")}{doopa}{boop|bop|pop}" - regexr test
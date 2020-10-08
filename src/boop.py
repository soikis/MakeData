from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
# from data_generators.numeric_generators.FloatGenerator import FloatGenerator
from data_generators.formatted_generators.DateGenerator import DateGenerator
from data_generators.formatted_generators.NameGenerator import NameGenerator
from datetime import datetime
from dateutil.tz import gettz
from models.BaseModels import BaseModel


def main():
    nameGen = NameGenerator(locale="en_INTER", default_format_name="ffl", name="Full Name")
    ageGen = IntegerGenerator(18, 38, name="Age",seed=2)
    birthdayGen = DateGenerator("1-1-1990", "31-12-1999", name="Birthday")
    personModel = BaseModel([nameGen, ageGen, birthdayGen], seed=42, overwrite_seeds=True, name="PersonModel")
    print(personModel(5))
    personModel = BaseModel([nameGen, ageGen, birthdayGen], seed=42, overwrite_seeds=True, name="PersonModel")
    personModel.reset_seeds(2)
    print(personModel(5))
    # personGen2 = NameGenerator(locale="en_INTER", default_format_name="lmf", seed=42)
    # print(personGen2(5))
    # print(personGen2.formats_templates)
    # intGen1 = IntegerGenerator(-1, 5, seed=42)
    # print(intGen1(5))
    
    # dateGen1 = DateGenerator("6-10-2020", "8-10-2020", default_format="%Y-%m-%d %H:%M:%S", seed=42)
    # print(personGen2(5, format_name="lff"))

    # model = BaseModel([intGen1,personGen2,dateGen1], name="please")

    # from timeit import default_timer
    # s = default_timer()
    # data = model.generate_data(500_000, split_samples=False)
    # e = default_timer()
    # print(e-s)

    # intGen1 = IntegerGenerator(-5,5, seed=20)
    # print(intGen1(5))
    # intGen2 = IntegerGenerator(-5,5, seed=21)
    # print(intGen2(5))
    # personGen1 = NameGenerator(locale="en_INTER", seed=80)
    # print(personGen1(5, "mfl"))
    # personGen2 = NameGenerator(locale="en_INTER", set_format="iffl", seed=8)
    # print(personGen2(5))
    # floatGen1 = FloatGenerator(-5,5, seed=5)
    # print(floatGen1(5))
    # floatGen2 = FloatGenerator(-5,5, seed=10)
    # print(floatGen2(5))
    # dateGen1 = DateGenerator(datetime(2020, 10, 6), datetime(2020, 10, 8), tz="Pacific/Kiritimati", set_format=r"%d-%m-%Y h:m:s", seed=5)
    # print(dateGen1.default_format)
    # print(dateGen1(5))
    # print(intGen1.name)
    # print(intGen2.name)
    # print(personGen1.name)
    # print(personGen2.name)
    # print(floatGen1.name)
    # print(floatGen2.name)
    # print(dateGen1.name)

if __name__ == "__main__":
    main()

#"{male_first_name} {last-name} {date2}{female_first_names[0].split-it(var='something',var2="something")}{doopa}{boop|bop|pop}" - regexr test
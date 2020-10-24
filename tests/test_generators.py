import pytest
from makedata.data_generators.BaseGenerators import *
from makedata.data_generators.numeric_generators.PrimitveNumerics import *
from makedata.data_generators.formatted_generators.NameGenerator import NameGenerator

class TestBaseGenerator:
    def test_generator_name_generation(self):
        gen = GeneratorObject()
        assert gen.name == "GeneratorObject0"

    def test_generator_name_set(self):
        gen = GeneratorObject(name="NewGeneratorObject")
        assert gen.name == "NewGeneratorObject"
    
    def test_reset_seed(self):
        gen = IntegerGenerator(0, 100, seed=42)
        gen.reset_seed(20)
        gen2 = IntegerGenerator(0, 100, seed=20)
        assert gen(5) == gen2(5) == (89, 28, 26, 46, 89)

class TestNameGenerator:

    @pytest.fixture(scope="class")
    def name_generator(self):
        return NameGenerator(locale="en_INTER", seed=42)

    @pytest.mark.parametrize("format_name,name", [
    ("male_first_and_last", ('Jace Hickcox', 'Aryan Herbertson', 'Amos Stillwell')), 
    ("female_first_and_last", ('Ivy Boone', 'Armani Lake', 'Alaina Winbush')),
    ("last_and_male_first", ('Raffel Brett', 'Robson Raul', 'Poock Rowan')),
    ("last_and_female_first", ('Spafford Royalty', 'Hodsdon Lucia', 'Juett Kaiya')),
    ("init_male_first_and_last", ('M. Simco', 'K. Leggins', 'K. Hillson')),
    ("init_female_first_and_last", ('K. Lin', 'N. Tetterton', 'J. Benefield')),
    ("mfl", ('Saint Mobbs', 'Anakin Channon', 'Corbin Risner')),
    ("ffl", ('Rayna Wilhelm', 'Joy Hinkson', 'Ariana Thresher')),
    ("lmf", ('Oxley Myles', 'Saban Nasir', 'Robbs Kyson')),
    ("lff", ('Jopp Cecilia', 'Barks Princess', 'Lemay Liv')),
    ("imfl", ('B. Wigg', 'M. Harrier', 'J. Foister')),
    ("iffl", ('B. Hudnell', 'R. Screen', 'A. Coleman'))])
    def test_name_formats(self, name_generator, format_name, name):
        assert name_generator(3, format_name=format_name) == name
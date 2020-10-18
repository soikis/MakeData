import pytest
from makedata.data_generators.BaseGenerators import *
from makedata.data_generators.numeric_generators.IntegerGenerator import IntegerGenerator

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

class TestFormattedGenerator:
    def test
    
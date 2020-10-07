# TODO documentation
from ..BaseGenerators import NumericGenerator


class IntegerGenerator(NumericGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # This is not necessary but it might help with readability for some people.
    def _integer_generator(self, k):
        return self.random_generator.integers(self.low, self.high, size=k)
    
    def _data_generator(self, k):
        return self._integer_generator(k)

# TODO documentation
from ..BaseGenerators import NumericGenerator


class FloatGenerator(NumericGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # This is not necessary but it might help with readability for some people.
    def _float_generator(self, k):
        return self.random_generator.uniform(self.low, self.high, size=k)
    
    def _data_generator(self, k):
        return self._float_generator(k)

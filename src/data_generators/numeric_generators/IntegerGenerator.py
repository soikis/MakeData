from ..BaseGenerators import NumericGenerator


class IntegerGenerator(NumericGenerator):
    """Generator to generate k integers in a given range.

        *args
                Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
        
        
        See Also
        --------
        data_generators.BaseGenerators.NumericGenerator : All the available functionalities derived from ``NumericGenerator``.

        Examples
        --------
        Using a ``IntegerGenerator`` to generate data:
        
        >>> from data_generators.numeric_generators.IntegerGenerator import IntegerGenerator
        >>> gen = IntegerGenerator(-1, 5, seed=42)
        >>> gen(5)
        (-1, 3, 2, 1, 1)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)    
    
    def _data_generator(self, k):
        """Generate k integers.

            Parameters
            ----------
            k : int
                Generate k samples.
        """
        return self.random_generator.integers(self.low, self.high, size=k)

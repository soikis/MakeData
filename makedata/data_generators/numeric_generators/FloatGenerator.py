from ..BaseGenerators import NumericGenerator


class FloatGenerator(NumericGenerator):
    """Generator to generate k floating point numbers in a given range.

        Parameters
        ----------
        *args
                Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
        
        
        See Also
        --------
        data_generators.BaseGenerators.NumericGenerator : All the available functionalities derived from ``NumericGenerator``.

        Examples
        --------
        Using a ``FloatGenerator`` to generate data:
        
        >>> from data_generators.numeric_generators.FloatGenerator import FloatGenerator
        >>> gen = FloatGenerator(-1, 5, seed=42)
        >>> gen(5)
        (3.64373629133578, 1.6332706385123137, 4.151587519468295, 3.1842081743561836, -0.4349359126741028)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

    def _data_generator(self, k):
        """Generate k floating point numbers.

            Parameters
            ----------
            k : int
                Generate k samples.
        """
        return self.random_generator.uniform(self.low, self.high, size=k)

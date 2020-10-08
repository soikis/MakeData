def GeneratingFunction(func):
    """Decorator to transform a ``GeneratorObject`` output to a tuple.
        
        .. note::
            This decorator should be used on the ``GeneratorObject``'s data generation method.
            By convention it's ``generate_data``.
    """
    def wrapper(*args, **kwargs):
        try:
            result = tuple(func(*args, **kwargs))
            return result
        except TypeError:
            raise TypeError(f"Method {func} has to return a result that can be used to generate a tuple such as an iterator or generator. " \
                                f"However, a result of type {type(result)} was returned.")
    return wrapper
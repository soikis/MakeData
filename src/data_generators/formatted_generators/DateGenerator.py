from ..BaseGenerators import FormattedGenerator
from dateutil.parser import parse
from datetime import datetime, timedelta
import numpy as np
from dateutil.tz import gettz
from dateutil.utils import default_tzinfo
from ..GeneratorExceptions import FormatError
from dateutil.relativedelta import relativedelta
from ..GeneratorDecorators import GeneratingFunction

class DateGenerator(FormattedGenerator):
    """Generator to generate k dates in a given range, using a spesific format.

        Parameters
        ----------
        start_time : datetime or float or str
            The time to start the ``timeframe`` from. Can be a datetime object, float timestamp or a string representation of a date.
        end_time : datetime or float or str
            The time to end the ``timeframe`` on. Can be a datetime object, float timestamp or a string representation of a date.
        tzinfo : datetime.tzinfo or str, optional
            Either a datetime.tzinfo or a tz name string.
            If ``None``, will try to infer from ``start_time``, if not found, try from ``end_time``, if not found, stays None.
        dayfirst : bool, optional
            Whether to interpret the first value in an ambiguous 3-integer date  
            (e.g. 01/05/09) as the day if ``True`` or month if ``False``.
        yearfirst : bool, optional
            Whether to interpret the first value in an ambiguous 3-integer date (e.g. 01/05/09) as the year. 
            If ``True``, the first number is taken to  be the year, otherwise the last number is taken to be the year. 
        *args
                Variable length argument list
        **kwargs
            Arbitrary keyword arguments. 
        
        Attributes
        ----------
        tzinfo : datetime.tzinfo
            Time zone information.
        time_frame : tuple
            A dictionary with a mapping between an abbreviations of a format and it's full name.
            Where 'abbreviation': 'name_of_format' are the 'key':'value', respectively.
        
        See Also
        --------
        data_generators.BaseGenerators.FormattedGenerator : All the available functionalities derived from ``FormattedGenerator``.

        Examples
        --------
        Using a ``DateGenerator`` to generate data with a custom format:
        
        >>> from data_generators.formatted_generators.DateGenerator import DateGenerator
        >>> gen = DateGenerator("6-10-2020", "8-10-2020", default_format="%Y-%m-%d %H:%M:%S", seed=42)
        >>> gen(5)
        ('2020-10-06 04:17:02', '2020-10-07 13:08:59', '2020-10-07 07:25:09', '2020-10-06 21:03:58', '2020-10-06 20:47:05')
        
        Using a ``DateGenerator`` to generate data with it's default format:
        
        >>> gen2 = DateGenerator(datetime(2020, 8, 2), datetime(2020, 12, 30), seed=42)
        >>> gen2(5)
        ('15-08-2020', '26-11-2020', '08-11-2020', '06-10-2020', '05-10-2020')
    """
    default_format = r"%d-%m-%Y"

    def __init__(self, start_time, end_time, tzinfo=None, dayfirst=True, yearfirst=False, *args, **kwargs):
        super().__init__(default_must=True, *args, **kwargs)

        timeframe = [start_time, end_time]

        if tzinfo is not None:
                if isinstance(tzinfo, str):
                    tzinfo = gettz(tzinfo)
        elif isinstance(start_time, datetime):
            if start_time.tzinfo is not None:
                tzinfo = start_time.tzinfo
        elif isinstance(end_time, datetime):
            if end_time.tzinfo is not None:
                tzinfo = end_time.tzinfo
        self.tzinfo = tzinfo

        for i, time in enumerate(timeframe):
            timeframe[i] = self._convert_to_date(time, dayfirst, yearfirst)

            if self.tzinfo is not None:
                timeframe[i] = default_tzinfo(time, self.tzinfo)
        
        self.timeframe = tuple(timeframe)
        if self.timeframe[0] > self.timeframe[1]:
            raise ValueError(f"'time_range' with values: {self.timeframe} is invalid. First datetime \
                            '{self.timeframe[0]}' can't be bigger than the second datetime '{self.timeframe[1]}'.")
        
        self.time_defference = self.timeframe[1].timestamp() - self.timeframe[0].timestamp()
        

    def _convert_to_date(self, time, dayfirst, yearfirst):
        """Convert ``time`` to a ``datetime`` object.

            Try to convert any possible input type to a ``datetime`` object.

            Parameters
            ----------
            time : datetime or float or str
                The input to be converted to ``datetime`` object.
            dayfirst : bool, optional
                Whether to interpret the first value in an ambiguous 3-integer date  
                (e.g. 01/05/09) as the day if ``True`` or month if ``False``.
            yearfirst : bool, optional
                Whether to interpret the first value in an ambiguous 3-integer date (e.g. 01/05/09) as the year. 
                If ``True``, the first number is taken to  be the year, otherwise the last number is taken to be the year.
        """
        if isinstance(time, str):
            return parse(time, dayfirst=dayfirst, yearfirst=yearfirst)
        elif isinstance(time, float):
            return datetime.fromtimestamp(time)
        elif isinstance(time, datetime):
            return time
        else:
            raise TypeError(f"Variable 'time' of type {type(time)} is not a supported type.")
    
    @GeneratingFunction
    def _data_generator(self, k, format_used=None, tzinfo=None, steps="D", return_datetime=False):
        """Generate k dates.

            Generate k random dates with the given format or the default one.

            Parameters
            ----------
            k : int
                Generate k samples.
            format_used : str, optional
                The format used to format the string, if not given, use ``default_format``.
            tzinfo : datetime.tzinfo or str, optional
                Either a ``datetime.tzinfo`` or a timezone name string.
            steps : str, optional
                Time resolution to use when generateing dates.
                years=Y, months=M, weeks=W, days=D, hours=h, minutes=m, seconds=s, milliseconds=ms TODO might be to many resolutions
            return_datetime : bool, optional
                Whether to return a ``datetime`` object or a formatted string.
                If True, and a ``format_used`` is specified, will raise a ``ValueError``.
            
            Raises
            ------
            FormatError
                If the provided format cannot be used by ``datetime.strftime``.
            ValueError
                If ``return_datetime=True`` and ``format_used`` is specified.
        """
        
        if format_used is not None and return_datetime:
            raise ValueError("If 'return_datetime' is True, 'format_used' can't be specified.")
        
        if format_used is None and not return_datetime:
            format_used = self.default_format
        
        # Generate k dates.
        chosen_deltas = self.random_generator.integers(0, self.time_defference, size=k).astype("timedelta64[s]").astype(f"timedelta64[{steps}]")
        chosen_dates = (np.datetime64(self.timeframe[0], steps) + chosen_deltas).astype(datetime)
        
        # If a default timezone is provided, but a new one is not, use the default.
        if tzinfo is None and self.tzinfo is not None:
            tzinfo = self.tzinfo

        # If this part fails, it is probably because of a bad format
        try:
            if tzinfo is not None:
                if isinstance(tzinfo, str):
                    tzinfo = gettz(tzinfo)
                
                    if return_datetime:
                        return (default_tzinfo(date, tzinfo) for date in chosen_dates)

                    func = lambda date: default_tzinfo(date, tzinfo).strftime(format_used)
                    return map(func, chosen_dates)

            if return_datetime:
                return chosen_dates

            func = lambda date: date.strftime(format_used)
            return map(func, chosen_dates)

        except ValueError:
                raise FormatError(format_used, self)
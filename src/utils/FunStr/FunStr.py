from re import finditer, findall, search, compile as recompile

# SIMPLE_PARAMETER_PATTERN  = recompile(r"\{([\w\d\-]+)[^\s\{\}]*\}")

# def parameters_list(funString): TODO PROBABLY NOT RELEVANT AT ALL
#     return findall(SIMPLE_PARAMETER_PATTERN, funString)


PARAMETERS_TEXT_SPLITTER = recompile(r"\\(?P<break>[\{\}])|\{(?P<params>.+?)[^\\]\}|(?P<txt>[^\{\}\\]+)|(?P<bad_match>.+)")
PARAMETER_PARSER = recompile(r"(?P<bad_var>[|(){}]?:)|(?P<var>[\w\d?]+[\w\d?[\]{}:\s.()]*|\((?P<var_group>[\w\d?|[\]{}:\s.()]+)\))(?P<op>[>~|])?|(?P<bad_op_group>[(){}>~|])")
CLEAN_VAR = recompile(r"[\w\d]+")

import random

PARAM_OPEN = "PARAM_OPEN"
PARAM_CLOSE = "PARAM_CLOSE"
GROUP_OPEN = "GROUP_OPEN"
GROUP_CLOSE = "GROUP_CLOSE"
ALT = "ALT"
PRECEDING = "PRECEDING"
ESCAPE = "ESCAPE"
CHAR = "CHAR"
QSTN = "QSTN"
EXCLUDE = "EXCLUDE"
NOT_PRECEDING = "NOT_PRECED"
BREAK = "BREAK"
BREAK_CHAR = "\x08"

class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.name + ":" + self.value

class Lexer:
    symbols = {"{": PARAM_OPEN, "}": PARAM_CLOSE,"(": GROUP_OPEN, ")": GROUP_CLOSE, "|": ALT, ">": PRECEDING, 
                    "~": NOT_PRECEDING, "\\": ESCAPE, "?": QSTN, BREAK_CHAR: BREAK}
    
    def __init__(self, pattern):
        self.pattern = pattern
    
    def get_token(self):
        for c in self.pattern:
            if c in Lexer.symbols:
                yield Token(Lexer.symbols[c], c)
            else:
                yield Token(CHAR, c)

class Parser:

    @staticmethod
    def consume(lex):
        try:
            return next(lex)
        except StopIteration:
            return Token(BREAK, BREAK_CHAR)


    @staticmethod
    def parse(pattern):
        sentence = []
        parameter_counter = 0
        prev_group = ""
        for segment in finditer(PARAMETERS_TEXT_SPLITTER, pattern):
            if segment.group("params") is not None:
                sentence.append(Parser.process_parameter(segment.group("params").replace(r"\{","{").replace(r"\}","}"), parameter_counter))
                parameter_counter += 1
                prev_group = "params"
            elif segment.group("txt") is not None:
                if prev_group == "txt":
                    sentence[-1] += segment.group("txt")
                else:
                    sentence.append(segment.group("txt"))
                    prev_group = "txt"
            elif segment.group("break") is not None:
                if prev_group == "txt":
                    sentence[-1] += segment.group("break")
                else:
                    sentence.append(segment.group("break"))
                    prev_group = "txt"
            elif segment.group("bad_match") is not None:
                raise Exception("parsing error")
            else:
                raise Exception("unkown error")
        return sentence
            

    @staticmethod
    def process_parameter(parameter_values, param_id):
        param_possibilities = []
        preceding_values = {None}                                            
        preceding_code = 0
        alternative = True
        for param in finditer(PARAMETER_PARSER, parameter_values):
            if param.group("bad_var") is not None:
                raise Exception("Parse Error")
            elif param.group("bad_op_group") is not None:
                raise Exception("Parse Error")
            
            if param.group("var_group") is not None:
                param_values = tuple(param.group("var_group").split("|"))
                if "" in param_values:
                    raise Exception("Parse error - empty or in parameter")
            elif param.group("var") is not None:
                param_values = tuple([param.group("var")])
            else:
                raise Exception("Parse Exception")

            if param.group("op") is not None:
                if  param.group("op") == "|":
                    alternative = True
                else:
                    if param_id == 0:
                        raise Exception("Parse error first parameter can't contain a conditinoal statement.")  # TODO make this available
                    if preceding_code != 0:
                        raise Exception("Parse error")
                    invalid_ids = [value for value in param_values if not value.isidentifier()]
                    if invalid_ids:
                        raise Exception("Parse error")
                    if param.group("op") == ">":
                        preceding_values = param_values
                        preceding_code = 1
                    elif param.group("op") == "~":
                        preceding_values = param_values
                        preceding_code = -1
                    continue
            else:
                alternative = False
            
            if "?" in preceding_values:
                    raise Exception("Parse exception")
                
            param_possibilities.append({"values": param_values, "preceding_code": preceding_code, 
                                            "preceding_values": preceding_values})

            preceding_values = {None}                                            
            preceding_code = 0

        if alternative:
                raise Exception("Parse Error")

        return param_possibilities


class FunStr:

    def __init__(self, pattern=None, seed=None):
        self.parser = Parser()
        if seed is not None:
            self.random_generator = random.Random(seed)
        else:
            self.random_generator = random.Random()
        
        if pattern is not None:
            self.compile(pattern)
        else:
            self.sentence = None
            self.compiled = False

    def compile(self, pattern):
        self.sentence = self.parser.parse(pattern)
        self.compiled = True

    def generate_format(self):
        # TODO use template strings if safety is needed - https://lucumr.pocoo.org/2016/12/29/careful-with-str-format/
        # and https://realpython.com/python-string-formatting/
        if self.compiled:
            formatting = []
            previous_params = set()
            for segment in self.sentence:
                if isinstance(segment, str):
                    formatting.append(segment)
                elif isinstance(segment, list):
                    segment_options = []
                    for option in segment:
                        if option["preceding_code"] == 1 and previous_params.intersection(option["preceding_values"]):
                            segment_options.extend(option["values"])
                        elif option["preceding_code"] == -1 and not previous_params.intersection(option["preceding_values"]):
                            segment_options.extend(option["values"])
                        elif option["preceding_code"] == 0:
                            segment_options.extend(option["values"])
                        else:
                            pass

                    # In order to prevent duplicates, we use a dict to hash the list of segment_options, why dict? 
                    # Because it keeps the order of insertion unlike a set (which is important for reproducibility).
                    segment_options = tuple(dict.fromkeys(segment_options))
                    
                    try:
                        choice = self.random_generator.choice(segment_options)
                        previous_params.add(search(CLEAN_VAR, choice).group())
                        if choice != "?":
                            formatting.append("{" + choice +"}")
                            continue
                        formatting.append("")
                        
                    except IndexError:
                        if not segment_options:
                            formatting.append("")
                        else:
                            raise IndexError() # TODO take message from except statement
                else:
                    raise Exception("Unkown error")
            return "".join(formatting)
        else:
            raise Exception("not compiled")


            


if __name__ == "__main__":
    #""
    parser = Parser()
    # parser.parse("{(_var1|var2)~(var3[0]|var4|?)|var5|var6|var6>var7|(var6|var7)~var8|var2>(var9|var10)} pops alot \{\} {more_params}")
    print (FunStr("{var[10]|var2}{var>var3|var4}",seed=4).generate_format())
    # parser.sentence.print_lst()
from re import finditer, findall, compile as recompile

# PARAMETER_PATTERN  = recompile(r"\{([\w\d\-]+)[^\s\{\}]*\}")

# def parameters_list(funString):
#     return findall(PARAMETER_PATTERN, funString)

PARAMETERS_TEXT_SPLITTER = recompile(r"\\(?P<break>[\{\}])|\{(?P<params>[^\s\\]+?)\}|(?P<txt>[^\{\}\\]+)|(?P<bad_match>.+)")
PARAMETER_PARSER = recompile(r"(?P<var>[\w\d\?\[\]]+|\((?P<var_group>[\w\d\|\?\[\]]+)\))(?P<op>[>~])?")

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
        is_first_param = True
        prev_group = ""
        for segment in finditer(PARAMETERS_TEXT_SPLITTER, pattern):
            if segment.group("params") is not None:
                sentence.append(Parser.process_parameter(segment.group("params"), is_first_param))
                is_first_param = False
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
    def process_parameter(parameter_values, is_first_param):
        param_possibilities = []
        preceding_values = {None}                                            
        preceding_code = 0
        for param in finditer(PARAMETER_PARSER, parameter_values):
            if param.group("var_group") is not None:
                param_values = tuple(param.group("var_group").split("|"))
            elif param.group("var") is not None:
                param_values = tuple([param.group("var")])
            else:
                raise Exception("Parse Exception")

            if param.group("op") is not None:
                if is_first_param:
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
            
            if "?" in preceding_values:
                    raise Exception("Parse exception")
                
            param_possibilities.append({"values": param_values, "preceding_code": preceding_code, 
                                            "preceding_values": preceding_values})

            preceding_values = {None}                                            
            preceding_code = 0

        return param_possibilities


class FunStr:

    def __init__(self, pattern=None, seed=None):
        self.parser = Parser()
        if seed is not None:
            self.random_generator = random.Random(seed)
        else:
            self.random_generator = random.Random()
        
        if pattern is not None:
            self.sentence = self.parser.parse(pattern)
            self.compiled = True
        else:
            self.sentence = None
            self.compiled = False

    def generate_format(self):
        if self.compiled:
            formatting = []
            last_param_pos = 0
            for i, segment in enumerate(self.sentence):
                if isinstance(segment, str):
                    formatting.append(segment)
                elif isinstance(segment, list):
                    segment_options = []
                    for option in segment:
                        if option["preceding_code"] == 1 and formatting[last_param_pos][1:-1] in option["preceding_values"]:
                            segment_options.extend(option["values"])
                        elif option["preceding_code"] == -1 and formatting[last_param_pos][1:-1] not in option["preceding_values"]:
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
                        last_param_pos = i
                        if choice != "?":
                            formatting.append("{" + choice +"}")
                            continue
                        formatting.append("")
                    except IndexError:
                        if not segment_options:
                            formatting.append("")
                        else:
                            raise IndexError() # TODO take error from except statement
                else:
                    raise Exception("Unkown error")
            return "".join(formatting)
        else:
            raise Exception("not compiled")


            


if __name__ == "__main__":
    #""
    parser = Parser()
    # parser.parse("{(_var1|var2)~(var3[0]|var4|?)|var5|var6|var6>var7|(var6|var7)~var8|var2>(var9|var10)} pops alot \{\} {more_params}")
    print (FunStr("{var3[0]|var4|?|var5|var6|var7|var8|var9|var10} pops alot \{\} {more_params}", seed=2).generate_format())
    # parser.sentence.print_lst()
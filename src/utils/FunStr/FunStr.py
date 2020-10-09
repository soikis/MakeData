from re import finditer, findall, compile as recompile

# PARAMETER_PATTERN  = recompile(r"\{([\w\d\-]+)[^\s\{\}]*\}")

# def parameters_list(funString):
#     return findall(PARAMETER_PATTERN, funString)

PARAMETERS_TEXT_SPLITTER = recompile(r"\{(?P<param>[^ \\]+)\}|(?P<txt>[^\{\}]+)")

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
        lex = Lexer(pattern).get_token()
        sentence = []
        current_char = Parser.consume(lex)
        while current_char.name != BREAK:

            if current_char.name == PARAM_OPEN:
                if current_char.name == BREAK:
                        raise Exception("Parse error")
                parameter = ""

                while current_char.name != PARAM_CLOSE:
                    current_char = Parser.consume(lex)
                    if current_char.name == PARAM_CLOSE or current_char.name == BREAK:
                        break
                    parameter += current_char.value

                sentence.append(Parser.process_parameter(parameter))
                current_char = Parser.consume(lex)

            if current_char.name == ESCAPE:
                current_char = Parser.consume(lex)
                current_char.name = CHAR

            if current_char.name == CHAR:
                txt_segment = ""
                while current_char.name == CHAR:
                    txt_segment += current_char.value
                    current_char = Parser.consume(lex)
                    if current_char.name == ESCAPE:
                        current_char = Parser.consume(lex)
                        current_char.name = CHAR
                sentence.append(txt_segment)
                
        return sentence
            

    @staticmethod
    def process_parameter(parameter_values):
        params = finditer(r"(?P<vars>\([\w\d\[\]\|\?]+\)|[\w\d\?]+)+(?P<op>[>~\|])*", parameter_values)

        param_possibilities = []
        preceding_values = {None}                                            
        preceding_code = 0
        for param in params:
            param_values = param.group("vars")

            if param_values[0] == "(":
                if param_values[-1] == ")":
                    param_values = param_values[1:-1]
                    param_values = set(param_values.split("|"))
                    if "" in param_values:
                        raise Exception("parse error")
                else:
                    raise Exception("Parse Exception")
            elif param_values[-1] in "()":
                raise Exception("Parse Exception")
            else:
                param_values = set([param_values])

                if "" in param_values:
                    raise Exception("parse error")

            param_op = param.group("op")
            if param_op == ">":
                preceding_values = set(param_values)
                preceding_code = 1
            elif param_op == "~":
                preceding_values = set(param_values)
                preceding_code = -1
            else:
                if "?" in preceding_values:
                    raise Exception("Parse exception")

                if len([val for val in param_values if val == "?"]) > 1:
                    raise Exception("Parse exception")

                param_possibilities.append({"values": param_values, "preceding_code": preceding_code, 
                                            "preceding_values": preceding_values, "type": "param"})

                preceding_values = {None}                                            
                preceding_code = 0

        return param_possibilities


class FunStr:

    def __init__(self, pattern=None):
        self.parser = Parser()
        self.compiled = False
        if pattern is not None:
            self.compile(pattern)

    def compile(self, pattern):
        self.parser.parse(pattern)
        self.sentence = self.parser.sentence.make_list()
        self.compiled = True

    def generate(self):
        formatting = []
        for state in self.sentence:
            if len(state) == 1:
                if state[0][3] == 0:
                    formatting.append(state[0][0])
                    continue
            state_options = []
            for option in state:
                if option[1] == 1 and option[2].intersection(formatting):
                    state_options.append("{" + option[0] + "}")
                elif option[1] == -1 and not option[2].intersection(formatting):
                    state_options.append("{" + option[0] + "}")
                elif option[1] == 0:
                    state_options.append("{" + option[0] + "}")
                else:
                    state_options.append("{}")
            choice = random.choice(state_options)
            if choice != "{}":
                formatting.append(choice)

        return "".join(formatting)


            


if __name__ == "__main__":
    #""
    parser = Parser()
    parser.parse("{(_var1[0]|var2)~(var3|var4|?)|var5|var6|var6>var7|(var6|var7)~var8|var2>(var9|var10)} pops alot {more_params}")
    # print (FunStr("{v1|v2|v3|?|v9}{(v2|v3|v9)>v4|?|v1~v5}{v1>WOW}").generate())
    # parser.sentence.print_lst()
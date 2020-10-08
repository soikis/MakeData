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

class State:
    def __init__(self, sentence_part):
        self.sentence_part = sentence_part
        self.possible_values = []
        self.next_node = None
    
    @property
    def has_next(self):
        return self.next_node is not None
    
    def convert_to_tuple(self):
        self.possible_values = tuple(self.possible_values)

class Sentence:
    def __init__(self):
        self.head = State(0)
        self.len = 0

    def make_list(self):
        sentence = []
        cur = self.head
        while cur.possible_values:
            sentence.append(cur.possible_values)
            if cur.has_next:
                cur = cur.next_node
            else:
                break
        return sentence

    def append(self, sentence_part):
        last_node = self.get(self.len)
        if last_node.has_next:
            raise Exception("It shouldn't have one")
        last_node.next_node = State(sentence_part)
        self.len += 1
        if sentence_part != self.len:
            raise Exception()
        #TODO fix this logic.

    def get(self, sentence_part):
        node = self.head
        curr_part = 0
        while curr_part < sentence_part:
            # TODO add check if next_node exists
            node = node.next_node
            curr_part += 1
        return node

class Parser:

    def __init__(self):
        self.sentence = Sentence()
        self.current_sentence_pos = 0

    def parse(self, pattern):
        self.lexer = Lexer(pattern)
        self.iter_express = self.lexer.get_token()
        self.lookahead = next(self.iter_express)
        self.simple_char()


    def consume(self, name):
        if self.lookahead.name == name:
            try:
                self.lookahead = next(self.iter_express)
            except StopIteration:
                self.lookahead = Token(BREAK, BREAK_CHAR)
        

    def simple_char(self):
        if self.lookahead.name == ESCAPE:
                    self.consume(ESCAPE)
                    self.lookahead.name = CHAR
                    self.simple_char()
        if self.lookahead.name not in self.lexer.symbols.values():
            phrase = ""
            while self.lookahead.name not in self.lexer.symbols.values():
                if self.lookahead.name == ESCAPE:
                    self.consume(ESCAPE)
                    self.lookahead.name = CHAR
                phrase += self.lookahead.value
                self.consume(CHAR)
            self.sentence.append(self.current_sentence_pos)
            self.sentence.get(self.current_sentence_pos).possible_values.append((phrase, 0, {None}, 0))
            self.sentence.get(self.current_sentence_pos).convert_to_tuple()
            self.current_sentence_pos += 1
            self.simple_char()
        self.open_param()

    def open_param(self):
        if self.lookahead.name == PARAM_OPEN:
            if self.sentence.get(self.current_sentence_pos) is None:
                self.sentence.append(self.current_sentence_pos)
            self.consume(PARAM_OPEN)
            # TODO if alternation raise error
            self.qstn()
            if self.lookahead.name is not PARAM_CLOSE:
                raise Exception()
            self.consume(PARAM_CLOSE)
            self.sentence.get(self.current_sentence_pos).convert_to_tuple()
            self.current_sentence_pos += 1
            self.simple_char()
        self.qstn()
            
            
    def alternation(self, grouped=False):
        if grouped:
            return self.variable_name(grouped=grouped)
        self.variable_name(grouped=grouped)
        if self.lookahead.name == ALT:
            self.consume(ALT)
            if self.lookahead.name == ALT:
                raise Exception("parse error")
            self.alternation()

    def preceding(self, var):
        if self.lookahead.name == PRECEDING:
            self.consume(PRECEDING)
            self.variable_name(preceding_code=1, previous_var=var)
        elif self.lookahead.name == NOT_PRECEDING:
            self.consume(NOT_PRECEDING)
            self.variable_name(preceding_code=-1, previous_var=var)
        
    def open_group(self, grouped=False):
        if self.lookahead.name == GROUP_OPEN:
            
            group_values = set()
            while self.lookahead.name != GROUP_CLOSE:
                self.consume(self.lookahead.name)
                group_values.add(self.alternation(grouped=True))

            if not group_values:
                raise Exception("PARSE ERROR")
            
            
            self.consume(GROUP_CLOSE)
            self.preceding(group_values)
            self.open_group(grouped=False)
        self.alternation(grouped=grouped)

    def valid_partial_format(self):
        character = self.lookahead.value
        return character.isalpha() or character.isnumeric() or character in "_[]"

    def variable_name(self, preceding_code=0, grouped=False, previous_var=None):
        if self.lookahead.name == CHAR:
            var_name = ""
            while self.lookahead.name == CHAR:
                current = self.lookahead.value
                if not self.valid_partial_format():
                    raise Exception("PARSE ERROR")
                var_name += current
                self.consume(CHAR)
            if self.lookahead.name == PRECEDING or self.lookahead.name == NOT_PRECEDING:
                self.preceding(var_name)
            elif grouped:
                return var_name
            else:
                if isinstance(previous_var, str) or previous_var is None:
                    previous_var = {previous_var}
                self.sentence.get(self.current_sentence_pos).possible_values.append((var_name, preceding_code, previous_var, 1))

    def qstn(self, has_qstn=False):
        self.open_group(grouped=False)
        if self.lookahead.name == QSTN:
            if has_qstn:
                raise Exception("Parising error")
            self.consume(QSTN)
            self.sentence.get(self.current_sentence_pos).possible_values.append(("", 0, {None}, 1))
            self.qstn(has_qstn=True)


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
        prev_choice = random.choice(self.sentence[0])
        formatting.append(prev_choice)
        for level in self.sentence[1:]:
            if level[0][3] == 1:
                level_options = []
                for option in level:
                    if option[1] == 1 and prev_choice[0] in option[2]:
                        level_options.append(option)
                    elif option[1] == -1 and prev_choice[0] not in option[2]:
                        level_options.append(option)
                    elif option[1] == 0:
                        level_options.append(option)
                if level_options:
                    prev_choice = random.choice(level_options)
                else:
                    continue
                formatting.append(prev_choice)
            elif level[0][3] == 0:
                formatting.append(level[0])
            else:
                raise Exception("NO")
            
        return "".join("{" + param[0] + "}" if param[3] == 1 else param[0] for param in formatting if param[0] != "")


            


if __name__ == "__main__":
    #""
    parser = Parser()
    parser.parse("{v1|v2|v3|?|v9}{(v2|v3|v9)>v4|?|v1~v5}{v1>WOW}")
    print (FunStr("{v1|v2|v3|?|v9}{(v2|v3|v9)>v4|?|v1~v5}{v1>WOW}").generate())
    # parser.sentence.print_lst()
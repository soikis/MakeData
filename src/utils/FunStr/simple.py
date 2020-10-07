from re import findall, compile as recompile

PARAMETER_PATTERN  = recompile(r"\{([\w\d\-]+)[^\s\{\}]*\}")

def parameters_list(funString):
    return findall(PARAMETER_PATTERN, funString)


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

class Node:
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
        self.head = Node(0)
        self.len = 0

    def print_lst(self):
        cur = self.head
        while cur.possible_values:
            print(cur.possible_values)
            if cur.has_next:
                cur = cur.next_node
            else:
                break

    def append(self, sentence_part):
        last_node = self.get(self.len)
        if last_node.has_next:
            raise Exception("It shouldn't have one")
        last_node.next_node = Node(sentence_part)
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

    def __init__(self, lexer):
        self.lexer = lexer
        self.sentence = Sentence()
        self.current_sentence_pos = 0
        self.iter_express = self.lexer.get_token()
        self.lookahead = next(self.iter_express)

    def parse(self):
        self.simple_char()


    def consume(self, name):
        if self.lookahead.name == name:
            try:
                self.lookahead = next(self.iter_express)
            except StopIteration:
                self.lookahead = Token(BREAK, BREAK_CHAR)
        
    
    def escape(self):
        # self.simple_char()
        # if self.lookahead.name == ESCAPE:
        #     self.consume(ESCAPE)
        #     self.lookahead.name = CHAR
        #     self.consume(CHAR)
        #     self.escape()
        pass

    def simple_char(self):
        if self.lookahead.value not in self.lexer.symbols:
            phrase = self.lookahead.value
            self.consume(CHAR)
            while self.lookahead.value not in self.lexer.symbols:
                phrase += self.lookahead.value
                self.consume(CHAR)
            self.sentence.append(self.current_sentence_pos)
            self.sentence.get(self.current_sentence_pos).possible_values.append((phrase, 0, {None}))
            self.sentence.get(self.current_sentence_pos).convert_to_tuple()
            self.current_sentence_pos += 1
            self.simple_char() # TODO chnage if something before
        self.open_param()

    def open_param(self):
        self.qstn()
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
        self.alternation(grouped=grouped)
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

        
    def variable_name(self, preceding_code=0, grouped=False, previous_var=None):
        if self.lookahead.name == CHAR:
            var_name = ""
            while self.lookahead.name == CHAR:
                current = self.lookahead.value
                if not (var_name + current).isidentifier():
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
                self.sentence.get(self.current_sentence_pos).possible_values.append((var_name, preceding_code, previous_var))

    def qstn(self, has_qstn=False):
        self.open_group(grouped=False)
        if self.lookahead.name == QSTN:
            if has_qstn:
                raise Exception("Parising error")
            self.consume(QSTN)
            self.sentence.get(self.current_sentence_pos).possible_values.append(("", 0, {None}))
            self.qstn(has_qstn=True)




if __name__ == "__main__":
    #"{v1|v2|v3|v9}{(v2|v3|v9)>v4|v1~v5}{WOW}"
    lex = Lexer("{v1|v2|v3|?|v9} word {(v2|v3|v9)>v4|?|v1~v5} poop {WOW}sdd")
    parser = Parser(lex)
    parser.parse()
    parser.sentence.print_lst()
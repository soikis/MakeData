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

class Sentence:
    def __init__(self):
        self.head = Node(0)

    def print_lst(self):
        cur = self.head
        while cur.possible_values:
            print(cur.possible_values)
            if cur.has_next:
                cur = cur.next_node
            else:
                break

    def append(self, sentence_part):
        last_node = self.get(sentence_part-1)
        if last_node.has_next:
            raise Exception("It shouldn't have one")
        last_node.next_node = Node(sentence_part)

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
        self.open_param()


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
        # self.open_param()
        # if self.lookahead.value not in Lexer.symbols:
        #     self.sentence.get(self.current_sentence_pos).possible_values.append((self.lookahead.value, ))
        #     self.current_sentence_pos += 1
        #     self.sentence.append(self.current_sentence_pos)
        #     self.consume(CHAR)
        # if self.lookahead.name == BREAK:
        #     return
        # self.escape()
        pass

    def open_param(self):
        self.alternation()
        if self.lookahead.name == PARAM_OPEN:
            if self.sentence.get(self.current_sentence_pos) is None:
                self.sentence.append(self.current_sentence_pos)
            self.consume(PARAM_OPEN)
            # TODO if alternation raise error
            self.alternation()
            if self.lookahead.name is not PARAM_CLOSE:
                raise Exception()
            self.consume(PARAM_CLOSE)
            self.current_sentence_pos += 1
            self.open_param() # TODO change if something is before
            
            
    def alternation(self):
        self.variable_name(0)
        if self.lookahead.name == ALT:
            self.consume(ALT)
            self.alternation()

    def preceding(self, var):
        if self.lookahead.name == PRECEDING:
            self.consume(PRECEDING)
            self.variable_name(1, var)
        elif self.lookahead.name == NOT_PRECEDING:
            self.consume(NOT_PRECEDING)
            self.variable_name(-1, var)
        
    def open_group(self):
        # self.variable_name(preceding_code)
        # if self.lookahead.name == GROUP_OPEN:
        #     while self.lookahead.name != GROUP_CLOSE:
        #         self.consume(GROUP_OPEN)
        #         self.sentence.get(self.current_sentence_pos).possible_values.append([])
        #         self.variable_name(preceding_code, group_number)
        #     group_number += 1
        pass
        
    def variable_name(self, preceding_code, previous_var=None):
        if self.lookahead.name == CHAR:
            var_name = ""
            while self.lookahead.name == CHAR:
                current = self.lookahead.value
                if not (var_name + current).isidentifier():
                    raise Exception("PARSE ERROR")
                var_name += current
                self.consume(CHAR)
            if preceding_code != 0:
                self.sentence.get(self.current_sentence_pos).possible_values.append((var_name, preceding_code, previous_var))
                return
            if self.lookahead.name == PRECEDING or self.lookahead.name == NOT_PRECEDING:
                self.preceding(var_name)
            else:
                self.sentence.get(self.current_sentence_pos).possible_values.append((var_name, preceding_code, ""))

    def qstn(self):
        # self.alternative()
        # if self.lookahead == QSTN:
        #     self.consume(QSTN)
        #     if group_number != -1:
        #         self.sentence.get(self.current_sentence_pos).possible_values[group_number].append(("", preceding_code))
        #     else:
        #         self.sentence.get(self.current_sentence_pos).possible_values.append(("", preceding_code))
        pass




if __name__ == "__main__":
    lex = Lexer("{v1|v2|v3}{v2>v4|v1~v5}")
    parser = Parser(lex)
    parser.parse()
    parser.sentence.print_lst()
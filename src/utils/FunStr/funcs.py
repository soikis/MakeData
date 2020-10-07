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
        # if possible_value is not None:
        #     new_node = Node(sentence_part, possible_value)
        # else:
        #     new_node = Node(sentence_part)

        # if self.head is None:
        #     self.head = new_node
        #     return
        last_node = self.get(sentence_part-1)
        if last_node.has_next:
            raise Exception("It shouldn't have one")
        last_node.next_node = Node(sentence_part)
        # curr_part = 0
        # insertion_point = self.head
        # while curr_part < sentence_part:
        #     curr_part += 1
        #     if insertion_point.next_node is None:
        #         new_node = Node(curr_part)
        #         break
        #     insertion_point = insertion_point.next_node
        
        # # TODO add this to the inside and the asignment aswell.
        # if curr_part != sentence_part:
        #     raise KeyError("Part 1 doesn't exist.")
        
        # # TODO that's incorrect.
        # if insertion_point.has_next:
        #     new_node = insertion_point.next_node
            # insertion_point.next_node = new_node
        # else:
        # insertion_point.next_node = new_node
     
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
        self.escape()


    def consume(self, name):
        if self.lookahead.name == name:
            try:
                self.lookahead = next(self.iter_express)
            except StopIteration:
                self.lookahead = Token(BREAK, BREAK_CHAR)
        
        # TODO raise parse error.
    
    def escape(self):
        
        self.simple_char()
        if self.lookahead.name == ESCAPE:
            self.consume(ESCAPE)
            self.lookahead.name = CHAR
            self.consume(CHAR)
            self.escape()
        
    def simple_char(self):
        self.open_param()
        if self.lookahead.value not in Lexer.symbols:
            self.sentence.get(self.current_sentence_pos).possible_values.append((self.lookahead.value, ))
            self.current_sentence_pos += 1
            self.sentence.append(self.current_sentence_pos)
            self.consume(CHAR)
        if self.lookahead.name == BREAK:
            return
        self.escape()
        
    def open_param(self):
        if self.lookahead.name == PARAM_OPEN:
            groups_counter = 0
            self.consume(PARAM_OPEN) # TODO check how to raise an error if it is PARAM_CLOSE.
            # while self.lookahead.name != PARAM_CLOSE:
            self.preceding(groups_counter)
            if self.lookahead.name is not PARAM_CLOSE:
                raise Exception()
            self.consume(PARAM_CLOSE)
            self.current_sentence_pos += 1
            self.sentence.append(self.current_sentence_pos)
            # self.sentence.insert(self.current_sentence_pos)
        # if self.lookahead.name == PARAM_CLOSE:
        #     self.consume(PARAM_CLOSE)
            # do a simple char check or maybe escape
    
    def preceding(self, group_number):
        self.open_group(group_number, 0)
        if self.lookahead.name == PRECEDING:
            self.consume(PRECEDING)
            self.open_group(group_number, 1)
        elif self.lookahead.name == NOT_PRECEDING:
            self.consume(PRECEDING)
            self.open_group(group_number, -1)
        

    def open_group(self, group_number, preceding_code=0):
        self.variable_name(preceding_code)
        if self.lookahead.name == GROUP_OPEN:
            while self.lookahead.name != GROUP_CLOSE:
                self.consume(GROUP_OPEN)
                self.sentence.get(self.current_sentence_pos).possible_values.append([])
                self.variable_name(preceding_code, group_number)
            group_number += 1
        
    def variable_name(self, preceding_code ,group_number=-1):
        self.qstn(preceding_code, group_number)
        if self.lookahead.name == CHAR:
            variable_name = ""
            while self.lookahead.name == CHAR:
                current = self.lookahead.value
                variable_name += current
                self.consume(CHAR)
                if self.lookahead.name == PARAM_CLOSE:
                    break
                
                if not self.lookahead.value.isidentifier():
                    raise Exception("PARSE ERROR")
            if group_number != -1:
                self.sentence.get(self.current_sentence_pos).possible_values[group_number].append((variable_name, preceding_code))
                self.qstn(preceding_code, group_number)
            else:
                self.sentence.get(self.current_sentence_pos).possible_values.append((variable_name, preceding_code))

    def qstn(self, preceding_code ,group_number=-1):
        # self.alternative()
        if self.lookahead == QSTN:
            self.consume(QSTN)
            if group_number != -1:
                self.sentence.get(self.current_sentence_pos).possible_values[group_number].append(("", preceding_code))
            else:
                self.sentence.get(self.current_sentence_pos).possible_values.append(("", preceding_code))




if __name__ == "__main__":
    lex = Lexer("{please|something}{maybe}")
    parser = Parser(lex)
    parser.parse()
    parser.sentence.print_lst()


# class ParserOld:
#     def __init__(self, lexer):
#         self.lexer = lexer
#         self.tokens = []
#         self.lookahead = self.lexer.get_token()
    
#     def consume(self, name):
#         if self.lookahead.name == name:
#             self.lookahead = self.lexer.get_token()
#         elif self.lookahead.name != name:
#             raise ParseError

#     def parse(self):
#         self.exp()
#         return self.tokens
    
#     def exp(self):
#         self.term()
#         if self.lookahead.name == 'ALT':
#             t = self.lookahead
#             self.consume('ALT')
#             self.exp()
#             self.tokens.append(t)

#     def term(self):
#         self.factor()
#         if self.lookahead.value not in ')|':
#             self.term()
#             self.tokens.append(Token('CONCAT', '\x08'))
    
#     def factor(self):
#         self.primary()
#         if self.lookahead.name in ['STAR', 'PLUS', 'QMARK']:
#             self.tokens.append(self.lookahead)
#             self.consume(self.lookahead.name)

#     def primary(self):
#         if self.lookahead.name == 'LEFT_PAREN':
#             self.consume('LEFT_PAREN')
#             self.exp()
#             self.consume('RIGHT_PAREN')
#         elif self.lookahead.name == 'CHAR':
#             self.tokens.append(self.lookahead)
#             self.consume('CHAR')

# class Handler:
#     pass
# # my state machine

# class TokenOld:
#     def __init__(self, name, value):
#         self.name = name
#         self.value = value

#     def __str__(self):
#         return self.name + ":" + self.value

# class LexerOld:
#     def __init__(self, pattern):
#         self.source = pattern
#         self.symbols = {'(':'LEFT_PAREN', ')':'RIGHT_PAREN', '*':'STAR', '|':'ALT', '\x08':'CONCAT', '+':'PLUS', '?':'QMARK'}
#         self.current = 0
#         self.length = len(self.source)
       
#     def get_token(self): 
#         if self.current < self.length:
#             c = self.source[self.current]
#             self.current += 1
#             if c not in self.symbols.keys(): # CHAR
#                 token = Token('CHAR', c)
#             else:
#                 token = Token(self.symbols[c], c)
#             return token
#         else:
#             return Token('NONE', '')



# class State:
#     def __init__(self, name):
#         self.epsilon = [] # epsilon-closure
#         self.transitions = {} # char : state
#         self.name = name
#         self.is_end = False
    
# class NFA:
#     def __init__(self, start, end):
#         self.start = start
#         self.end = end # start and end states
#         end.is_end = True
    
#     def addstate(self, state, state_set): # add state + recursively add epsilon transitions
#         if state in state_set:
#             return
#         state_set.add(state)
#         for eps in state.epsilon:
#             self.addstate(eps, state_set)
    
#     def pretty_print(self):
#         '''
#         print using Graphviz
#         '''
#         pass
    
#     def match(self,s):
#         current_states = set()
#         self.addstate(self.start, current_states)
        
#         for c in s:
#             next_states = set()
#             for state in current_states:
#                 if c in state.transitions.keys():
#                     trans_state = state.transitions[c]
#                     self.addstate(trans_state, next_states)
           
#             current_states = next_states

#         for s in current_states:
#             if s.is_end:
#                 return True
#         return False

# class HandlerOld:
#     def __init__(self):
#         self.handlers = {'CHAR':self.handle_char, 'CONCAT':self.handle_concat,
#                          'ALT':self.handle_alt, 'STAR':self.handle_rep,
#                          'PLUS':self.handle_rep, 'QMARK':self.handle_qmark}
#         self.state_count = 0

#     def create_state(self):
#         self.state_count += 1
#         return State('s' + str(self.state_count))
    
#     def handle_char(self, t, nfa_stack):
#         s0 = self.create_state()
#         s1 = self.create_state()
#         s0.transitions[t.value] = s1
#         nfa = NFA(s0, s1)
#         nfa_stack.append(nfa)
    
#     def handle_concat(self, t, nfa_stack):
#         n2 = nfa_stack.pop()
#         n1 = nfa_stack.pop()
#         n1.end.is_end = False
#         n1.end.epsilon.append(n2.start)
#         nfa = NFA(n1.start, n2.end)
#         nfa_stack.append(nfa)
    
#     def handle_alt(self, t, nfa_stack):
#         n2 = nfa_stack.pop()
#         n1 = nfa_stack.pop()
#         s0 = self.create_state()
#         s0.epsilon = [n1.start, n2.start]
#         s3 = self.create_state()
#         n1.end.epsilon.append(s3)
#         n2.end.epsilon.append(s3)
#         n1.end.is_end = False
#         n2.end.is_end = False
#         nfa = NFA(s0, s3)
#         nfa_stack.append(nfa)
    
#     def handle_rep(self, t, nfa_stack):
#         n1 = nfa_stack.pop()
#         s0 = self.create_state()
#         s1 = self.create_state()
#         s0.epsilon = [n1.start]
#         if t.name == 'STAR':
#             s0.epsilon.append(s1)
#         n1.end.epsilon.extend([s1, n1.start])
#         n1.end.is_end = False
#         nfa = NFA(s0, s1)
#         nfa_stack.append(nfa)

#     def handle_qmark(self, t, nfa_stack):
#         n1 = nfa_stack.pop()
#         n1.start.epsilon.append(n1.end)
#         nfa_stack.append(n1)

# def compile(p, debug = False):
    
#     def print_tokens(tokens):
#         for t in tokens:
#             print(t)

#     lexer = LexerOld(p)
#     parser = Parser(lexer)
#     tokens = parser.parse()

#     handler = Handler()
    
#     if debug:
#         print_tokens(tokens) 

#     nfa_stack = []
    
#     for t in tokens:
#         handler.handlers[t.name](t, nfa_stack)
    
#     assert len(nfa_stack) == 1
#     return nfa_stack.pop()


# if __name__ == "__main__":
#     nfa = compile('ab+d')
#     if False:
#         nfa.pretty_print()
#     print(nfa.match('ab'))
# Token types
#
# EOF (end-of-file) token is used to indicate that
# there is no more input left for lexical analysis
tokens = {'NUMBER':'NUMBER',
          'STRING':'STRING',
          'PLUS':'PLUS',
          'MINUS':'MINUS',
          'MUL':'MUL',
          'DIV':'DIV',
          'LPAREN':'(',
          'RPAREN':')',
          'LCURLY':'{',
          'RCURLY':'}',
          'ID':'ID',
          'ASSIGN':'ASSIGN',
          'SEMI':'SEMI',
          'EOF':'EOF',
          'COMMA':',',
          'EQ':'==',
          'NEQ':'!=',
          'LT':'<',
          'MT':'>',
          'LEQT':'<=',
          'MEQT':'>=',
          'IF':'IF',
          'WHILE':'WHILE',
          'ELSE':'ELSE',
          'OR':'OR',
          'AND':'AND',
          'VAR':'VAR',
          'DEF':'DEF'
}

def get_tokens():
    return tokens

globals().update(get_tokens())

class Token(object):
    """
    Class representing Token object constructed by lexer.
    """
    def __init__(self, type, value):
        """
        Construct Token object of given type and value.
        :param type: One of token types defined in global space.
        :param value: Value of the token (for example 3 fo INTEGER token).
        """
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        Examples:
            Token(INTEGER, 11)
            Token(PLUS, '+')
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()

# RESERVED KEYWORDS THAT CANNOT BE USED AS IDENTIFIERS
RESERVED_KEYWORDS = {
    'if': Token('IF', 'IF'),
    'else': Token('ELSE', 'ELSE'),
    'and': Token('AND', 'AND'),
    'or': Token('OR', 'OR'),
    'var': Token('VAR', 'VAR'),
    'while': Token('WHILE', 'WHILE'),
    'def': Token('DEF', 'DEF')
}


class Lexer(object):
    """
    lexer class used for tokenizing lines of text.
    """
    def __init__(self, text):
        """
        Construct lexer that will be used to tokenize given line of text.
        :param text: Line of text to tokenize
        """
        self.text = text
        # self.pos is an index into self.text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def error(self):
        raise Exception('Invalid character')

    def advance(self):
        """Advance the `pos` pointer and set the `current_char` variable."""
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Indicates end of input
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """
        Skip whitespace in text.
        """
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def skip_comment(self):
        """
        Skip every character in line after comment sign '#'.
        """
        while self.current_char != '\n':
            self.advance()
        self.advance()

    def string(self):
        """Return a string token"""
        result = ''
        self.advance()
        while self.current_char is not '\"':
            result += self.current_char
            self.advance()

        self.advance()
        return Token('STRING', result)

    def number(self):
        """Return a number token that contains float or integer value."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()

            while (
                    self.current_char is not None and
                    self.current_char.isdigit()
            ):
                result += self.current_char
                self.advance()
            token = Token('NUMBER', float(result))
        else:
            token = Token('NUMBER', int(result))

        return token

    def _id(self):
        """Handle identifiers and reserved keywords"""
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        token = RESERVED_KEYWORDS.get(result.lower(), Token(ID, result))
        return token

    def get_next_token(self):
        """
        Return next token from text.
        """
        while self.current_char is not None:

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isalpha():
                return self._id()

            if self.current_char.isdigit():
                return self.number()

            if self.current_char == '=':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(EQ, '==')
                else:
                    return Token(ASSIGN, '=')

            if self.current_char == '!':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(NEQ, '!=')
                else:
                    self.error()

            if self.current_char == '<':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(LEQT, '<=')
                else:
                    return Token(LT, '<')

            if self.current_char == '>':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(MEQT, '>=')
                else:
                    return Token(MT, '>')

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == ';':
                self.advance()
                return Token(SEMI, ';')

            if self.current_char == '+':
                self.advance()
                return Token(PLUS, '+')

            if self.current_char == '-':
                self.advance()
                return Token(MINUS, '-')

            if self.current_char == '*':
                self.advance()
                return Token(MUL, '*')

            if self.current_char == '/':
                self.advance()
                return Token(DIV, '/')

            if self.current_char == '(':
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ')':
                self.advance()
                return Token(RPAREN, ')')

            if self.current_char == '{':
                self.advance()
                return Token(LCURLY, '{')

            if self.current_char == '}':
                self.advance()
                return Token(RCURLY, '}')

            if self.current_char == '\"':
                return self.string()

            if self.current_char == '#':
                self.advance()
                self.skip_comment()

            self.error()

        return Token(EOF, None)

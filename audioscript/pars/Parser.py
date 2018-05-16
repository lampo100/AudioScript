from lexer.Lexer import get_tokens

globals().update(get_tokens())

class AST(object):
    """
    Base class for all AbstractSyntaxTree node types.
    """
    pass


class Program(AST):
    def __init__(self, root):
        self.root = root


class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class UnaryOp(AST):
    """
    Represents unary operation(plus and minus sign) node.
    """
    def __init__(self, op, numeric_value):
        """
        Unary operation node.
        :param op: Unary operation (plus or minus sign) token.
        :param numeric_value: numeric value
        """
        self.token = self.op = op
        self.value = numeric_value


class StatList(AST):
    """
    Represents list of statements.
    """
    def __init__(self, statements):
        """
        List of statements AST node.
        :param statements: list of statement nodes.
        """
        self.statements = statements


class Assign(AST):
    """
    Represents assignment operation.
    """
    def __init__(self, left, op, right):
        """
        Assign operation node.
        :param left: lvalue
        :param op: assignment token
        :param right: rvalue
        """
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    """The Var node is constructed out of ID token."""
    def __init__(self, token):
        """
        Variable node.
        :param token: ID token representing variable identifier.
        """
        self.token = token
        self.value = token.value


class ConditionalVal(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class NoOp(AST):
    """
    Node representing empty production(nothing happens)
    """
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()

    def error(self, expected=None):
        raise Exception('Invalid syntax, expected {} and got {} instead.'.format(expected, self.current_token.type))

    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error(token_type)

    def program(self):
        """program = statement-list"""
        stat_list = self.statement_list()
        node = Program(stat_list)
        return node

    def statement_list(self):
        """
        statement_list : {statement}*\
        """
        node = self.statement()

        results = [node]

        while self.current_token.type != EOF:
            results.append(self.statement())

        return StatList(results)

    def statement(self):
        """
        statement = block-statement
	    | assignment-statement, semi
	    | function-call, semi
	    | numeric-value, semi
	    | string-value, semi
	    | while-statement
	    | if-statement
	    | empty ;
        """
        if self.current_token.type == ID:
            node = self.assignment_statement()
            self.eat(SEMI)
        elif self.current_token.type == IF:
            self.eat(IF)
            node = self.cond_expr()
            self.eat(SEMI)
        elif self.current_token.type == PLUS or self.current_token.type == MINUS or self.current_token.type == NUMBER or self.current_token.type == LPAREN:
            node = self.numeric_value()
            self.eat(SEMI)
        elif self.current_token.type == STRING:
            node = self.string_value()
            self.eat(SEMI)
        else:
            node = self.empty()
        return node

    def assignment_statement(self):
        """
        assignment-statement = variable, assign, (numeric-value | string-value | nill) ;
        """
        left = self.variable()
        token = self.current_token
        self.eat(ASSIGN)
        if self.current_token.type == STRING:
            right = self.string_value()
        else:
            right = self.numeric_value()

        node = Assign(left, token, right)
        return node

    def string_value(self):
        token = self.current_token
        if token.type == STRING:
            self.eat(STRING)
            return String(token)
        elif token.type == ID:
            self.eat(ID)
            return Var(token)

    def variable(self):
        """
        variable = identifier
        """
        node = Var(self.current_token)
        self.eat(ID)
        return node

    def empty(self):
        """An empty production"""
        return NoOp()

    ############# LOGIC ############
    def cond_expr(self):
        """
        cond-exp = cond-value, {higher-logic-operator, cond-value} ;
        """
        node = self.cond_value()

        while self.current_token.type in (AND, OR):
            token = self.current_token
            if token.type == AND:
                self.eat(AND)
                node = ConditionalVal(node, token, self.cond_value())
            elif token.type == OR:
                self.eat(OR)
                node = ConditionalVal(node, token, self.cond_value())

        return node

    def cond_value(self):
        """
        cond-value = numeric-value, lower-logic-operator, numeric-value ;
        """
        lvalue = self.numeric_value()
        token = self.current_token

        if token.type == EQ:
            self.eat(EQ)
        elif token.type == NEQ:
            self.eat(NEQ)
        elif token.type == LT:
            self.eat(LT)
        elif token.type == MT:
            self.eat(MT)
        elif token.type == LEQT:
            self.eat(LEQT)
        elif token.type == MEQT:
            self.eat(MEQT)
        else:
            self.error("CONDITIONAL-TOKEN")

        rvalue = self.numeric_value()
        return ConditionalVal(lvalue, token, rvalue)

    ############# MATH #############
    def numeric_value(self):
        """
        numeric-value = term, {math-sign, term} ;
        """
        node = self.term()

        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node

    def term(self):
        """term : factor {binary-math-operator, factor}"""
        node = self.factor()

        while self.current_token.type in (MUL, DIV):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def factor(self):
        """factor = unary-operator, factor
                    | integer
                    | float
                    | variable
                    | function-call
                    | lparen, numeric-value, rparen ;
        """
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == NUMBER:
            self.eat(NUMBER)
            return Num(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.numeric_value()
            self.eat(RPAREN)
            return node
        else:
            node = self.variable()
            return node

    def parse(self):
        """
        Parse program and return root node.
        :return:
        """
        node = self.program()
        if self.current_token.type != EOF:
            self.error()

        return node

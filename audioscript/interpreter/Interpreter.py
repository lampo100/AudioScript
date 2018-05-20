from lexer.Lexer import Lexer, get_tokens
from pars.Parser import Parser
from interpreter.symbol_table import ScopedSymbolTable, VarSymbol, FunctionSymbol, BuiltinTypeSymbol, ExternalFunctionSymbol


globals().update(get_tokens())

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.default_visit)
        return visitor(node)

    def default_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))

class Interpreter(NodeVisitor):

    GLOBAL_SCOPE = {}
    GLOBAL_RETURN = None
    FUNCTION_CALL_RETURN_FLAG = False
    ext_functions = {}

    def __init__(self, parser):
        self.parser = parser
        self.current_scope = None
        self.global_scope = None

    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.default_visit)
        if not self.FUNCTION_CALL_RETURN_FLAG:
            return visitor(node)

    def visit_Program(self, node):
        """
        program = declarations, statement-list ;
        """
        print('ENTER scope: global')
        self.global_scope = ScopedSymbolTable(
            scope_name='global',
            scope_level=1,
            enclosing_scope=self.current_scope, # None
        )
        self.global_scope._init_builtins()
        self.current_scope = self.global_scope

        # visit subtree
        if node.declarations is not None:
            self.visit(node.declarations)

        if node.code is not None:
            self.visit(node.code)

        self.current_scope = self.current_scope.enclosing_scope
        print(self.global_scope)
        print('LEAVE scope: global')

    def visit_Declarations(self, node):
        for ext_type in node.types:
            self.visit(ext_type)

        for module in node.modules:
            self.visit(module)

    def visit_DeclaredType(self, node):
        if node.name != 'STRING' and node.name != 'NUMBER':
            self.current_scope.insert(BuiltinTypeSymbol(node.name))

    def visit_ModuleDeclaration(self, node):
        mod = __import__(node.name)
        for function in node.functions:
            globals()[function.name] = mod.__getattribute__(function.name)
            self.visit(function)

    def visit_ExternalFunctionDeclaration(self, node):
        function_name = node.name
        return_type = node.return_type
        args_types = node.arguments_types

        if return_type is not None:
            return_type = self.current_scope.lookup(return_type)

        args_types = [self.current_scope.lookup(arg_type) for arg_type in args_types]

        self.current_scope.insert(ExternalFunctionSymbol(function_name, args_types, return_type))

    def visit_BlockStat(self, node):
        print('ENTER scope: %s' %  "BLOCK SCOPE")
        # Scope for parameters and local variables
        block_scope = ScopedSymbolTable(
            scope_name="block",
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = block_scope

        self.visit(node.list)

        print(block_scope)
        self.current_scope = block_scope.enclosing_scope
        print("LEAVE scope: BLOCK SCOPE")

    def visit_StatList(self, node):
        """
        statement-list = {statement}* ;
        """
        for statement in node.statements:
            print(self.visit(statement))

    def visit_FunctionDeclaration(self, node):
        name = node.name
        args = node.arguments
        body = node.body

        func_symbol = FunctionSymbol(name.value, body, args)
        if self.current_scope.lookup(name.value, current_scope_only=True):
            raise Exception(
                "Error: Duplicate identifier '%s' found" % name.value
            )
        self.current_scope.insert(func_symbol)

    def visit_FunctionCall(self, node):
        function = node.function

        func_symbol = self.current_scope.lookup(function.value)
        if func_symbol is None:
            raise Exception(
                "Error: Unidentified function \"%s\"" % function.name
            )

        if isinstance(func_symbol, ExternalFunctionSymbol):
            func = globals()[func_symbol.name]
            self.GLOBAL_RETURN = func(*[x.value for x in node.args])
            return self.GLOBAL_RETURN

        function_scope = ScopedSymbolTable(
            scope_name="function",
            scope_level=self.current_scope.scope_level + 1,
            enclosing_scope=self.current_scope
        )
        self.current_scope = function_scope

        for name, val in zip(func_symbol.arguments, node.args):
            function_scope.insert(VarSymbol(name, function_scope.lookup('VAR'), self.visit(val)))

        self.visit(func_symbol.body)
        self.FUNCTION_CALL_RETURN_FLAG = False

        self.current_scope = function_scope.enclosing_scope
        return self.GLOBAL_RETURN

    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) / self.visit(node.right)

        self.GLOBAL_RETURN = None

    def visit_Num(self, node):
        return node.value

    def visit_String(self, node):
        return node.value

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.value)
        elif op == MINUS:
            return -self.visit(node.value)

    def visit_If(self, node):
        cond_node = node.cond
        block_node = node.block

        if(self.visit(cond_node)):
            self.visit(block_node)

    def visit_While(self, node):
        cond_node = node.cond
        block_node = node.block

        while(self.visit(cond_node)):
            self.visit(block_node)

    def visit_Assign(self, node):
        # right-hand side
        value = self.visit(node.right)
        # if value is None:
        #     raise Exception(
        #         "Cannot assign None"
        #     )
        # left-hand side

        node = node.left
        var_name = node.value

        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Unidentified variable \"%s\"" % var_name
            )
        var_symbol.value = value
        self.GLOBAL_RETURN = None

    def visit_VarDeclaration(self, node):
        var_type = self.current_scope.lookup(node.type.value)

        for variable in node.names:
            var_symbol = VarSymbol(variable.value, var_type, None)
            if self.current_scope.lookup(variable.value, current_scope_only=True):
                raise Exception(
                    "Error: Duplicate identifier '%s' found" % var_name
                )
            self.current_scope.insert(var_symbol)


    def visit_Return(self, node):
        return_value_node = node.value

        if self.current_scope.scope_level == 1 or self.current_scope.enclosing_scope.scope_name != "function":
            raise Exception(
                "Cannot return outside of function"
            )
        val = self.visit(return_value_node)

        #Really ugly but I don't have time to think about doing it in some other way.
        self.GLOBAL_RETURN = val
        self.FUNCTION_CALL_RETURN_FLAG = True


    def visit_Var(self, node):
        var_name = node.value
        var_symbol = self.current_scope.lookup(var_name)
        if var_symbol is None:
            raise Exception(
                "Error: Symbol(identifier) not found '%s'" % var_name
            )
        return var_symbol.value

    def visit_Function(self, node):
        arguments = node.arguments

    def visit_ConditionalVal(self, node):
        if node.op.type == EQ:
            return self.visit(node.left) == self.visit(node.right)
        elif node.op.type == NEQ:
            return self.visit(node.left) != self.visit(node.right)
        elif node.op.type == LT:
            return self.visit(node.left) < self.visit(node.right)
        elif node.op.type == MT:
            return self.visit(node.left) > self.visit(node.right)
        elif node.op.type == LEQT:
            return self.visit(node.left) <= self.visit(node.right)
        elif node.op.type == MEQT:
            return self.visit(node.left) >= self.visit(node.right)
        elif node.op.type == AND:
            return self.visit(node.left) and self.visit(node.right)
        elif node.op.type == OR:
            return self.visit(node.left) or self.visit(node.right)

    def visit_NoOp(self, node):
        pass

    def interpret(self):
        tree = self.parser.parse()

        return self.visit(tree)


def main():
    # text = input("> ")
    # lexer = Lexer(text)
    # parser = Parser(lexer)
    # interpreter = Interpreter(parser)
    # result = interpreter.interpret()
    # print(interpreter.global_scope)

    filepath = input("Input code path:\n>")
    with open(filepath, 'r') as f:
        text = ""
        for line in f:
            text += line.strip()
        lexer = Lexer(text)
        parser = Parser(lexer)
        int = Interpreter(parser)
        int.interpret()

if __name__ == '__main__':
    main()
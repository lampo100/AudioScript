from collections import OrderedDict
import numbers


class Symbol(object):
    def __init__(self, name, type=None, value=0):
        self.name = name
        self.type = type
        self.value = value


class VarSymbol(Symbol):
    def __init__(self, name, type, value):
        super(VarSymbol, self).__init__(name, type, value)

    def __str__(self):
        return "<{class_name}(name='{name}', type='{type}')> = {value}".format(
            class_name=self.__class__.__name__,
            name=self.name,
            type=self.type,
            value=self.value
        )

    __repr__ = __str__


class BuiltinTypeSymbol(Symbol):
    def __init__(self, name):
        super(BuiltinTypeSymbol, self).__init__(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<{class_name}(name='{name}')>".format(
            class_name=self.__class__.__name__,
            name=self.name,
        )

    __repr__ = __str__


class FunctionSymbol(Symbol):
    def __init__(self, name, body, arguments=None):
        super(FunctionSymbol, self).__init__(name)
        self.arguments = arguments if arguments is not None else []
        self.body = body

    def __str__(self):
        return '<{class_name}(name={name}, arguments={arguments})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            arguments=self.arguments,
        )

    __repr__ = __str__


class ExternalFunctionSymbol(Symbol):
    def __init__(self, name, arguments_types=None, return_type = None):
        super(ExternalFunctionSymbol, self).__init__(name)
        self.arguments_types = arguments_types if arguments_types is not None else []
        self.return_type = return_type

    def __str__(self):
        return '<{class_name}(name={name}, arguments types={arguments}, return type={return_type})>'.format(
            class_name=self.__class__.__name__,
            name=self.name,
            arguments=self.arguments_types,
            return_type=self.return_type
        )

    __repr__ = __str__


class ScopedSymbolTable(object):
    def __init__(self, scope_name, scope_level, enclosing_scope=None):
        self._symbols = OrderedDict()
        self.scope_name = scope_name
        self.scope_level = scope_level
        self.enclosing_scope = enclosing_scope

    def _init_builtins(self):
        self.insert(BuiltinTypeSymbol('NUMBER'))
        self.insert(BuiltinTypeSymbol('STRING'))
        self.insert(BuiltinTypeSymbol('VAR'))

    def __str__(self):
        h1 = 'SCOPE (SCOPED SYMBOL TABLE)'
        lines = ['\n', h1, '=' * len(h1)]
        for header_name, header_value in (

            ('Scope name', self.scope_name),
            ('Scope level', self.scope_level),
            ('Enclosing scope',
             self.enclosing_scope.scope_name if self.enclosing_scope else None
            )
        ):
            lines.append('%-15s: %s' % (header_name, header_value))
        h2 = 'Scope (Scoped symbol table) contents'
        lines.extend([h2, '-' * len(h2)])
        lines.extend(
            ('%7s: %r' % (key, value))
            for key, value in self._symbols.items()
        )
        lines.append('\n')
        s = '\n'.join(lines)
        return s

    __repr__ = __str__

    def insert(self, symbol):
        #print('Insert: %s' % symbol.name)
        self._symbols[symbol.name] = symbol

    def lookup(self, name, current_scope_only=False):
        #print('Lookup: %s. (Scope name: %s)' % (name, self.scope_name))
        # 'symbol' is either an instance of the Symbol class or None
        symbol = self._symbols.get(name)

        if symbol is not None:
            return symbol

        if current_scope_only:
            return None

        # recursively go up the chain and lookup the name
        if self.enclosing_scope is not None:
            return self.enclosing_scope.lookup(name)

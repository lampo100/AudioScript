###############################################################################
#  AST visualizer - generates a DOT file for Graphviz.                        #
#                                                                             #
#  To generate an image from the DOT file run $ dot -Tpng -o ast.png ast.dot  #
#                                                                             #
###############################################################################
import textwrap
from graphviz import render

from interpreter.Interpreter import NodeVisitor
from lexer.Lexer import Lexer
from pars.Parser import Parser


class ASTVisualizer(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=circle, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]

        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def visit_Program(self, node):
        """
        program = declarations, statement-list ;
        """
        s = '  node{} [label="Program"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        if node.declarations is not None:
            self.visit(node.declarations)
            s = '  node{} -> node{}\n'.format(node._num, node.declarations._num)
            self.dot_body.append(s)

        self.visit(node.code)
        s = '  node{} -> node{}\n'.format(node._num, node.code._num)
        self.dot_body.append(s)

    def visit_DeclaredType(self, node):
        s = '  node{} [label="External type: {}"]\n'.format(self.ncount, node.name)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_ExternalFunctionDeclaration(self, node):
        s = '  node{} [label="External Function\\nDeclaration:\\n {} {}({})"]\n'.format(self.ncount, node.return_type, node.name,
                                                                              ', '.join(node.arguments_types))
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_ModuleDeclaration(self, node):
        s = '  node{} [label="Module: {}"]\n'.format(self.ncount, node.name)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for function in node.functions:
            self.visit(function)
            s = '  node{} -> node{}\n'.format(node._num, function._num)
            self.dot_body.append(s)

    def visit_Declarations(self, node):
        s = '  node{} [label="Declarations"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for ext_type in node.types:
            self.visit(ext_type)
            s = '  node{} -> node{}\n'.format(node._num, ext_type._num)
            self.dot_body.append(s)

        for module in node.modules:
            self.visit(module)
            s = '  node{} -> node{}\n'.format(node._num, module._num)
            self.dot_body.append(s)

    def visit_BlockStat(self, node):
        s = '  node{} [label="Block"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.list)
        s = '  node{} -> node{}\n'.format(node._num, node.list._num)
        self.dot_body.append(s)

    def visit_StatList(self, node):
        s = '  node{} [label="Statement List"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for statement in node.statements:
            self.visit(statement)
            s = '  node{} -> node{}\n'.format(node._num, statement._num)
            self.dot_body.append(s)

    def visit_Var(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_VarDeclaration(self, node):
        s = '  node{} [label="Var\\nDeclaration: {}"]\n'.format(self.ncount, node.type.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for variable, i in zip(node.names, range(1, len(node.names) + 1)):
            s = '  node{} -> node{}\n'.format(node._num, node._num + i)
            ns = '  node{} [label="{}"]\n'.format(node._num + i, variable.value)
            self.dot_body.extend((s, ns))

        self.ncount += len(node.names)

    def visit_Num(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_ConditionalVal(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_String(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.token.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def visit_If(self, node):
        s = '  node{} [label="If"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.cond)
        self.visit(node.block)
        self.dot_body.append('  node{} -> node{}\n'.format(node._num, node.cond._num))
        self.dot_body.append('  node{} -> node{}\n'.format(node._num, node.block._num))

    def visit_Return(self, node):
        s = '  node{} [label="Return"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.value)
        s = '  node{} -> node{}\n'.format(node._num, node.value._num)
        self.dot_body.append(s)

    def visit_FunctionDeclaration(self, node):
        s = '  node{} [label="Function \\nDeclaration: {}"]\n'.format(self.ncount, node.name.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        for arg, i in zip(node.arguments, range(1, len(node.arguments) + 1)):
            ns = '  node{} [label="{}"]\n'.format(node._num + i, arg)
            s = '  node{} -> node{}\n'.format(node._num, node._num + i)
            self.dot_body.extend((s, ns))

        self.ncount += len(node.arguments)

        self.visit(node.body)
        self.dot_body.append('  node{} -> node{}\n'.format(node._num, node.body._num))

    def visit_FunctionCall(self, node):
        args_values = [str(val.value) for val in node.args]
        s = '  node{} [label="{}({})"]\n'.format(self.ncount, node.function.value, ', '.join(args_values))
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1



    def visit_While(self, node):
        s = '  node{} [label="While"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.cond)
        self.visit(node.block)
        self.dot_body.append('  node{} -> node{}\n'.format(node._num, node.cond._num))
        self.dot_body.append('  node{} -> node{}\n'.format(node._num, node.block._num))

    def visit_BinOp(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_UnaryOp(self, node):
        s = '  node{} [label="unary {}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.value)
        s = '  node{} -> node{}\n'.format(node._num, node.value._num)
        self.dot_body.append(s)

    def visit_Assign(self, node):
        s = '  node{} [label="{}"]\n'.format(self.ncount, node.op.value)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

        self.visit(node.left)
        self.visit(node.right)

        for child_node in (node.left, node.right):
            s = '  node{} -> node{}\n'.format(node._num, child_node._num)
            self.dot_body.append(s)

    def visit_NoOp(self, node):
        s = '  node{} [label="NoOp"]\n'.format(self.ncount)
        self.dot_body.append(s)
        node._num = self.ncount
        self.ncount += 1

    def gendot(self):
        tree = self.parser.parse()
        self.visit(tree)
        return ''.join(self.dot_header + self.dot_body + self.dot_footer)


def main():
    filepath = input("Input code path:\n>")
    with open(filepath, 'r') as f:
        text = ""
        for line in f:
            text += line.strip()
        lexer = Lexer(text)
        parser = Parser(lexer)
        viz = ASTVisualizer(parser)
        content = viz.gendot()
        print(content)

    print(text)

    with open("./AST.dot", 'w') as f:
        f.write(content)


if __name__ == '__main__':
    main()

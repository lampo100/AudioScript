import audioscript.interpreter.Interpreter
import audioscript.lexer.Lexer
import audioscript.pars.Parser

if __name__ == '__main__':
    filepath = input("Input code path:\n>")
    with open(filepath, 'r') as f:
        text = ""
        for line in f:
            text += line.strip()
        lexer = audioscript.lexer.Lexer.Lexer(text)
        parser = audioscript.pars.Parser.Parser(lexer)
        int = audioscript.interpreter.Interpreter.Interpreter(parser)
        int.interpret()
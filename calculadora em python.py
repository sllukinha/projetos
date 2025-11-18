import ast
import operator as op
import math
import sys

#!/usr/bin/env python3
# calculadora em python - CLI segura
# Use expressões com + - * / // % **, parênteses e funções: sin, cos, tan, sqrt, log, exp, pow, floor, ceil
# Digite 'exit' ou 'quit' para sair.


ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.FloorDiv: op.floordiv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
}

ALLOWED_UNARYOPS = {
    ast.UAdd: lambda x: x,
    ast.USub: op.neg,
}

ALLOWED_FUNCS = {
    'sin': math.sin,
    'cos': math.cos,
    'tan': math.tan,
    'sqrt': math.sqrt,
    'log': math.log,    # natural log; log(x, base) supported via two args
    'exp': math.exp,
    'pow': math.pow,
    'floor': math.floor,
    'ceil': math.ceil,
    'abs': abs,
}

ALLOWED_CONSTS = {
    'pi': math.pi,
    'e': math.e,
}

def safe_eval(expr, names):
    """
    Avalia expressão aritmética segura usando AST.
    names: dict com nomes permitidos (por ex. '_' para último resultado)
    """
    node = ast.parse(expr, mode='eval')

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant):  # Python 3.8+
            if isinstance(n.value, (int, float)):
                return n.value
            raise ValueError("Constante não numérica")
        if isinstance(n, ast.Num):  # fallback
            return n.n
        if isinstance(n, ast.BinOp):
            if type(n.op) not in ALLOWED_BINOPS:
                raise ValueError("Operador binário não permitido")
            left = _eval(n.left)
            right = _eval(n.right)
            return ALLOWED_BINOPS[type(n.op)](left, right)
        if isinstance(n, ast.UnaryOp):
            if type(n.op) not in ALLOWED_UNARYOPS:
                raise ValueError("Operador unário não permitido")
            return ALLOWED_UNARYOPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.Call):
            if not isinstance(n.func, ast.Name):
                raise ValueError("Chamada de função inválida")
            fname = n.func.id
            if fname not in ALLOWED_FUNCS:
                raise ValueError(f"Função '{fname}' não permitida")
            args = [_eval(a) for a in n.args]
            return ALLOWED_FUNCS[fname](*args)
        if isinstance(n, ast.Name):
            idn = n.id
            if idn in names:
                return names[idn]
            if idn in ALLOWED_CONSTS:
                return ALLOWED_CONSTS[idn]
            raise ValueError(f"Nome '{idn}' não definido")
        if isinstance(n, ast.Tuple):
            return tuple(_eval(elt) for elt in n.elts)
        raise ValueError(f"Nó AST não permitido: {type(n).__name__}")

    return _eval(node)

def repl():
    last = 0
    print("Calculadora (digite 'exit' ou 'quit'). Exemplos: 2+3*4, sqrt(2), pow(2,3), pi*2")
    try:
        while True:
            try:
                s = input("calculadora> ").strip()
            except EOFError:
                print()
                break
            if not s:
                continue
            if s.lower() in ('exit', 'quit'):
                break
            try:
                result = safe_eval(s, {'_': last})
                print(result)
                last = result
            except Exception as e:
                print("Erro:", e)
    except KeyboardInterrupt:
        print()
    print("Saindo.")

if __name__ == "__main__":
    repl()
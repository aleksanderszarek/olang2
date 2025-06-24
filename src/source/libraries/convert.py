'''
This module provides functionality for converting expressions
Instructions:
- int(value): Converts the value to an integer.
- float(value): Converts the value to a float.
- str(value): Converts the value to a string.
- bool(value): Converts the value to a boolean.
- type(value): Returns the type of the value as a string.
'''
import re
def eval_value(value: str, run_object, throw_error) -> object:
    value = str(value).strip()

    if value.startswith('-'):
        value = '0' + value  # handle things like -x

    if value.count("[") != value.count("]"):
        throw_error("Mismatched brackets in the expression.", True, value)
        return False

    tokens = []
    current = ""
    depth = 0
    in_string = False
    string_char = ""
    i = 0

    while i < len(value):
        c = value[i]

        if in_string:
            current += c
            if c == string_char:
                in_string = False
            i += 1
            continue

        if c in "\"'":
            in_string = True
            string_char = c
            current += c
        elif c in "([{":
            depth += 1
            current += c
        elif c in ")]}":
            depth -= 1
            current += c
        elif c in "+-*/^" and depth == 0:
            if current.strip():
                tokens.append(current.strip())
            tokens.append(c)
            current = ""
        else:
            current += c
        i += 1

    if current.strip():
        tokens.append(current.strip())

    # Evaluate each token
    result_tokens = []
    for token in tokens:
        if token in "+-*/^":
            result_tokens.append(token)
            continue
        try:
            result_tokens.append(str(float(token)))
        except ValueError:
            try:
                result_tokens.append(str(run_object(token)))
            except Exception as e:
                throw_error(f"Could not evaluate token '{token}'", True, token)
                return False

    expr = "".join(result_tokens).replace('^', '**')

    try:
        return eval(expr, {"__builtins__": None}, {})
    except Exception as e:
        throw_error(f"Evaluation failed for '{expr}': {e}", True, expr)
        return False
def split_args(content: str) -> list[str]:
    args = []
    current = ""
    depth = 0
    in_string = False
    string_char = ""

    for c in content:
        if in_string:
            current += c
            if c == string_char:
                in_string = False
            continue

        if c in "\"'":
            in_string = True
            string_char = c
            current += c
        elif c == "," and depth == 0:
            args.append(current.strip())
            current = ""
        else:
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            current += c

    if current:
        args.append(current.strip())

    return args

class MainLib:
    def int(self, arg: str, run_object, throw_error):
        content = arg.strip()[arg.find('(') + 1:arg.rfind(')')].replace("\\n", "\n").replace("\\t", "\t")
        content = eval_value(content, run_object, throw_error)
        if isinstance(content, (int, float, bool)):
            return int(content)
        elif isinstance(content, str):
            try:
                return int(content)
            except ValueError:
                throw_error("Cannot convert to int.", True, arg)
                return 0
        else:
            throw_error("Unsupported type for int conversion.", True, arg)
            return 0
    def float(self, arg: str, run_object, throw_error):
        content = arg.strip()[arg.find('(') + 1:arg.rfind(')')].replace("\\n", "\n").replace("\\t", "\t")
        content = eval_value(content, run_object, throw_error)
        if isinstance(content, (int, float, bool)):
            return float(content)
        elif isinstance(content, str):
            try:
                return int(content)
            except ValueError:
                throw_error("Cannot convert to float.", True, arg)
                return 0
        else:
            throw_error("Unsupported type for float conversion.", True, arg)
            return 0
    def str(self, arg: str, run_object, throw_error):
        content = arg.strip()[arg.find('(') + 1:arg.rfind(')')].replace("\\n", "\n").replace("\\t", "\t")
        content = eval_value(content, run_object, throw_error)
        return str(content)
            
    def bool(self, arg: str, run_object, throw_error):
        content = arg.strip()[arg.find('(') + 1:arg.rfind(')')].replace("\\n", "\n").replace("\\t", "\t")
        content = eval_value(content, run_object, throw_error)
        if isinstance(content, (int, float, bool)):
            return int(content)
        elif isinstance(content, str):
            try:
                return 0 if content.lower() in ["false", "0", 0] else 1
            except ValueError:
                throw_error("Cannot convert to bool.", True, arg)
                return 0
        else:
            throw_error("Unsupported type for bool conversion.", True, arg)
            return 0
            
    

l = MainLib()
instructions: list[str] = ["int", "float", "str", "bool"]
variables: list[object] = [l.int, l.float, l.str, l.bool]
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
    value = str(value)
    raw_value = value.replace(" ", "").replace(",", "$")
    values = raw_value.replace("+", ",").replace("-", ",").replace("*", ",").replace("/", ",").replace("^", ",").split(",")

    vals = []
    valchars = []
    bracketstarts = []
    bracketends = []
    v = []

    # Operators
    for i in value:
        if i in '+-*/^%^':
            valchars.append(i)

    # Bracket mismatch check
    if value.count("[") != value.count("]"):
        throw_error("Mismatched brackets in the expression.", True, value)
        return False

    if len(values) > 1:
        for i, val in enumerate(values):
            if val.startswith("["):
                bracketstarts.append(i)
                val = val[1:]
            if val.endswith("]"):
                val = val[:-1]
                bracketends.append(i+1)

            # Handle values
            try:
                val = float(val)
            except ValueError:
                # Detect function call
                if re.match(r"^[a-zA-Z_]\w*\(.*\)$", val.replace("$", ",")):
                    val = run_object(val.replace("$", ","))
                else:
                    val = run_object(val.replace("$", ","))
            vals.append(val)

        for i, val in enumerate(vals):
            while i in bracketstarts:
                v.append('(')
                bracketstarts.remove(i)
            while i in bracketends:
                v.append(')')
                bracketends.remove(i)
            v.append(str(val))
            if i < len(vals) - 1:
                v.append(str(valchars[i]))

        if bracketends:
            v.append(')')

    else:
        # Handle standalone value
        try:
            return float(value)
        except ValueError:
            return run_object(value)

    evaluated = "".join(v).replace('^', '**').replace('[','(').replace(']',')')

    try:
        return eval(evaluated)
    except Exception as e:
        throw_error(f"Evaluation failed for '{evaluated}'", True, evaluated)
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
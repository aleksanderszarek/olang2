'''
This module provides main functionality for running objects, printing strings to the screen or getting input values.
Instructions:
- exec(object_name, arg1, arg2, ...): Executes an object with the given name and arguments.
- write(arg1, arg2, ...): Prints the given arguments to the console.
- writeline(arg1, arg2, ...): Prints the given arguments to the console followed by a newline.
- read(): Reads input from the user and returns it as a string.
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

    def exec(self, arg: str, run_object, throw_error):
        # content = arg.strip()[arg.find('(') + 1:arg.rfind(')')].replace("\\n", "\n").replace("\\t", "\t")
        # items = split_args(content)
        # if len(items) > 0:
        #     name = items[0]
        #     if len(items) > 1:
        #         args = items[1:]
        #     else:
        #         args = []
        #     obj = run_object(f"god({name})")
        #     obj.args
        #     obj.body
        return
    def write(self, arg: str, run_object, throw_error):
        content = arg.strip()[arg.find('(') + 1:arg.rfind(')')].replace("\\n", "\n").replace("\\t", "\t")
        items = split_args(content)

        for item in items:
            item = item.strip()
            if item.startswith("'") and item.endswith("'"):
                print(item[1:-1], end="")
            elif item.startswith('"') and item.endswith('"'):
                print(item[1:-1], end="")
            else:
                try:
                    print(float(item), end="")
                except ValueError:
                    print(eval_value(item, run_object, throw_error), end="")
    def writeline(self, arg: str, run_object, throw_error):
        self.write(arg, run_object, throw_error)
        print()
    def read(self, arg: str, run_object, throw_error) -> str:
        if arg.strip() != "read()":
            throw_error("Invalid read function syntax. Expected 'read()'.", True, arg)
            return ""
        try:
            return input()
        except EOFError:
            throw_error("Input was interrupted or EOF reached.", False, arg)
            return ""

l = MainLib()
instructions: list[str] = ["exec","write","writeline","read"]
variables: list[object] = [l.exec, l.write, l.writeline, l.read]
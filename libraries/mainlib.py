'''
This module provides main functionality for running objects, printing strings to the screen or getting input values.
Instructions:
- exec(object_name, arg1, arg2, ...): Executes an object with the given name and arguments.
- write(arg1, arg2, ...): Prints the given arguments to the console.
- writeline(arg1, arg2, ...): Prints the given arguments to the console followed by a newline.
- read(): Reads input from the user and returns it as a string.
- if(condition) => instruction: Executes the instruction if the condition is true.
'''
import re, json
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
        try:
            args_string = arg.strip()[arg.find('(') + 1:arg.rfind(')')]
            args = [a.strip() for a in split_args(args_string)]

            if len(args) < 1:
                throw_error("exec(...) requires at least one argument", True, arg)
                return

            raw_name = args[0]
            arguments = args[1:]

            try:
                name_value = run_object(raw_name)
            except Exception:
                name_value = raw_name.strip("\"'")

            try:
                god_result = run_object(f'god({name_value})')
            except Exception as e:
                throw_error(f"Error resolving god(...): {e}", True, arg)
                return

            code = god_result["body"]
            parameters = god_result.get("args", [])

            if len(arguments) != len(parameters):
                throw_error(f"Function {name_value} expected {len(parameters)} args, got {len(arguments)}", True, arg)
                return

            for param, raw_arg in zip(parameters, arguments):
                if ':' not in param:
                    throw_error(f"Invalid parameter format: {param}. Expected 'name:type'.", True, arg)
                    return
                param_name, param_type = [p.strip() for p in param.split(':')]

                evaluated = run_object(raw_arg)

                # Handle quoting string values explicitly
                if isinstance(evaluated, str):
                    value_repr = f'"{evaluated}"'
                elif isinstance(evaluated, bool):
                    value_repr = "true" if evaluated else "false"
                else:
                    value_repr = str(evaluated)

                run_object(f"declare({param_name}, {param_type}, {value_repr})")

            for ins in code:
                run_object(ins)

        except Exception as e:
            throw_error(f"Failed to execute exec: {e}", True, arg)
    
    def if_statement(self, arg: str, run_object, throw_error):
        try:
            parts = arg.strip().split('=>', 1)
            if len(parts) != 2:
                throw_error("Missing '=>' in if statement", True, arg)
                return

            condition_str = parts[0].strip()
            instruction = parts[1].strip()
            if not condition_str.startswith("if(") or not condition_str.endswith(")"):
                throw_error("Invalid if statement syntax", True, arg)
                return
            condition_expr = condition_str[3:-1].strip()
            def xor(a, b): return bool(a) != bool(b)
            func_call_pattern = r'\b([a-zA-Z_]\w*)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)'
            while True:
                matches = list(re.finditer(func_call_pattern, condition_expr))
                if not matches:
                    break
                for match in reversed(matches): 
                    full_call = match.group(0)
                    try:
                        result = run_object(full_call)
                    except Exception as e:
                        throw_error(f"Error evaluating expression `{full_call}`: {e}", True, arg)
                        return
                    if isinstance(result, str):
                        result = f'"{result}"'
                    elif result is None:
                        result = "None"

                    condition_expr = condition_expr[:match.start()] + str(result) + condition_expr[match.end():]
            result = eval(condition_expr, {"__builtins__": None}, {"xor": xor})
            if result:
                return run_object(instruction)

        except Exception as e:
            throw_error(f"Failed to execute if_statement: {e}", True, arg)

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
instructions: list[str] = ["exec","write","writeline","read", "if"]
variables: list[object] = [l.exec, l.write, l.writeline, l.read, l.if_statement]
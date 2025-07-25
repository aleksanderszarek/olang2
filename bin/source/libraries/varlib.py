'''
This module provides a variable library for managing variables in a script such as declaring, setting, getting, deleting, and checking types of variables.
Instructions:
- declare(name, type, value): Declares a variable with the specified name, type (int, float, str, bool), and optional initial value.
- set(name, value): Sets the value of an existing variable.
- get(name): Returns the value of the specified variable.
- typeof(name): Returns the type of the specified variable.
- delete(name): Deletes the specified variable.
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
class Variable:
    def __init__(self, name: str, type: int, value: object):
        self.name = name
        self.type = type
        self.type_name = "int" if type == 1 else "float" if type == 2 else "str" if type == 3 else "bool" if type == 4 else "object"
        self.value = value
    def get_value(self) -> object:
        return self.value
    def set_value(self, value, run_object, throw_error) -> bool:
        evaluated = eval_value(value, run_object, throw_error)
        if self.type == 1:  # int
            if isinstance(evaluated, int):
                self.value = evaluated
                return True
            elif isinstance(evaluated, (float, bool)):
                self.value = int(evaluated)
                return True
            elif isinstance(evaluated, str):
                try:
                    self.value = int(evaluated)
                    return True
                except ValueError:
                    return False
            else:
                return False

        elif self.type == 2:  # float
            if isinstance(evaluated, (float, int, bool)):
                self.value = float(evaluated)
                return True
            elif isinstance(evaluated, str):
                try:
                    self.value = float(evaluated)
                    return True
                except ValueError:
                    return False
            else:
                return False

        elif self.type == 3:  # str
            if isinstance(evaluated, str):
                self.value = evaluated
            else:
                self.value = str(evaluated)
            return True

        elif self.type == 4:  # bool
            if isinstance(evaluated, bool):
                self.value = evaluated
                return True
            elif isinstance(evaluated, (int, float)):
                self.value = evaluated != 0
                return True
            elif isinstance(evaluated, str):
                if evaluated.lower() in ["true", "false"]:
                    self.value = evaluated.lower() == "true"
                    return True
                return False
            else:
                return False

        return False
def parse_args(arg_str: str) -> list[str]:
    # Extract the content inside the outermost parentheses
    match = re.search(r"\((.*)\)", arg_str)
    if not match:
        return []

    content = match.group(1)
    args = []
    depth = 0
    current = ""

    for c in content:
        if c == "," and depth == 0:
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
class VarLib:
    def __init__(self):
        self.variables = []
    
    def declare_variable(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 2:
            name, type_str = args
            value = None
        elif len(args) == 3:
            name, type_str, value = args
        else:
            throw_error(f"Invalid declare syntax: {arg}", True, arg)
            return
        if any(var.name == name for var in self.variables):
            throw_error(f"Variable '{name}' already exists.", True, arg)
            return
        type_map = {"int": 1, "float": 2, "str": 3, "bool": 4}
        if type_str not in type_map:
            throw_error(f"Invalid type '{type_str}' for variable '{name}'. Expected one of {list(type_map.keys())}.", True, arg)
            return

        var_type = type_map[type_str]
        new_var = Variable(name, var_type, None)

        if len(args) == 3:
            if not new_var.set_value(value, run_object, throw_error):
                throw_error(f"Cannot assign the value for variable '{name}'. Expected {type_str}, got {str(type(value))[8:-2]}.", True, arg)

        self.variables.append(new_var)
    def set_variable(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) != 2:
            throw_error(f"Invalid set syntax: {arg}", True, arg)
            return
        name, value = args
        for var in self.variables:
            if var.name == name:
                if not var.set_value(value, run_object, throw_error):
                    throw_error(f"Cannot assign the value '{value}' to variable '{name}'. Expected type {var.type_name}, got {type(value).__name__}.", True, arg)
                return

        throw_error(f"Could not find '{name}' in the scope!", True, arg)
    def get_variable(self, arg: str, run_object, throw_error):
        content = arg.split("(")[1].split(")")[0].replace(" ", "").split(",")
        if len(content) == 1:
            name = content[0]
            for var in self.variables:
                if var.name == name:
                    return var.get_value()
            throw_error(f"Could not find '{name}' in the scope!", False, arg)
        else:
            throw_error(f"Invalid function declaration format. Expected: get(name).", True, arg)
        return None
    def typeof_variable(self, arg: str, run_object, throw_error) -> str:
        content = arg.split("(")[1].split(")")[0].replace(" ", "").split(",")
        if len(content) == 1:
            name = content[0]
            for var in self.variables:
                if var.name == name:
                    return var.type_name
        return "unknown"
    def delete_variable(self, arg: str, run_object, throw_error) -> None:
        content = arg.split("(")[1].split(")")[0].replace(" ", "").split(",")
        if len(content) == 1:
            name = content[0]
            for var in self.variables:
                if var.name == name:
                    self.variables.remove(var)
                    return
            throw_error(f"Could not find '{name}' in the scope!", True, arg)
        throw_error("Invalid function declaration format. Expected: delete(name).", True, arg)
        return
    def exists_variable(self, arg: str, run_object, throw_error) -> bool:
        content = arg.split("(")[1].split(")")[0].replace(" ", "").split(",")
        if len(content) == 1:
            name = content[0]
            for var in self.variables:
                if var.name == name:
                    return True
            return False
        throw_error("Invalid function declaration format. Expected: exists(name).", True, arg)
        return False
l = VarLib()
instructions: list[str] = ["declare", "set", "get", "delete", "typeof", "exists"]
variables: list[object] = [l.declare_variable, l.set_variable, l.get_variable, l.delete_variable, l.typeof_variable, l.exists_variable]
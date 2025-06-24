'''
This module provides functionality for arrays in a script such as creating, accessing, modifying, and deleting arrays.
Instructions:
- declare[](name, type): Creates an array with the specified name and type (int, float, str, bool).
- get[](name, index): Returns the value at the specified index in the array. If no index - returns the whole array.
- set[](name, index, value): Sets the value at the specified index in the array.
- append[](name, value): Appends a value to the end of the array.
- delete[](name, index): Deletes the value at the specified index in the array. If no index - deletes the whole array.
- length[](name): Returns the length of the array.
- clear[](name): Clears the array, removing all elements.
- contains[](name, value): Checks if the array contains the specified value.
- sort[](name): Sorts the array in ascending order.
- reverse[](name): Reverses the order of elements in the array.
- indexof[](name, value): Returns the index of the first occurrence of the specified value in the array.
- lastindexof[](name, value): Returns the index of the last occurrence of the specified value in the array.
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
class Arrays:
    def __init__(self, name: str, type: int, value: list[object]):
        self.name = name
        self.type = type
        self.type_name = "int" if type == 1 else "float" if type == 2 else "str" if type == 3 else "bool" if type == 4 else "object"
        self.value = value
    def get_value(self, index) -> object:
        return self.value[index] if 0 <= index < len(self.value) else None
    def set_value(self, value, index,  run_object, throw_error) -> bool:
        evaluated = eval_value(value, run_object, throw_error)
        if self.type == 1:  # int
            if isinstance(evaluated, int):
                self.value[index] = evaluated
                return True
            elif isinstance(evaluated, (float, bool)):
                self.value[index] = int(evaluated)
                return True
            elif isinstance(evaluated, str):
                try:
                    self.value[index] = int(evaluated)
                    return True
                except ValueError:
                    return False
            else:
                return False

        elif self.type == 2:  # float
            if isinstance(evaluated, (float, int, bool)):
                self.value[index] = float(evaluated)
                return True
            elif isinstance(evaluated, str):
                try:
                    self.value[index] = float(evaluated)
                    return True
                except ValueError:
                    return False
            else:
                return False
        elif self.type == 3:  # str
            if isinstance(evaluated, str):
                self.value[index] = evaluated
            else:
                self.value[index] = str(evaluated)
            return True

        elif self.type == 4:  # bool
            if isinstance(evaluated, bool):
                self.value[index] = evaluated
                return True
            elif isinstance(evaluated, (int, float)):
                self.value[index] = evaluated != 0
                return True
            elif isinstance(evaluated, str):
                if evaluated.lower() in ["true", "false"]:
                    self.value[index] = evaluated.lower() == "true"
                    return True
                return False
            else:
                return False

        return False
    def append_value(self, value,  run_object, throw_error) -> bool:
        evaluated = eval_value(value, run_object, throw_error)
        if self.type == 1:  # int
            if isinstance(evaluated, int):
                self.value.append(evaluated)
                return True
            elif isinstance(evaluated, (float, bool)):
                self.value.append(int(evaluated))
                return True
            elif isinstance(evaluated, str):
                try:
                    self.value.append(int(evaluated))
                    return True
                except ValueError:
                    return False
            else:
                return False

        elif self.type == 2:  # float
            if isinstance(evaluated, (float, int, bool)):
                self.value.append(float(evaluated))
                return True
            elif isinstance(evaluated, str):
                try:
                    self.value.append(float(evaluated))
                    return True
                except ValueError:
                    return False
            else:
                return False

        elif self.type == 3:  # str
            if isinstance(evaluated, str):
                self.value.append(evaluated)
            else:
                self.value.append(str(evaluated))
            return True

        elif self.type == 4:  # bool
            if isinstance(evaluated, bool):
                self.value.append(evaluated)
                return True
            elif isinstance(evaluated, (int, float)):
                self.value.append(evaluated != 0)
                return True
            elif isinstance(evaluated, str):
                if evaluated.lower() in ["true", "false"]:
                    self.value.append(evaluated.lower() == "true")
                    return True
                return False
            else:
                return False

        return False
    def delete_value(self, index) -> bool:
        if 0 <= index < len(self.value):
            del self.value[index]
            return True
        return False
    def length(self) -> int:
        return len(self.value)
    def clear(self) -> None:
        self.value.clear()
    def contains(self, value, run_object, throw_error) -> bool:
        evaluated = eval_value(value, run_object, throw_error)
        return evaluated in self.value
    def sort(self) -> None:
        if self.type in [1, 2]:
            self.value.sort()
        elif self.type == 3:
            self.value.sort(key=lambda x: str(x))
        elif self.type == 4:
            self.value.sort(key=lambda x: bool(x))
    def reverse(self) -> None:
        self.value.reverse()
    def index_of(self, value, run_object, throw_error) -> int:
        evaluated = eval_value(value, run_object, throw_error)
        try:
            return self.value.index(evaluated)
        except ValueError:
            return -1
    def last_index_of(self, value, run_object, throw_error) -> int:
        evaluated = eval_value(value, run_object, throw_error)
        try:
            return len(self.value) - 1 - self.value[::-1].index(evaluated)
        except ValueError:
            return -1
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
        self.arrays = []
    
    def declare_array(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 2:
            name, type_str = args
        else:
            throw_error(f"Invalid declare syntax: {arg}", True, arg)
            return

        type_map = {"int": 1, "float": 2, "str": 3, "bool": 4}
        if type_str not in type_map:
            throw_error(f"Invalid type '{type_str}' for array '{name}'. Expected one of {list(type_map.keys())}.", True, arg)
            return
        if any(array.name == name for array in self.arrays):
            throw_error(f"Array '{name}' already exists.", True, arg)
            return
        var_type = type_map[type_str]
        new_var = Arrays(name, var_type, [])

        self.arrays.append(new_var)
    
    def set_array(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 3:
            name, index, type_str = args
            index = eval_value(index, run_object, throw_error)
            try:
                index = int(index)
            except ValueError:
                throw_error(f"Invalid index '{index}' for array '{name}'. Index must be an integer.", True, arg)
                return
        else:
            throw_error(f"Invalid set syntax: {arg}", True, arg)
            return
        if not any(array.name == name for array in self.arrays):
            throw_error(f"Array '{name}' does not exist.", True, arg)
            return
        for array in self.arrays:
            if array.name == name:
                if not array.set_value(type_str, index, run_object, throw_error):
                    throw_error(f"Cannot assign the value '{type_str}' to array '{name}' at index {index}. Expected type {array.type_name}, got {type(type_str).__name__}.", True, arg)
                return
        throw_error(f"Array '{name}' does not exist.", True, arg)
    
    def get_array(self, arg: str, run_object, throw_error) -> object:
        args = parse_args(arg)
        if len(args) == 2:
            name, index = args
            index = eval_value(index, run_object, throw_error)
            try:
                index = int(index)
            except ValueError:
                throw_error(f"Invalid index '{index}' for array '{name}'. Index must be an integer.", True, arg)
                return None
            for array in self.arrays:
                if array.name == name:
                    return array.get_value(index)
            throw_error(f"Array '{name}' does not exist.", True, arg)
        elif len(args) == 1:
            name = args[0]
            for array in self.arrays:
                if array.name == name:
                    return array.value
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid get syntax: {arg}", True, arg)
            return None
        return None
    
    def append_array(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 2:
            name, value = args
            value = eval_value(value, run_object, throw_error)
        else:
            throw_error(f"Invalid append syntax: {arg}", True, arg)
            return
        for array in self.arrays:
            if array.name == name:
                if not array.append_value(value, run_object, throw_error):
                    throw_error(f"Cannot append the value '{value}' to array '{name}'. Expected type {array.type_name}, got {type(value).__name__}.", True, arg)
                return
        throw_error(f"Array '{name}' does not exist.", True, arg)
    def append_many(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 2:
            name, value = args
            value = eval_value(value, run_object, throw_error)
        else:
            throw_error(f"Invalid append syntax: {arg}", True, arg)
            return
        for array in self.arrays:
            if array.name == name:
                if isinstance(value, list):
                    for val in value:
                        val = f"'{val}'" if isinstance(val, str) else val
                        if not array.append_value(val, run_object, throw_error):
                            throw_error(f"Cannot append the value '{val}' to array '{name}'. Expected type {array.type_name}, got {type(val).__name__}.", True, arg)
                else:
                    throw_error(f"Invalid appendmany syntax. Expected an array-like value.", True, arg)
                return
        throw_error(f"Array '{name}' does not exist.", True, arg)
    def delete_element(self, arg: str, run_object, throw_error) -> object:
        args = parse_args(arg)
        if len(args) == 2:
            name, index = args
            index = eval_value(index, run_object, throw_error)
            try:
                index = int(index)
            except ValueError:
                throw_error(f"Invalid index '{index}' for array '{name}'. Index must be an integer.", True, arg)
                return None
            for array in self.arrays:
                if array.name == name:
                    if not array.delete_value(index):
                        throw_error(f"Cannot delete index '{index}' of array '{name}'.")
                    return
            throw_error(f"Array '{name}' does not exist.", True, arg)
        elif len(args) == 1:
            name = args[0]
            for i, array in enumerate(self.arrays):
                if array.name == name:
                    del self.arrays[i]
                    return
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid get syntax: {arg}", True, arg)
            return None
        return None
    def length(self, arg: str, run_object, throw_error) -> int:
        args = parse_args(arg)
        if len(args) == 1:
            name = args[0]
            for array in self.arrays:
                if array.name == name:
                    return array.length()
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid length syntax: {arg}", True, arg)
            return -1
    def clear(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 1:
            name = args[0]
            for array in self.arrays:
                if array.name == name:
                    array.clear()
                    return
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid clear syntax: {arg}", True, arg)
            return None
    def contains(self, arg: str, run_object, throw_error) -> bool:
        args = parse_args(arg)
        if len(args) == 2:
            name, value = args
            value = eval_value(value, run_object, throw_error)
            for array in self.arrays:
                if array.name == name:
                    return array.contains(value, run_object, throw_error)
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid contains syntax: {arg}", True, arg)
            return False
    def sort(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 1:
            name = args[0]
            for array in self.arrays:
                if array.name == name:
                    array.sort()
                    return
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid sort syntax: {arg}", True, arg)
            return None
    def reverse(self, arg: str, run_object, throw_error) -> None:
        args = parse_args(arg)
        if len(args) == 1:
            name = args[0]
            for array in self.arrays:
                if array.name == name:
                    array.reverse()
                    return
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid reverse syntax: {arg}", True, arg)
            return None
    def index_of(self, arg: str, run_object, throw_error) -> int:
        args = parse_args(arg)
        if len(args) == 2:
            name, value = args
            value = eval_value(value, run_object, throw_error)
            for array in self.arrays:
                if array.name == name:
                    return array.index_of(value, run_object, throw_error)
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid indexof syntax: {arg}", True, arg)
            return -1
    def last_index_of(self, arg: str, run_object, throw_error) -> int:
        args = parse_args(arg)
        if len(args) == 2:
            name, value = args
            value = eval_value(value, run_object, throw_error)
            for array in self.arrays:
                if array.name == name:
                    return array.last_index_of(value, run_object, throw_error)
            throw_error(f"Array '{name}' does not exist.", True, arg)
        else:
            throw_error(f"Invalid lastindexof syntax: {arg}", True, arg)
            return -1
    
l = VarLib()
instructions: list[str] = ["declare[]", "set[]", "append[]", "get[]", "delete[]", "clear[]", "length[]", "contains[]", "sort[]", "reverse[]", "indexof[]", "lastindexof[]", "appendmany[]"]
variables: list[object] = [l.declare_array, l.set_array, l.append_array, l.get_array, l.delete_element, l.clear, l.length, l.contains, l.sort, l.reverse, l.index_of, l.last_index_of, l.append_many]
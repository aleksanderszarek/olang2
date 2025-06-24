'''
This module provides instructions for string manipulation such as concatenation, splitting, replacing, and checking if a string contains a substring.
- concat(str1, str2): Concatenates two strings.
- split(str, delimiter): Splits a string into a list of substrings based on the specified delimiter.
- replace(str, old, new): Replaces occurrences of a substring with another substring in the given string.
- contains(str, substring): Checks if the string contains the specified substring and returns a boolean value.
- find(str, substring): Finds the substring in the specified string and returns its starting index or -1.
- length(str): Returns the length of the string.
- startswith(str, substring): Checks if the string starts with the specified substring and returns a boolean value.
- endswith(str, substring): Checks if the string ends with the specified substring and returns a boolean value.
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
class String:
    def concat(self, args: str, run_object, throw_error) -> str:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = [eval_value(p.strip(), run_object, throw_error) for p in content]
        if len(parts) < 2:
            throw_error("concat requires at least two arguments.", True, args)
            return ""
        return "".join(str(part) for part in parts)
    def split(self, args: str, run_object, throw_error) -> list[str]:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = content
        if len(parts) != 2:
            throw_error("split requires exactly two arguments: the string and the delimiter.", True, args)
            return []
        try:
            string = str(eval_value(parts[0].strip(), run_object, throw_error))
            delimiter = str(eval_value(parts[1].strip(), run_object, throw_error))
        except Exception as e:
            throw_error(f"Invalid arguments for split", True, args)
            return []
        return string.split(str(delimiter))
    def replace(self, args: str, run_object, throw_error) -> str:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = content
        if len(parts) != 3:
            throw_error("replace requires exactly three arguments: the string, the old substring, and the new substring.", True, args)
            return ""
        try:
            string = str(eval_value(parts[0].strip(), run_object, throw_error))
            old_substring = str(eval_value(parts[1].strip(), run_object, throw_error))
            new_substring = str(eval_value(parts[2].strip(), run_object, throw_error))
        except Exception as e:
            throw_error(f"Invalid arguments for replace", True, args)
            return ""
        return string.replace(old_substring, new_substring)
    def contains(self, args: str, run_object, throw_error) -> bool:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = content
        if len(parts) != 2:
            throw_error("contains requires exactly two arguments: the string and the substring to check.", True, args)
            return False
        try:
            string = str(eval_value(parts[0].strip(), run_object, throw_error))
            substring = str(eval_value(parts[1].strip(), run_object, throw_error))
        except Exception as e:
            throw_error(f"Invalid arguments for contains", True, args)
            return False
        return substring in string
    def find(self, args: str, run_object, throw_error) -> int:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = content
        if len(parts) != 2:
            throw_error("find requires exactly two arguments: the string and the substring to check.", True, args)
            return False
        try:
            string = str(eval_value(parts[0].strip(), run_object, throw_error))
            substring = str(eval_value(parts[1].strip(), run_object, throw_error))
        except Exception as e:
            throw_error(f"Invalid arguments for find", True, args)
            return False
        return string.find(substring)
    def startswith(self, args: str, run_object, throw_error) -> bool:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = content
        if len(parts) != 2:
            throw_error("startswith requires exactly two arguments: the string and the substring to check.", True, args)
            return False
        try:
            string = str(eval_value(parts[0].strip(), run_object, throw_error))
            substring = str(eval_value(parts[1].strip(), run_object, throw_error))
        except Exception as e:
            throw_error(f"Invalid arguments for find", True, args)
            return False
        return string.startswith(substring)
    def endswith(self, args: str, run_object, throw_error) -> bool:
        content = args[args.index("(")+1:args.rindex(")")]
        content = split_args(content)
        parts = content
        if len(parts) != 2:
            throw_error("endswith requires exactly two arguments: the string and the substring to check.", True, args)
            return False
        try:
            string = str(eval_value(parts[0].strip(), run_object, throw_error))
            substring = str(eval_value(parts[1].strip(), run_object, throw_error))
        except Exception as e:
            throw_error(f"Invalid arguments for find", True, args)
            return False
        return string.endswith(substring)
    def length(self, args: str, run_object, throw_error) -> int:
        content = args[args.index("(")+1:args.rindex(")")]
        if (content.startswith('"') and content.endswith('"')) or (content.startswith("'") and content.endswith("'")):
            content = content[1:-1]
        else:
            try:
                content = run_object(content)
            except Exception:
                throw_error("Invalid argument for length, expected string.")
                return -1
        return len(content)
l = String()
instructions: list[str] = ["concat", "split", "replace", "contains", "length", "find", "startswith", "endswith"]
variables: list[object] = [l.concat, l.split, l.replace, l.contains, l.length, l.find, l.startswith, l.endswith]
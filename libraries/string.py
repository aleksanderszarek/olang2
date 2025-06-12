'''
This module provides instructions for string manipulation such as concatenation, splitting, replacing, and checking if a string contains a substring.
- concat(str1, str2): Concatenates two strings.
- split(str, delimiter): Splits a string into a list of substrings based on the specified delimiter.
- replace(str, old, new): Replaces occurrences of a substring with another substring in the given string.
- contains(str, substring): Checks if the string contains the specified substring and returns a boolean value.
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
    def find(self, args: str, run_object, throw_error) -> bool:
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
instructions: list[str] = ["concat", "split", "replace", "contains", "length", "find"]
variables: list[object] = [l.concat, l.split, l.replace, l.contains, l.length, l.find]
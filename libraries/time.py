'''
This module provides time-related functions such as random number generation, waiting, getting the current time, and date conversion.
Instructions:
- random(min, max): Returns a random integer between min and max.
- wait seconds: Pauses execution for the specified number of seconds.
- now(): Returns the current date and time in "YYYY-MM-DD HH:MM:SS" format.
- dconv(format, date): Converts a date string (YYYY-MM-DD HH:MM:SS) to a specified format (d, m, y, H, M, S).
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
class Time:
    def random(self, args: str, run_object, throw_error) -> int:
        content = args.strip()[args.find('(') + 1:args.rfind(')')].replace(" ", "")
        content = split_args(content)
        if len(content) != 2:
            throw_error("Invalid random function syntax. Expected two arguments: min and max.", True, args)
            return 0
        try:
            content[1] = int(content[1])
        except ValueError:
            try:
                content[1] = int(run_object(content[1]))
            except Exception as e:
                throw_error(f"Invalid min argument for random function", True, args)
                return 0
        try:
            content[0] = int(content[0])
        except ValueError:
            try:
                content[0] = int(run_object(content[0]))
            except Exception as e:
                throw_error(f"Invalid min argument for random function", True, args)
                return 0
        
        import random
        return random.randint(content[0], content[1])

    def wait(self, args: str, run_object, throw_error) -> None:
        content = args.strip()[args.find(' ') + 1:].replace(" ", "")
        import time
        time.sleep(eval_value(content, run_object, throw_error))
    def now(self, args: str, run_object, throw_error) -> str:
        import datetime
        if args.strip() != "now()":
            throw_error("The now function does not take any arguments.", True, args)
            return ""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def dconv(self, args: str, run_object, throw_error) -> str:
        content = args.strip()[args.find('(') + 1:args.rfind(')')]
        content = split_args(content)
        if len(content) != 2:
            throw_error("Invalid dconv function syntax. Expected dconv(format, date)", True, args)
            return ""
        format_str = content[0].strip().replace(" ", "")
        date_str = eval_value(content[1].strip(), run_object, throw_error)
        for _, i in enumerate(date_str):
            if not i == ' ':
                break
            date_str = date_str[1:]
        for _, i in enumerate(date_str[::-1]):
            if not i == ' ':
                date_str = date_str[:len(date_str) - _]
                break
        import datetime
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            throw_error(f"Invalid date format: {date_str}. Expected 'YYYY-MM-DD HH:MM:SS'.", True, args)
            return ""
        if format_str == "d":
            return str(date_obj.day)
        elif format_str == "m":
            return str(date_obj.month)
        elif format_str == "y":
            return str(date_obj.year)
        elif format_str == "H":
            return str(date_obj.hour)
        elif format_str == "M":
            return str(date_obj.minute)
        elif format_str == "S":
            return str(date_obj.second)
    
l = Time()
instructions: list[str] = ["random","wait", "now", "dconv"]
variables: list[object] = [l.random, l.wait, l.now, l.dconv]
    
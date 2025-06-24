'''
This module provides main functionality for running objects, printing strings to the screen or getting input values.
Instructions:
- exec(object_name, arg1, arg2, ...): Executes an object with the given name and arguments.
- write(arg1, arg2, ...): Prints the given arguments to the console.
- writeline(arg1, arg2, ...): Prints the given arguments to the console followed by a newline.
- read(): Reads input from the user and returns it as a string.
- if(condition) => instruction: Executes the instruction if the condition is true.
- while(condition) => instruction: Repeatedly executes the instruction as long as the condition is true.
- raise(message, fatal): Raises an error with the given message.
- end(): Ends the execution of the current script.
'''
import re, os
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
                if isinstance(name_value, int):
                    god_result = run_object(f'god({name_value})')
                else:
                    god_result = run_object(f'god("{name_value}")')
            except Exception as e:
                throw_error(f"Error resolving god(...): {e}", True, arg)
                return

            code = god_result["body"]
            parameters = god_result.get("args", [])

            if len(arguments) != len(parameters):
                throw_error(f"Function {name_value} expected {len(parameters)} args, got {len(arguments)}", True, arg)
                return

            for param_name, raw_arg in zip(parameters, arguments):
                evaluated = run_object(raw_arg)

                # Detect type for declaration
                if isinstance(evaluated, int):
                    param_type = "int"
                elif isinstance(evaluated, float):
                    param_type = "float"
                elif isinstance(evaluated, str):
                    param_type = "str"
                    evaluated = f'"{evaluated}"'
                elif isinstance(evaluated, bool):
                    param_type = "bool"
                    evaluated = "true" if evaluated else "false"
                else:
                    param_type = "object"
                    evaluated = str(evaluated)

                run_object(f"declare({param_name}, {param_type}, {evaluated})")

            for ins in code:
                run_object(ins)
            for param_name, raw_arg in zip(parameters, arguments):
                evaluated = run_object(raw_arg)
                run_object(f"delete({param_name})")
        except Exception as e:
            throw_error(f"Failed to execute exec: {e}", True, arg)

    def while_statement(self, arg: str, run_object, throw_error):
        while True:
            try:
                parts = arg.strip().split('=>', 1)
                if len(parts) != 2:
                    throw_error("Missing '=>' in while statement", True, arg)
                    return

                condition_str = parts[0].strip()
                instruction = parts[1].strip()
                if not condition_str.startswith("while(") or not condition_str.endswith(")"):
                    throw_error("Invalid while statement syntax", True, arg)
                    return
                condition_expr = condition_str[6:-1].strip()
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
                    run_object(instruction)
                else:
                    break

            except Exception as e:
                throw_error(f"Failed to execute while_statement: {e}", True, arg)
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
    def raise_error(self, arg: str, run_object, throw_error) -> None:
        parts = arg.strip().split(',')
        if len(parts) < 1 or len(parts) > 2:
            throw_error("raise(...) requires one or two arguments", True, arg)
            return

        message = parts[0].strip().strip('"').strip("'")
        fatal = parts[1].strip().lower() == "true" if len(parts) == 2 else False

        throw_error(message, fatal, arg)
    def end(self, arg: str, run_object, throw_error):
        if arg.strip() != "end()":
            throw_error("Invalid end function syntax. Expected 'end()'.", True, arg)
            return
        os._exit(0)
l = MainLib()
instructions: list[str] = ["exec","write","writeline","read", "if", "while", "raise", "end"]
variables: list[object] = [l.exec, l.write, l.writeline, l.read, l.if_statement, l.while_statement, l.raise_error, l.end]
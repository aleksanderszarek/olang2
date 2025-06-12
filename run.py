import json
import os
import importlib.util
from colorama import init as colorama_init
from colorama import Fore
from colorama import Style

colorama_init()
config = json.load(open('config.json', 'r', encoding='utf-8'))
defaultLibraries = config.get('includeLibraries', [])
returnOnFatal = config.get('returnOnFatal', True)
preprocessorDebug = config.get('preprocessorDebug', False)
generalLibraryLocation = config.get('generalLibraryLocation', False)
code = open('test.olang', 'r', encoding='utf-8').readlines()
code = filter(lambda x: x not in ['\n','\t',''], code)
code = filter(lambda x: x[0:1] != '//', code)
c = "".join(code)
code = c.replace('\n', '').replace('    ', '').replace("{",";{;").replace("}",";};").split(';')
vtypes = ["int", "float", "string", "bool", "char", "object"]
class Variable:
    def __init__(self, name: str, type: int, value: str):
        self.name = name
        self.type = type # 0 = int, 1 = float, 2 = string, 3 = bool, 4 = char, 5 = object
        self.value = value
    def __str__(self):
        return f"[{self.name} -> {vtypes[self.type]}]"
class Object:
    def __init__(self, type: int, args: list[str], body: list[str]):
        self.type = type # 0 = function, 1 = for loop, 2 = while loop, 3 = if statement
        self.args = args
        self.body = body
    def exec(self, args: list[Variable]):
        for instruction in self.body:
            if instruction.exec(args) != None:
                return instruction.exec(args)
        return None
    def __call__(self):
        ...
        
variables: list[Variable] = []
instructions: list[str] = []
objects: list[Object] = []
librariesVars: list[object] = []
def split_args(s: str) -> list[str]:
    args = []
    current = ""
    depth = 0
    in_str = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == '"' or c == "'":
            if in_str == c:
                in_str = False
            elif not in_str:
                in_str = c
            current += c
        elif c == "," and depth == 0 and not in_str:
            args.append(current.strip())
            current = ""
        else:
            if c == "(" and not in_str:
                depth += 1
            elif c == ")" and not in_str:
                depth -= 1
            current += c
        i += 1
    if current.strip():
        args.append(current.strip())
    return args

class Preprocessor:
    def __init__(self) -> None:
        ...
    def getlibraries(self, code: list[str]) -> list[str]:
        libraries = []
        for library in defaultLibraries:
            libraries.append(library)
        for i, line in enumerate(code):
            if line.startswith("//"):
                continue
            if line.startswith("$use"):
                lib = line.split(' ')[1].strip()
                code[i] = ""
                if lib not in libraries:
                    libraries.append(lib.replace(" ", ""))
            else:
                return libraries
    def getfunctions(self, code: list[str], starting_id: int) -> tuple[list[Object], list[str], int]:
        objects = []
        new_code = []
        nested_objs = []
        i = 0
        loop_id = starting_id

        while i < len(code):
            line = code[i]
            if line.startswith("function"):
                name = line.split(' ')[1].split('(')[0]
                args_str = line[line.find('(')+1 : line.rfind(')')]
                args = []

                if args_str:
                    for arg in split_args(args_str):
                        parts = arg.strip().split()
                        if len(parts) != 2:
                            raise Exception(f"Invalid function argument format: '{arg}'")
                        argtype_str, argname = parts
                        if argtype_str not in vtypes:
                            raise Exception(f"Invalid argument type: {argtype_str}")
                        argtype = vtypes.index(argtype_str)
                        args.append(Variable(argname, argtype, None))

                # Skip to opening brace
                while i < len(code) and code[i] != "{":
                    i += 1
                i += 1  # Skip the '{'

                # Extract body
                body = []
                depth = 1
                while i < len(code) and depth > 0:
                    current = code[i]
                    if current == "{":
                        depth += 1
                    elif current == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    else:
                        body.append(current)
                    i += 1

                # Handle nested loops inside the function
                nested_objs, processed_body, loop_id = self.getloops(body, loop_id)
                objects.extend(nested_objs)

                obj = Object(0, args, processed_body)
                objects.append(obj)
                variables.append(Variable(name, 5, obj))

                loop_id += 1
            else:
                new_code.append(line)
            i += 1

        return objects, new_code, loop_id


    def getloops(self, code: list[str], starting_id: int) -> tuple[list[Object], list[str], int]:
        objects = []
        new_code = []
        i = 0
        loop_id = starting_id

        while i < len(code):
            line = code[i]
            if line.startswith("for"):
                raw_args = line[line.find('(')+1 : line.rfind(')')].strip()
                parts = split_args(raw_args)
                if len(parts) != 3:
                    raise Exception("Invalid for loop syntax. Expected 3 parts: init, condition, step")

                init = parts[0]
                condition = parts[1]
                step = parts[2]

                # Skip to body
                while i < len(code) and code[i] != "{":
                    i += 1
                i += 1  # skip "{"

                # Extract loop body
                body = []
                depth = 1
                while i < len(code) and depth > 0:
                    current = code[i]
                    if current == "{":
                        depth += 1
                    elif current == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    else:
                        body.append(current)
                    i += 1

                loop_id += 1

                # Handle nested loops
                nested_objs, transformed_body, loop_id = self.getloops(body, loop_id)
                objects.extend(nested_objs)

                # Inject control structure
                transformed_body.insert(0, init)
                transformed_body.append(step)
                transformed_body.append(f"if({condition}) exec({loop_id})")

                obj = Object(1, [], transformed_body)
                objects.append(obj)
                variables.append(Variable("", 5, obj))

                new_code.append(f"exec({loop_id})")
            else:
                new_code.append(line)
            i += 1
        return objects, new_code, loop_id


def throw_error(message: str, fatality: bool, line: str):
    print(Fore.RED, Style.BRIGHT, f"\n\nInterpreter run into an error while running {line.split(" ")[0].split("(")[0]}!\n", Style.DIM, f"{message}", Fore.RESET, Style.RESET_ALL)
    if fatality and returnOnFatal:
        exit()
def run_object(line: str):
    if line.strip().startswith('god'):
        try:
            content = line.strip()[4:-1].strip()
            # Try by index
            if content.isdigit():
                idx = int(content) - 1
                if 0 <= idx < len(variables):
                    var = variables[idx]
                    if var.type == 5:  # object
                        return {
                            "name": var.name,
                            "type": "object",
                            "object_type": ["Function", "ForLoop", "WhileLoop", "IfStatement"][var.value.type],
                            "args": [str(a) for a in var.value.args],
                            "body": var.value.body
                        }
                    else:
                        return {
                            "name": var.name,
                            "type": vtypes[var.type],
                            "value": var.value
                        }
                else:
                    throw_error("Variable index out of range", True, line)

            # Try by variable name
            for var in variables:
                if var.name == content:
                    if var.type == 5:  # object
                        return {
                            "name": var.name,
                            "type": "object",
                            "object_type": ["Function", "ForLoop", "WhileLoop", "IfStatement"][var.value.type],
                            "args": [str(a) for a in var.value.args],
                            "body": var.value.body
                        }
                    else:
                        return {
                            "name": var.name,
                            "type": vtypes[var.type],
                            "value": var.value
                        }

            throw_error("Variable not found by name or index", True, line)

        except Exception as e:
            throw_error(f"Error resolving god(...): {e}", True, line)

    if "//" in line:
        line = line[:line.index("//")]
    try:
        return eval(line.strip())
    except Exception as e:
        ...
    try:
        return float(line.strip())
    except ValueError:
        ...
    if line.strip() == "":
        return
    for lib in librariesVars:
        try:
            insts = lib.instructions
            instsVars = lib.variables
            ins = line.strip().split('(')[0].split()[0]
        except Exception as e:
            throw_error(f"Failed to access library specification for {libraries[librariesVars.index(lib)]}", True, line)
            return
        if ins in insts:
            try:
                return instsVars[insts.index(ins)](line.strip(), run_object, throw_error)
            except Exception as e:
                throw_error(f"Unknown error while executing {ins}", True, line)
                return
    throw_error(f"Could not find instruction in current scope!", True, line)
def execute(code):
    pre = Preprocessor()

    function_objs, code, next_id = pre.getfunctions(code, 0)
    loop_objs, code, _ = pre.getloops(code, next_id)
    all_objects = function_objs + loop_objs
    if preprocessorDebug:
        print(Style.BRIGHT, "=== LIBRARIES ===", Style.RESET_ALL)
    global libraries
    libraries = pre.getlibraries(code)
    for i, lib in enumerate(libraries):
        try:
            if os.path.exists(os.path.join(os.getcwd(), generalLibraryLocation, (lib + ".py"))):
                lib_path = os.path.join(os.getcwd(), generalLibraryLocation, lib + ".py")
                spec = importlib.util.spec_from_file_location(lib, lib_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                librariesVars.append(mod)
                if preprocessorDebug:
                    print(f"[ID {i}] {lib}")
            else:
                if preprocessorDebug:
                    print(f"[ID {i}] {lib} (not found)")
        except Exception as e:
            throw_error(f"Failed to load library {lib}", True, lib)
    if preprocessorDebug:
        print(Style.BRIGHT, "\n=== OBJECTS ===", Style.RESET_ALL)
        for idx, obj in enumerate(all_objects):
            print(f"[ID {idx}] Type: {'Function' if obj.type == 0 else 'ForLoop'}")
            for instr in obj.body:
                print(f"  {instr}")
        print(Style.BRIGHT, "\n=== MAIN CODE ===", Style.RESET_ALL)
        for i, line in enumerate(code):
            print(line) if line.strip() != "" else ...

    global objects
    objects = all_objects
    print(Fore.YELLOW, Style.BRIGHT, "\nPreprocessing complete. Objects and main code are ready for execution.", Style.RESET_ALL, Fore.RESET)
    
    for line in code:
        run_object(line)
    print(Fore.GREEN, Style.BRIGHT, "\n\nInterpreter finished code execution with exit code 0", Style.RESET_ALL, Fore.RESET)
    
if __name__ == "__main__":
    execute(code)

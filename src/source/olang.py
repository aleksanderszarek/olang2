import json
import os, sys
import importlib.util
from colorama import init as colorama_init
from colorama import Fore, Style

colorama_init()

EXE_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
os.chdir(EXE_DIR)

filename = "local"
force_debug = False
force_ignore = False

args = sys.argv[1:]
for arg in args:
    if arg == "--debug":
        force_debug = True
    elif arg == "--ignore":
        force_ignore = True
    elif arg.endswith(".olang") and os.path.isfile(arg):
        filename = arg

try:
    config = json.load(open('config.json', 'r', encoding='utf-8'))
except FileNotFoundError:
    print(Fore.RED, Style.BRIGHT + "Missing config.json. Aborting." + Fore.RESET, Style.RESET_ALL)
    input("\nPress any key to exit...")
    os._exit(1)

defaultLibraries = config.get('includeLibraries', [])
returnOnFatal = not force_ignore and config.get('returnOnFatal', True)
preprocessorDebug = force_debug or config.get('preprocessorDebug', False)
generalLibraryLocation = config.get('generalLibraryLocation', '')
if filename == "local":
    print(Fore.RED + Style.BRIGHT + "No file specified, please use 'olang <filename>' instead!" + Fore.RESET + Style.RESET_ALL)
    os._exit(1)
try:
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.readlines()
except FileNotFoundError:
    print(Fore.RED + f"File not found: {filename}" + Fore.RESET)
    input("\nPress any key to exit...")
    sys.exit(1)

code = filter(lambda x: x not in ['\n','\t',''], code)
code = filter(lambda x: x[0:1] != '//', code)
c = "".join(code)
code = c.replace('\n', '').replace('    ', '').replace("{",";{;").replace("}",";};").split(';')

vtypes = ["int", "float", "string", "bool", "char", "object"]

class Object:
    def __init__(self, type: int, args: list[str], body: list[str], name: str = ""):
        self.type = type  # 0=function, 1=for
        self.args = args
        self.body = body
        self.name = name

   

    def __call__(self):
        ...

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
    def getlibraries(self, code: list[str]) -> list[str]:
        libraries = list(defaultLibraries)
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
        i = 0
        loop_id = starting_id

        while i < len(code):
            line = code[i]
            if line.startswith("function"):
                name = line.split(' ')[1].split('(')[0]
                args_str = line[line.find('(')+1 : line.rfind(')')]
                args = split_args(args_str) if args_str else []

                while i < len(code) and code[i] != "{":
                    i += 1
                i += 1
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

                nested_objs, processed_body, loop_id = self.getloops(body, loop_id, len(objects))
                objects.extend(nested_objs)
                obj = Object(0, args, processed_body, name)
                objects.append(obj)
            else:
                new_code.append(line)
            i += 1

        return objects, new_code, loop_id

    def getloops(self, code: list[str], starting_id: int, function_objects_len: int) -> tuple[list[Object], list[str], int]:
        objects = []
        new_code = []
        i = 0
        loop_id = starting_id

        while i < len(code):
            line = code[i]
            if line.startswith("for(") and ":" in line:
                loop_def = line[line.find('(')+1:line.rfind(')')]
                decl_part, cond_part, step = split_args(loop_def)

                var_decl = decl_part.strip()
                var_name, var_type = var_decl.split(":")
                var_name = var_name.strip()
                var_type = var_type.strip()
                if "=>|" in cond_part:
                    min_val, max_val = map(str.strip, cond_part.split("=>|"))
                    if min_val > max_val:
                        symb = ">"
                    else:
                        symb = "<"
                    condition = f"get({var_name}) {symb} {max_val}"
                elif "=>" in cond_part:
                    min_val, max_val = map(str.strip, cond_part.split("=>"))
                    if min_val > max_val:
                        symb = ">"
                    else:
                        symb = "<"
                    condition = f"get({var_name}) {symb}= {max_val}"
                else:
                    throw_error(f"Invalid for loop range syntax, expected '=>' or '=>|', got {cond_part}", True, line)
                step_instr = f"set({var_name}, {step.strip()})"
                init_instr = f"declare({var_name}, {var_type}, {min_val})"
                delete_instr = f"delete({var_name})"

                while i < len(code) and code[i] != "{":
                    i += 1
                i += 1
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
                nested_objs, transformed_body, loop_id = self.getloops(body, loop_id, function_objects_len)
                objects.extend(nested_objs)

                obj = Object(1, [], transformed_body + [step_instr], name=f"for_loop_{loop_id - 1}")
                objects.append(obj)
                new_code.append(init_instr)
                new_code.append(f"while({condition}) => exec({loop_id - 1 + function_objects_len})")
                new_code.append(delete_instr)
            else:
                new_code.append(line)
            i += 1

        return objects, new_code, loop_id

def throw_error(message: str, fatality: bool, line: str):
    print(Fore.YELLOW, Style.BRIGHT, f"\n\nInterpreter run into an error while running {line.split(' ')[0].split('(')[0]}!\n", Style.DIM, f"{message}", Fore.RESET, Style.RESET_ALL)
    if fatality and returnOnFatal:
        print(Fore.RED, Style.BRIGHT, "\nFatal error encountered. Interpreter finished code execution.", Style.RESET_ALL, "\nPress any key to exit...")
        input()
        os._exit(1)
def run_object(line: str):
    if line.strip().startswith('god'):
        try:
            content = line.strip()[4:-1].strip()
            if content.isdigit():
                idx = int(content)
                if 0 <= idx < len(objects):
                    obj = objects[idx]
                    return {
                        "name": obj.name,
                        "type": "object",
                        "object_type": ["Function", "ForLoop", "WhileLoop"][obj.type],
                        "args": obj.args,
                        "body": obj.body
                    }
                else:
                    throw_error("Object index out of range", True, line)
            for obj in objects:
                if obj.name == content[1:-1]:
                    return {
                        "name": obj.name,
                        "type": "object",
                        "object_type": ["Function", "ForLoop", "WhileLoop"][obj.type],
                        "args": obj.args,
                        "body": obj.body
                    }
            throw_error("Object not found by name or index", True, line)
        except Exception as e:
            throw_error(f"Error resolving god", True, line)
      
    if "//" in line:
        line = line[:line.index("//")]
    try:
        if "input" in line or "print" in line:
            throw_error("Could not find instruction in current scope!", True, line)
        return eval(line.strip())
    except:
        ...
    try:
        return float(line.strip())
    except:
        ...
    if line.strip() == "":
        return
    for lib in librariesVars:
        try:
            insts = lib.instructions
            instsVars = lib.variables
            ins = line.strip().split('(')[0].strip()
            
        except:
            throw_error(f"Failed to access library specification", True, line)
            return
        if ins in insts:
            try:
                return instsVars[insts.index(ins)](line, run_object, throw_error)
            except:
                throw_error(f"Unknown error while executing {ins}", True, line)
                return

    throw_error(f"Could not find instruction in current scope!", True, line)

def execute(code):
    pre = Preprocessor()
    function_objs, code, next_id = pre.getfunctions(code, 0)
    loop_objs, code, _ = pre.getloops(code, next_id, len(function_objs))
    all_objects = function_objs + loop_objs

    if preprocessorDebug:
        print(Style.BRIGHT, "=== LIBRARIES ===", Style.RESET_ALL)

    global libraries
    libraries = pre.getlibraries(code)
    for i, lib in enumerate(libraries):
        try:
            lib_path = os.path.join(os.getcwd(), generalLibraryLocation, lib + ".py")
            if os.path.exists(lib_path):
                spec = importlib.util.spec_from_file_location(lib, lib_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                librariesVars.append(mod)
                if preprocessorDebug:
                    print(f"[ID {i}] {lib}")
            else:
                if preprocessorDebug:
                    print(f"[ID {i}] {lib} (not found)")
        except:
            throw_error(f"Failed to load library {lib}", True, lib)

    if preprocessorDebug:
        print(Style.BRIGHT, "\n=== OBJECTS ===", Style.RESET_ALL)
        for idx, obj in enumerate(all_objects):
            print(f"[ID {idx}] {obj.name} Type: {'Function' if obj.type == 0 else 'ForLoop'}")
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
    print(Fore.GREEN, Style.BRIGHT, "\n\nInterpreter finished code execution with exit code 0", Style.RESET_ALL, Fore.RESET, "\nPress any key to exit...")
    input()
    os._exit(0)
if __name__ == "__main__":
    execute(code)

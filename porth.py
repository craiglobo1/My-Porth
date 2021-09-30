import sys
from enum import Enum,auto
import subprocess

class Intrinsic(Enum):
    PUSH = auto()
    ADD = auto()
    SUB = auto()
    DUMP = auto()

def push(x):
    return (Intrinsic.PUSH, x)

def add():
    return (Intrinsic.ADD,)

def sub():
    return (Intrinsic.SUB,)

def dump():
    return (Intrinsic.DUMP,)

def usage(program_name):
    print("Usage: %s [OPTIONS] <SUBCOMMAND> [ARGS]" % program_name)
    print("SUBCOMMAND:")
    print("   sim <file>  Simulate the program")
    print("   com <file>  Compile the program")

def callCmd(cmd):
    print(cmd)
    subprocess.call(cmd)


def simulate_program(program):
    stack =[]
    for op in program:
        assert len(Intrinsic) == 4, "Exhaustive handling of operations"
        if op[0] == Intrinsic.PUSH:
            stack.append(op[1])

        elif op[0] == Intrinsic.ADD:
            a = stack.pop()
            b = stack.pop()
            stack.append(a+b)

        elif op[0] == Intrinsic.SUB:
            a = stack.pop()
            b = stack.pop()
            stack.append(b-a)

        elif op[0] == Intrinsic.DUMP:
            print(stack[-1])

def find_col(line, start, predicate):
    while start < len(line) and predicate(line[start]):
        start += 1
    return start

def lex_line(line):
    col = find_col(line, 0, lambda x: x.isspace())
    while col < len(line):
        col_end = find_col(line, col, lambda x: not x.isspace())
        yield (col, line[col:col_end])
        col = find_col(line, col_end, lambda x: x.isspace())


def lex_file(file_path):
    with open(file_path, "r") as f:
        return [(file_path, row, col, token) 
                for (row, line) in enumerate(f.readlines())
                for (col, token) in lex_line(line)]

def load_program(program_name):

    def parseTokenAsOp(token):
        file_path, row, col, word = token 
        if word == "+":
            return add()
        elif word == "-":
            return sub()
        elif word == ".":
            return dump()
        else:
            try:
                return push(int(word))
            except ValueError as err:
                print(f"{file_path}:{row+1}:{col+1} {err}")
                exit(1)

    return [ parseTokenAsOp(token) for token in lex_file(program_name)]

def compile_program(program, outFilePath):
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)
        #add implementation of logic
        for op in program:
            assert len(Intrinsic) == 4, "Exhaustive handling of operations"
            if op[0] == Intrinsic.PUSH:
                wf.write(f"     ; -- push --\n")
                wf.write(f"      push {op[1]}\n")

            elif op[0] == Intrinsic.ADD:
                wf.write(f"     ; -- add --\n")
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      add eax, ebx\n")
                wf.write("      push eax\n")


            elif op[0] == Intrinsic.SUB:
                wf.write(f"     ; -- sub --\n")
                wf.write("      pop ebx\n")
                wf.write("      pop eax\n")
                wf.write("      sub eax, ebx\n")
                wf.write("      push eax\n")

            elif op[0] == Intrinsic.DUMP:
                wf.write(f"     ; -- dump --\n")
                wf.write("      pop eax\n")
                wf.write("      push eax\n")
                wf.write("      lea edi, decimalstr\n")
                wf.write("      call DUMP\n")
        
        with open("static\endAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)


    # assert False, "compiler not implemented"


def main():

    if len(sys.argv) < 2:
        usage(sys.argv[0])
        exit(1)
    if sys.argv[1] == "com" and len(sys.argv) < 3:
        usage(sys.argv[0])
        exit(1)

    program = load_program(sys.argv[2])
    programName = "main"

    if sys.argv[1] == "sim":
        simulate_program(program)
    
    if sys.argv[1] == "com":
        compile_program(program,f"{programName}.asm")
        callCmd(["ml", "/c", "/Zd", "/coff", f"{programName}.asm"])
        callCmd(["Link", "/SUBSYSTEM:CONSOLE", f"{programName}.obj"])
        callCmd([f"{programName}.exe"])
        


if __name__ == "__main__":
    main()
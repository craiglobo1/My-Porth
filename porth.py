import enum
import sys
from enum import Enum,auto
import subprocess

class Intrinsic(Enum):
    PUSH = auto()
    ADD = auto()
    SUB = auto()
    EQUAL = auto()
    DUMP = auto()
    IF = auto()
    ENDIF = auto()

def push(x):
    return (Intrinsic.PUSH, x)

def add():
    return (Intrinsic.ADD,)

def sub():
    return (Intrinsic.SUB,)

def equal():
    return (Intrinsic.EQUAL,)

def dump():
    return (Intrinsic.DUMP,)

def iff():
    return (Intrinsic.IF,)

def endif():
    return (Intrinsic.ENDIF,)

def usage(program_name):
    print("Usage: %s [OPTIONS] <SUBCOMMAND> [ARGS]" % program_name)
    print("SUBCOMMAND:")
    print("   sim <file>  Simulate the program")
    print("   com <file>  Compile the program")

def callCmd(cmd):
    cmdStr = " ".join(cmd)
    print(f"[CMD] {cmdStr}")
    subprocess.call(cmd)


def crossreference_blocks(program):
    stack = []
    for i, op in enumerate(program):
        assert len(Intrinsic) == 7 , "Exhaustive handling of ops in crossreference_blocks (not all ops handled only blocks)" 
        if op[0] == Intrinsic.IF:
            stack.append(i)
        elif op[0] == Intrinsic.ENDIF:
            if_i = stack.pop()
            assert program[if_i][0] == Intrinsic.IF, "End can only close blocks for now"
            program[if_i] = (Intrinsic.IF, i)
    return program
            

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
        assert len(Intrinsic) == 7, "Exhaustive handling of op in parseTokenAsOp"
        if word == "+":
            return add()
        elif word == "-":
            return sub()
        elif word == ".":
            return dump()
        elif word == "=":
            return equal()
        elif word  == "if":
            return iff()
        elif word == "endif":
            return endif()
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
            assert len(Intrinsic) == 7, "Exhaustive handling of operations whilst compiling"
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

            elif op[0] == Intrinsic.EQUAL:
                wf.write(f"     ; -- equal --\n")
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      .if eax == ebx\n")
                wf.write("          push 1\n")
                wf.write("      .else\n")
                wf.write("          push 0\n")
                wf.write("      .endif\n")

                # assert False, "Not implemented equals yet"

            elif op[0] == Intrinsic.DUMP:
                wf.write(f"     ; -- dump --\n")
                wf.write("      pop eax\n")
                wf.write("      push eax\n")
                wf.write("      lea edi, decimalstr\n")
                wf.write("      call DUMP\n")
            
            elif op[0] == Intrinsic.IF:
                wf.write(f" ; -- if --\n")
                wf.write("      pop eax\n")
                wf.write("      .if eax == 1\n")
            
            elif op[0] == Intrinsic.ENDIF:            
                wf.write("      .endif\n")
                wf.write(f" ; -- endif --\n")

        
        with open("static\endAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)


    # assert False, "compiler not implemented"

def simulate_program(program):
    stack = []
    i = 0
    while i < len(program):
        op = program[i]

        assert len(Intrinsic) == 7, "Exhaustive handling of operations whilst simulating"
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
        
        elif op[0] == Intrinsic.EQUAL:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a == b))

        elif op[0] == Intrinsic.IF:
            a = stack.pop()
            assert len(op) >= 2, "`if` does not have ref to endif of its block call crossreference_blocks"
            if a == 0:
                i = op[1]

        elif op[0] == Intrinsic.ENDIF:
            pass


        elif op[0] == Intrinsic.DUMP:
            print(stack[-1])

        i += 1


def main():

    if len(sys.argv) < 2:
        usage(sys.argv[0])
        exit(1)
    if sys.argv[1] == "com" and len(sys.argv) < 3:
        usage(sys.argv[0])
        exit(1)

    program = load_program(sys.argv[2])
    program = crossreference_blocks(program)
    programName = "main"

    if sys.argv[1] == "sim":
        simulate_program(program)
    
    if sys.argv[1] == "com":
        print(f"[INFO] Generating {programName}.asm")
        compile_program(program,f"{programName}.asm")
        callCmd(["ml", "/c", "/Zd", "/coff", f"{programName}.asm"])
        callCmd(["Link", "/SUBSYSTEM:CONSOLE", f"{programName}.obj"])
        callCmd([f"{programName}.exe"])
        


if __name__ == "__main__":
    main()
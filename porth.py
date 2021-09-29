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

def load_program(program_name):

    def parseAsOp(word):
        if word == "+":
            return add()
        elif word == "-":
            return sub()
        elif word == ".":
            return dump()
        elif word.isnumeric():
            return push(int(word))


    with open(program_name, "r") as rf:
        text = rf.read()
    
    text = text.split()
    program = [parseAsOp(op) for op in text]
    return program

def compile_program(program, outFilePath):
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)
        #add implementation of logic
        for op in program:
            assert len(Intrinsic) == 4, "Exhaustive handling of operations"
            if op[0] == Intrinsic.PUSH:
                wf.write(f"      push {op[1]}\n")

            elif op[0] == Intrinsic.ADD:
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      add eax, ebx\n")
                wf.write("      push eax\n")


            elif op[0] == Intrinsic.SUB:
                wf.write("      pop ebx\n")
                wf.write("      pop eax\n")
                wf.write("      sub eax, ebx\n")
                wf.write("      push eax\n")

            elif op[0] == Intrinsic.DUMP:
                wf.write(" pop eax\n")
                wf.write(" push eax\n")
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
    # program = [
    # push(20),
    # push(70),
    # sub(),
    # dump(),
    # push(10),
    # push(20),
    # add(),
    # add(),
    # dump()
    # ]
    if sys.argv[1] == "sim":
        simulate_program(program)
    
    if sys.argv[1] == "com":
        compile_program(program,"main.asm")
        callCmd(["ml", "/c", "/Zd", "/coff", "main.asm"])
        callCmd(["Link", "/SUBSYSTEM:CONSOLE", "main.obj"])
        callCmd(["main.exe"])
        


if __name__ == "__main__":
    main()
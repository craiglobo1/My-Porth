"""
Program is a list of Ops
Op is a dict with the follwing possible fields
- `type` -- The type of the Op. One of Intrinsic.ADD, Intrinsic.LT, Intrinsic.IF etc
- `loc` -- location of the Op in the program it contains (`file_name`,  `row`, `col`)
- `value` -- Only exists for Intrinsic.PUSH. Contains the value to be pushed to stack
- `jmp` -- It is an optional field and is used for code blocks like if,else, while, end etc. It is created in crossreference_blocks
"""


import sys
from enum import Enum,auto
import subprocess

class Intrinsic(Enum):
    PUSH = auto()
    ADD = auto()
    SUB = auto()
    EQUAL = auto()
    GT = auto()
    LT = auto()
    DUMP = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    END = auto()
    DUP = auto()
    MEM = auto()
    STORE = auto()
    LOAD = auto()
    PRINT = auto()

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
        assert len(Intrinsic) == 17 , "Exhaustive handling of ops in crossreference_blocks (not all ops handled only blocks)" 
        if op["type"] == Intrinsic.IF:
            stack.append(i)
        
        elif op["type"] == Intrinsic.ELSE:
            if_i = stack.pop()
            if program[if_i]["type"] != Intrinsic.IF:
                print("%s:%d:%d ERROR: `else` can only be used in `if`-blocks" % program[if_i]["loc"] )
                exit(1)

            program[if_i]["jmp"] = i
            stack.append(i)
        
        elif op["type"] == Intrinsic.END:
            block_i = stack.pop()
            if program[block_i]["type"] == Intrinsic.IF or program[block_i]["type"] == Intrinsic.ELSE:
                program[block_i]["jmp"] = i

            elif program[block_i]["type"] == Intrinsic.DO:
                program[block_i]["jmp"] = i
                block_i = stack.pop()

            else:
                assert False, "`end` can only close `if` blocks"

            if program[block_i]["type"] == Intrinsic.WHILE:
                program[i]["jmp"] = block_i

        elif op["type"] == Intrinsic.WHILE:
            stack.append(i)

        elif op["type"] == Intrinsic.DO:
            stack.append(i)
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
                for (col, token) in lex_line(line.split('//')[0])]

def load_program(program_name):

    def parseTokenAsOp(token):
        file_path, row, col, word = token
        row += 1
        col += 1
        assert len(Intrinsic) == 17, "Exhaustive handling of op in parseTokenAsOp"
        if word == "+":
            return {"type": Intrinsic.ADD, "loc" : (file_path, row, col)}
        elif word == "-":
            return {"type": Intrinsic.SUB, "loc" : (file_path, row, col)}
        elif word == "dump":
            return {"type": Intrinsic.DUMP, "loc" : (file_path, row, col)}
        elif word == "=":
            return {"type": Intrinsic.EQUAL, "loc" : (file_path, row, col)}
        elif word == ">":
            return {"type": Intrinsic.GT, "loc" : (file_path, row, col)}
        elif word == "<":
            return {"type": Intrinsic.LT, "loc" : (file_path, row, col)}
        elif word  == "if":
            return {"type": Intrinsic.IF, "loc" : (file_path, row, col)}
        elif word == "else":
            return {"type": Intrinsic.ELSE, "loc" : (file_path, row, col)}
        elif word == "while":
            return {"type": Intrinsic.WHILE, "loc" : (file_path, row, col)}
        elif word == "do":
            return {"type": Intrinsic.DO, "loc" : (file_path, row, col)}
        elif word == "end":
            return {"type": Intrinsic.END, "loc" : (file_path, row, col)}
        elif word == "dup":
            return {"type": Intrinsic.DUP, "loc" : (file_path, row, col)}
        elif word == "mem":
            return {"type": Intrinsic.MEM, "loc" : (file_path, row, col)}
        elif word == ".":
            return {"type": Intrinsic.STORE, "loc": (file_path, row, col)}
        elif word == ",":
            return {"type": Intrinsic.LOAD, "loc": (file_path, row, col)}
        elif word == "print":
            return {"type": Intrinsic.PRINT, "loc" : (file_path, row, col)}
        else:
            try:
                return {"type": Intrinsic.PUSH, "loc" : (file_path, row, col), "val" : int(word)}
            except ValueError as err:
                print(f"{file_path}:{row}:{col} {err}")
                exit(1)

    return [ parseTokenAsOp(token) for token in lex_file(program_name)]

def compile_program(program, outFilePath):
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)

        #add implementation of logic
        for i, op in enumerate(program):
            assert len(Intrinsic) == 17, "Exhaustive handling of operations whilst compiling"
            if op["type"] == Intrinsic.PUSH:
                valToPush = op["val"]
                wf.write(f"     ; -- push --\n")
                wf.write(f"      push {valToPush}\n")

            elif op["type"] == Intrinsic.ADD:
                wf.write(f"     ; -- add --\n")
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      add eax, ebx\n")
                wf.write("      push eax\n")


            elif op["type"] == Intrinsic.SUB:
                wf.write(f"     ; -- sub --\n")
                wf.write("      pop ebx\n")
                wf.write("      pop eax\n")
                wf.write("      sub eax, ebx\n")
                wf.write("      push eax\n")

            elif op["type"] == Intrinsic.EQUAL:
                wf.write(f"     ; -- equal --\n")
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      .if eax == ebx\n")
                wf.write("          push 1\n")
                wf.write("      .else\n")
                wf.write("          push 0\n")
                wf.write("      .endif\n")
            
            elif op["type"] == Intrinsic.GT:
                wf.write(f"     ; -- greater than --\n")
                wf.write("      pop ebx\n")
                wf.write("      pop eax\n")
                wf.write("      .if eax > ebx\n")
                wf.write("          push 1\n")
                wf.write("      .else\n")
                wf.write("          push 0\n")
                wf.write("      .endif\n")
                        
            elif op["type"] == Intrinsic.LT:
                wf.write(f"     ; -- less than --\n")
                wf.write("      pop ebx\n")
                wf.write("      pop eax\n")
                wf.write("      .if eax < ebx\n")
                wf.write("          push 1\n")
                wf.write("      .else\n")
                wf.write("          push 0\n")
                wf.write("      .endif\n")


            elif op["type"] == Intrinsic.DUMP:
                wf.write(f"      ; -- dump --\n")
                wf.write("      pop eax\n")
                wf.write("      lea edi, decimalstr\n")
                wf.write("      call DUMP\n")
            
            elif op["type"] == Intrinsic.IF:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                wf.write(f" ; -- if --\n")
                wf.write("      pop eax\n")
                wf.write("      push eax\n")
                wf.write("      .if eax == 1\n")
            
            elif op["type"] == Intrinsic.ELSE:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                wf.write(f" ; -- else --\n")
                wf.write("      .else\n")
            
            elif op["type"] == Intrinsic.WHILE:
                wf.write(f" ; -- while --\n")
                wf.write(f"     WHILE_{i}:\n")

            elif op["type"] == Intrinsic.DO:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                jmp_idx = op["jmp"]
                wf.write(f" ; -- do --\n")
                wf.write( "      pop eax\n")
                wf.write( "      cmp eax, 1\n")
                wf.write(f"      jne END_{jmp_idx}\n")
                
                
            elif op["type"] == Intrinsic.END:
                if "jmp" in op:
                    jmp_idx = op["jmp"]
                    wf.write(f"      jmp WHILE_{jmp_idx}\n")
                    wf.write(f"      END_{i}:\n")
                    wf.write(f" ; -- end while --\n")
                else:
                    wf.write("      .endif\n")
                    wf.write(f" ; -- end --\n")

            elif op["type"] == Intrinsic.DUP:
                wf.write("      ; -- duplicate --\n")
                wf.write("      pop eax\n")
                wf.write("      push eax\n")
                wf.write("      push eax\n")

            elif op["type"] == Intrinsic.MEM:
                wf.write("      ;-- mem --\n")
                wf.write("      lea edi, mem\n")
                wf.write("      push edi\n")
            
            elif op["type"] == Intrinsic.LOAD:
                wf.write("      ;-- load (,) --\n")
                wf.write("      pop eax\n")
                wf.write("      xor ebx, ebx\n")
                wf.write("      mov bl, [eax]\n")
                wf.write("      push ebx\n")

            elif op["type"] == Intrinsic.STORE:
                wf.write("      ;-- store (.) --\n")
                wf.write("      pop  eax\n")
                wf.write("      pop  ebx\n")
                wf.write("      mov  byte ptr [ebx], al\n")
            
            elif op["type"] == Intrinsic.PRINT:
                wf.write("      ;-- print --\n")
                wf.write("      pop eax\n")
                wf.write("      invoke StdOut, addr [eax]\n")
        
        with open("static\endAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)


    # assert False, "compiler not implemented"

def simulate_program(program):
    stack = []
    mem = bytearray(690_000)
    i = 0
    while i < len(program):
        op = program[i]

        assert len(Intrinsic) == 16, "Exhaustive handling of operations whilst simulating"
        if op["type"] == Intrinsic.PUSH:
            stack.append(op["val"])

        elif op["type"] == Intrinsic.ADD:
            a = stack.pop()
            b = stack.pop()
            stack.append(a+b)

        elif op["type"] == Intrinsic.SUB:
            a = stack.pop()
            b = stack.pop()
            stack.append(b-a)
        
        elif op["type"] == Intrinsic.EQUAL:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a == b))
        elif op["type"] == Intrinsic.GT:
            b = stack.pop()
            a = stack.pop()
            stack.append(int(a > b))

        elif op["type"] == Intrinsic.LT:
            b = stack.pop()
            a = stack.pop()
            stack.append(int(a < b))

        elif op["type"] == Intrinsic.IF:
            a = stack[-1]
            if "jmp" not in op:
                print("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program[i]["loc"])
                exit(1)
            if a == 0:
                i = op["jmp"]

        elif op["type"] == Intrinsic.ELSE:
            if "jmp" not in op:
                print("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program[i]["loc"])
                exit(1)

            i = op["jmp"]

        elif op["type"] == Intrinsic.DO:
            if "jmp" not in op:
                print("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program[i]["loc"])
                exit(1)

            a = stack.pop()
            if a == 0:
                i = op["jmp"]

        elif op["type"] == Intrinsic.END:
            if "jmp" in op:
                i = op["jmp"]

        elif op["type"] == Intrinsic.DUP:
            stack.append(stack[-1])

        elif op["type"] == Intrinsic.DUMP:
            a = stack.pop()
            print(a)
        elif op["type"] == Intrinsic.MEM:
            stack.append(0)

        elif op["type"] == Intrinsic.LOAD:
            addr = stack.pop()
            byte = mem[addr]
            stack.append(byte)
        
        elif op["type"] == Intrinsic.STORE:
            val = stack.pop()
            addr = stack.pop()
            mem[addr] = val & 0xFF

        i += 1
        print(mem[:10])


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
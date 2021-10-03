"""
Program is a list of Ops
Op is a dict with the follwing possible fields
- `type` -- The type of the Op. One of Intrinsic.ADD, Intrinsic.LT, Intrinsic.IF etc
- `loc` -- location of the Op in the program it contains (`file_name`,  `row`, `col`)
- `value` -- Only exists for Intrinsic.PUSH. Contains the value to be pushed to stack
- `jmp` -- It is an optional field and is used for code blocks like if,else, while, end etc. It is created in crossreference_blocks
"""
"""
Token is a dict with the follwing possible fields
- `type` -- The type of the Op. One of Token.INT, Token.WORD etc
- `loc` -- location of the Op in the program it contains (`file_name`,  `row`, `col`)
- `value` -- the value of the token depending on the type of the Token. For `str` it's Token.WORD and For `int` it's Token.INT
"""


import sys
from enum import Enum,auto
import subprocess

class Token(Enum):
    INT = auto()
    WORD = auto()

class Intrinsic(Enum):
    # arithmetic operations
    ADD = auto()
    SUB = auto()
    # logical operations
    EQUAL = auto()
    GT = auto()
    LT = auto()
    # blocks
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    END = auto()
    # stack operations
    PUSH = auto()
    DROP= auto()
    DUMP = auto()
    DUP = auto()
    DUP2=auto()
    OVER= auto()
    OVER2= auto()
    SWAP = auto()
    # mem operations
    MEM = auto()
    STORE = auto()
    LOAD = auto()
    PRINT = auto()
    # bitwise operations
    SHL= auto()
    SHR = auto()
    BAND = auto()
    BOR = auto()

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
        assert len(Intrinsic) == 26, "Exhaustive handling of ops in crossreference_blocks (not all ops handled only blocks)" 
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

def lex_word(wordOfToken):
    try:
        return (Token.INT, int(wordOfToken))
    except:
        return (Token.WORD, wordOfToken)


def lex_line(line):
    col = find_col(line, 0, lambda x: x.isspace())
    while col < len(line):
        col_end = find_col(line, col, lambda x: not x.isspace())
        yield (col, lex_word(line[col:col_end]))
        col = find_col(line, col_end, lambda x: x.isspace())


def lex_file(file_path):
    with open(file_path, "r") as f:
        return [{"type": tokenType, "loc": (file_path, row+1, col+1), "value" : tokenVal} 
                for (row, line) in enumerate(f.readlines())
                for (col, (tokenType, tokenVal)) in lex_line(line.split('//')[0])]


assert len(Intrinsic) == 26, "Exhaustive handling of op in parseTokenAsOp"
BUILTIN_WORDS = {
"+" : Intrinsic.ADD,
"-" : Intrinsic.SUB,
"dump" : Intrinsic.DUMP,
"=" : Intrinsic.EQUAL,
">" : Intrinsic.GT,
"<" : Intrinsic.LT,
"if" : Intrinsic.IF,
"else" : Intrinsic.ELSE,
"while" : Intrinsic.WHILE,
"do" : Intrinsic.DO,
"end" : Intrinsic.END,
"drop" : Intrinsic.DROP,
"dup" : Intrinsic.DUP,
"2dup" : Intrinsic.DUP2,
"swap" : Intrinsic.SWAP,
"over" : Intrinsic.OVER,
"2over" : Intrinsic.OVER2,
"mem" : Intrinsic.MEM,
"." : Intrinsic.STORE,
"," : Intrinsic.LOAD,
"print" : Intrinsic.PRINT,
"shl" : Intrinsic.SHL,
"shr" : Intrinsic.SHR,
"bor" : Intrinsic.BOR,
"band" : Intrinsic.BAND
}
def load_program(program_name):

    def parseTokenAsOp(token):
        if token["type"] == Token.WORD:
            if token["value"] in BUILTIN_WORDS:
                return {"type" : BUILTIN_WORDS[token["value"]], "loc" : token["loc"]}
            else:
                print("%s:%d:%d unknown word: %s" % (token["loc"] + (token["value"],)))
                exit(1)

        if token["type"] == Token.INT:
            return {"type" : Intrinsic.PUSH, "loc" : token["loc"], "value" : token["value"]}
        else:
            assert False, "unreachable"

    return [ parseTokenAsOp(token) for token in lex_file(program_name)]

def compile_program(program, outFilePath):
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)

        #add implementation of logic
        for i, op in enumerate(program):
            assert len(Intrinsic) == 26, "Exhaustive handling of operations whilst compiling"
            if op["type"] == Intrinsic.PUSH:
                valToPush = op["value"]
                wf.write(f"     ; -- push {valToPush} --\n")
                wf.write(f"      push {valToPush}\n")
            
            if op["type"] == Intrinsic.DROP:
                wf.write("      ; -- drop --\n")
                wf.write("      pop eax\n")

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
                wf.write(f"      pop eax\n")
                wf.write(f"      pop ebx\n")
                wf.write(f"      cmp eax, ebx\n")
                wf.write(f"      jne ZERO{i}\n")
                wf.write(f"      push 1\n")
                wf.write(f"      jmp END{i}\n")
                wf.write(f"      ZERO{i}:\n")
                wf.write(f"          push 0\n")
                wf.write(f"      END{i}:\n")
            
            elif op["type"] == Intrinsic.GT:
                wf.write(f"     ; -- greater than --\n")
                wf.write(f"      pop eax\n")
                wf.write(f"      pop ebx\n")
                wf.write(f"      cmp eax, ebx\n")
                wf.write(f"      jge ZERO{i}\n")
                wf.write(f"      push 1\n")
                wf.write(f"      jmp END{i}\n")
                wf.write(f"      ZERO{i}:\n")
                wf.write(f"          push 0\n")
                wf.write(f"      END{i}:\n")
                        
            elif op["type"] == Intrinsic.LT:
                wf.write(f"     ; -- less than --\n")
                wf.write(f"      pop eax\n")
                wf.write(f"      pop ebx\n")
                wf.write(f"      cmp eax, ebx\n")
                wf.write(f"      jle ZERO{i}\n")
                wf.write(f"      push 1\n")
                wf.write(f"      jmp END{i}\n")
                wf.write(f"      ZERO{i}:\n")
                wf.write(f"          push 0\n")
                wf.write(f"      END{i}:\n")

            elif op["type"] == Intrinsic.DUMP:
                wf.write(f"      ; -- dump --\n")
                wf.write("      pop eax\n")
                wf.write("      lea edi, decimalstr\n")
                wf.write("      call DUMP\n")
            
            elif op["type"] == Intrinsic.IF:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                jmpArg = op["jmp"]
                wf.write(f" ; -- if --\n")
                wf.write("      pop eax\n")
                wf.write("      cmp eax, 1\n")
                wf.write(f"      jne NEXT{jmpArg}\n")
            
            elif op["type"] == Intrinsic.ELSE:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                jmpArg = op["jmp"]
                wf.write(f" ; -- else --\n")
                wf.write(f"      jmp NEXT{jmpArg}\n")
                wf.write(f"      NEXT{i}:\n")
            
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
                    wf.write(f"      NEXT{i}:\n")
                    wf.write(f" ; -- end --\n")

            elif op["type"] == Intrinsic.DUP:
                wf.write("      ; -- duplicate --\n")
                wf.write("      pop eax\n")
                wf.write("      push eax\n")
                wf.write("      push eax\n")

            elif op["type"] == Intrinsic.DUP2:
                wf.write("      ; -- duplicate --\n")
                wf.write("      pop  eax\n")
                wf.write("      pop  ebx\n")
                wf.write("      push ebx\n")
                wf.write("      push eax\n")
                wf.write("      push ebx\n")
                wf.write("      push eax\n")
            
            elif op["type"] == Intrinsic.OVER:
                wf.write("      ; -- duplicate --\n")
                wf.write("      pop  eax\n")
                wf.write("      pop  ebx\n")
                wf.write("      push ebx\n")
                wf.write("      push eax\n")
                wf.write("      push ebx\n")

            elif op["type"] == Intrinsic.OVER2:
                wf.write("      ; -- duplicate --\n")
                wf.write("      pop  eax\n")
                wf.write("      pop  ebx\n")
                wf.write("      pop  ecx\n")
                wf.write("      push ecx\n")
                wf.write("      push ebx\n")
                wf.write("      push eax\n")
                wf.write("      push ecx\n")

            elif op["type"] == Intrinsic.SWAP:
                wf.write("      ; -- duplicate --\n")
                wf.write("      pop  eax\n")
                wf.write("      pop  ebx\n")
                wf.write("      push eax\n")
                wf.write("      push ebx\n")


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

            elif op["type"] == Intrinsic.SHL:
                wf.write("      ;-- shl --\n")
                wf.write("      pop ecx\n")
                wf.write("      pop ebx\n")
                wf.write("      shl ebx, cl\n")
                wf.write("      push ebx\n")
                

            elif op["type"] == Intrinsic.SHR:
                wf.write("      ;-- shr --\n")
                wf.write("      pop ecx\n")
                wf.write("      pop ebx\n")
                wf.write("      shr ebx, cl\n")
                wf.write("      push ebx\n")

            elif op["type"] == Intrinsic.BOR:
                wf.write("      ;-- bor --\n")
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      or ebx, eax\n")
                wf.write("      push  ebx\n")

            elif op["type"] == Intrinsic.BAND:
                wf.write("      ;-- bor --\n")
                wf.write("      pop eax\n")
                wf.write("      pop ebx\n")
                wf.write("      and ebx, eax\n")
                wf.write("      push  ebx\n")
            
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

        assert len(Intrinsic) == 26, "Exhaustive handling of operations whilst simulating"
        if op["type"] == Intrinsic.PUSH:
            stack.append(op["value"])
        
        if op["type"] == Intrinsic.DROP:
            stack.pop()

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
            a = stack.pop()
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
        
        elif op["type"] == Intrinsic.DUP2:
            a = stack.pop()
            b = stack.pop()

            stack.append(b)
            stack.append(a)
            stack.append(b)
            stack.append(a)
        
        elif op["type"] == Intrinsic.OVER:
            a = stack.pop()
            b = stack.pop()
            stack.append(b)
            stack.append(a)
            stack.append(b)

        elif op["type"] == Intrinsic.OVER2:
            a = stack.pop()
            b = stack.pop()
            c = stack.pop()
            stack.append(c)
            stack.append(b)
            stack.append(a)
            stack.append(c)

        elif op["type"] == Intrinsic.SWAP:
            a = stack.pop()
            b = stack.pop()
            stack.append(a)
            stack.append(b)

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
        
        elif op["type"] == Intrinsic.PRINT:
            addr = stack.pop()
            while mem[addr] != 0:
                print(chr(mem[addr]), end='')
                addr += 1

        elif op["type"] == Intrinsic.SHL:
            shiftAmt = stack.pop()
            val = stack.pop()
            stack.append(val << shiftAmt)
            

        elif op["type"] == Intrinsic.SHR:
            shiftAmt = stack.pop()
            val = stack.pop()
            stack.append(val >> shiftAmt)

        elif op["type"] == Intrinsic.BOR:
            a= stack.pop()
            b = stack.pop()
            stack.append(a | b)

        elif op["type"] == Intrinsic.BAND:
            a= stack.pop()
            b = stack.pop()
            stack.append(a & b)
        # print(op["type"], stack, mem[:31])
        # input()
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
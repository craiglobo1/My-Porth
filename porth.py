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
    STR = auto()

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
    PUSH_INT = auto()
    PUSH_STR = auto()
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
        assert len(Intrinsic) == 27, "Exhaustive handling of ops in crossreference_blocks (not all ops handled only blocks)" 
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
        if line[col] == '"':
            col_end = find_col(line, col+1, lambda x: not x == '"')
            wordOfToken = line[col+1:col_end]
            assert line[col_end] == '"', "string literal not closed"
            yield (col, (Token.STR, bytes(wordOfToken, "utf-8").decode("unicode-escape")))
            col = find_col(line, col_end+1, lambda x: x.isspace())
        else:
            col_end = find_col(line, col, lambda x: not x.isspace())
            wordOfToken = line[col:col_end]
            try:
                yield (col,(Token.INT, int(wordOfToken)))
            except:
                yield (col,(Token.WORD, wordOfToken))
            col = find_col(line, col_end, lambda x: x.isspace())


def lex_file(file_path):
    with open(file_path, "r") as f:
        return [{"type": tokenType, "loc": (file_path, row+1, col+1), "value" : tokenVal} 
                for (row, line) in enumerate(f.readlines())
                for (col, (tokenType, tokenVal)) in lex_line(line.split('//')[0])]


assert len(Intrinsic) == 27, "Exhaustive handling in BUILTIN WORDS"
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
        assert len(Token) == 3, "Exhaustive handling of Tokens"
        if token["type"] == Token.WORD:
            if token["value"] in BUILTIN_WORDS:
                return {"type" : BUILTIN_WORDS[token["value"]], "loc" : token["loc"]}
            else:
                print("%s:%d:%d unknown word: %s" % (token["loc"] + (token["value"],)))
                exit(1)

        if token["type"] == Token.INT:
            return {"type" : Intrinsic.PUSH_INT, "loc" : token["loc"], "value" : token["value"]}
        if token["type"] == Token.STR:
            return {"type" : Intrinsic.PUSH_STR, "loc" : token["loc"], "value" : token["value"]}

        else:
            assert False, "unreachable"

    return [ parseTokenAsOp(token) for token in lex_file(program_name)]

def compile_program(program, outFilePath):
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)
        lt = []
        strs = []
        #add implementation of logic
        for i, op in enumerate(program):
            assert len(Intrinsic) == 27, "Exhaustive handling of operations whilst compiling"
            if op["type"] == Intrinsic.PUSH_INT:
                valToPush = op["value"]
                lt.append(f"     ; -- push int {valToPush} --\n")
                lt.append(f"      push {valToPush}\n")
            
            if op["type"] == Intrinsic.PUSH_STR:
                valToPush = op["value"]
                lt.append(f"      lea edi, str_{len(strs)}\n")
                lt.append(f"      push edi\n")
                strs.append(valToPush)
                # assert False, "Not Implemented yet"
            
            if op["type"] == Intrinsic.DROP:
                lt.append("      ; -- drop --\n")
                lt.append("      pop eax\n")

            elif op["type"] == Intrinsic.ADD:
                lt.append(f"     ; -- add --\n")
                lt.append("      pop eax\n")
                lt.append("      pop ebx\n")
                lt.append("      add eax, ebx\n")
                lt.append("      push eax\n")


            elif op["type"] == Intrinsic.SUB:
                lt.append(f"     ; -- sub --\n")
                lt.append("      pop ebx\n")
                lt.append("      pop eax\n")
                lt.append("      sub eax, ebx\n")
                lt.append("      push eax\n")

            elif op["type"] == Intrinsic.EQUAL:
                lt.append(f"     ; -- equal --\n")
                lt.append(f"      pop eax\n")
                lt.append(f"      pop ebx\n")
                lt.append(f"      cmp eax, ebx\n")
                lt.append(f"      jne ZERO{i}\n")
                lt.append(f"      push 1\n")
                lt.append(f"      jmp END{i}\n")
                lt.append(f"      ZERO{i}:\n")
                lt.append(f"          push 0\n")
                lt.append(f"      END{i}:\n")
            
            elif op["type"] == Intrinsic.GT:
                lt.append(f"     ; -- greater than --\n")
                lt.append(f"      pop eax\n")
                lt.append(f"      pop ebx\n")
                lt.append(f"      cmp eax, ebx\n")
                lt.append(f"      jge ZERO{i}\n")
                lt.append(f"      push 1\n")
                lt.append(f"      jmp END{i}\n")
                lt.append(f"      ZERO{i}:\n")
                lt.append(f"          push 0\n")
                lt.append(f"      END{i}:\n")
                        
            elif op["type"] == Intrinsic.LT:
                lt.append(f"     ; -- less than --\n")
                lt.append(f"      pop eax\n")
                lt.append(f"      pop ebx\n")
                lt.append(f"      cmp eax, ebx\n")
                lt.append(f"      jle ZERO{i}\n")
                lt.append(f"      push 1\n")
                lt.append(f"      jmp END{i}\n")
                lt.append(f"      ZERO{i}:\n")
                lt.append(f"          push 0\n")
                lt.append(f"      END{i}:\n")

            elif op["type"] == Intrinsic.DUMP:
                lt.append(f"      ; -- dump --\n")
                lt.append("      pop eax\n")
                lt.append("      lea edi, decimalstr\n")
                lt.append("      call DUMP\n")
            
            elif op["type"] == Intrinsic.IF:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                jmpArg = op["jmp"]
                lt.append(f" ; -- if --\n")
                lt.append("      pop eax\n")
                lt.append("      cmp eax, 1\n")
                lt.append(f"      jne NEXT{jmpArg}\n")
            
            elif op["type"] == Intrinsic.ELSE:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                jmpArg = op["jmp"]
                lt.append(f" ; -- else --\n")
                lt.append(f"      jmp NEXT{jmpArg}\n")
                lt.append(f"      NEXT{i}:\n")
            
            elif op["type"] == Intrinsic.WHILE:
                lt.append(f" ; -- while --\n")
                lt.append(f"     WHILE_{i}:\n")

            elif op["type"] == Intrinsic.DO:
                if "jmp" not in op:
                    print("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program[i]["loc"])
                    exit(1)
                jmp_idx = op["jmp"]
                lt.append(f" ; -- do --\n")
                lt.append( "      pop eax\n")
                lt.append( "      cmp eax, 1\n")
                lt.append(f"      jne END_{jmp_idx}\n")
                
                
            elif op["type"] == Intrinsic.END:
                if "jmp" in op:
                    jmp_idx = op["jmp"]
                    lt.append(f"      jmp WHILE_{jmp_idx}\n")
                    lt.append(f"      END_{i}:\n")
                    lt.append(f" ; -- end while --\n")
                else:
                    lt.append(f"      NEXT{i}:\n")
                    lt.append(f" ; -- end --\n")

            elif op["type"] == Intrinsic.DUP:
                lt.append("      ; -- duplicate --\n")
                lt.append("      pop eax\n")
                lt.append("      push eax\n")
                lt.append("      push eax\n")

            elif op["type"] == Intrinsic.DUP2:
                lt.append("      ; -- duplicate --\n")
                lt.append("      pop  eax\n")
                lt.append("      pop  ebx\n")
                lt.append("      push ebx\n")
                lt.append("      push eax\n")
                lt.append("      push ebx\n")
                lt.append("      push eax\n")
            
            elif op["type"] == Intrinsic.OVER:
                lt.append("      ; -- duplicate --\n")
                lt.append("      pop  eax\n")
                lt.append("      pop  ebx\n")
                lt.append("      push ebx\n")
                lt.append("      push eax\n")
                lt.append("      push ebx\n")

            elif op["type"] == Intrinsic.OVER2:
                lt.append("      ; -- duplicate --\n")
                lt.append("      pop  eax\n")
                lt.append("      pop  ebx\n")
                lt.append("      pop  ecx\n")
                lt.append("      push ecx\n")
                lt.append("      push ebx\n")
                lt.append("      push eax\n")
                lt.append("      push ecx\n")

            elif op["type"] == Intrinsic.SWAP:
                lt.append("      ; -- duplicate --\n")
                lt.append("      pop  eax\n")
                lt.append("      pop  ebx\n")
                lt.append("      push eax\n")
                lt.append("      push ebx\n")


            elif op["type"] == Intrinsic.MEM:
                lt.append("      ;-- mem --\n")
                lt.append("      lea edi, mem\n")
                lt.append("      push edi\n")
            
            elif op["type"] == Intrinsic.LOAD:
                lt.append("      ;-- load (,) --\n")
                lt.append("      pop eax\n")
                lt.append("      xor ebx, ebx\n")
                lt.append("      mov bl, [eax]\n")
                lt.append("      push ebx\n")

            elif op["type"] == Intrinsic.STORE:
                lt.append("      ;-- store (.) --\n")
                lt.append("      pop  eax\n")
                lt.append("      pop  ebx\n")
                lt.append("      mov  byte ptr [ebx], al\n")
            
            elif op["type"] == Intrinsic.PRINT:
                lt.append("      ;-- print --\n")
                lt.append("      pop eax\n")
                lt.append("      invoke StdOut, addr [eax]\n")

            elif op["type"] == Intrinsic.SHL:
                lt.append("      ;-- shl --\n")
                lt.append("      pop ecx\n")
                lt.append("      pop ebx\n")
                lt.append("      shl ebx, cl\n")
                lt.append("      push ebx\n")
                

            elif op["type"] == Intrinsic.SHR:
                lt.append("      ;-- shr --\n")
                lt.append("      pop ecx\n")
                lt.append("      pop ebx\n")
                lt.append("      shr ebx, cl\n")
                lt.append("      push ebx\n")

            elif op["type"] == Intrinsic.BOR:
                lt.append("      ;-- bor --\n")
                lt.append("      pop eax\n")
                lt.append("      pop ebx\n")
                lt.append("      or ebx, eax\n")
                lt.append("      push  ebx\n")

            elif op["type"] == Intrinsic.BAND:
                lt.append("      ;-- bor --\n")
                lt.append("      pop eax\n")
                lt.append("      pop ebx\n")
                lt.append("      and ebx, eax\n")
                lt.append("      push  ebx\n")

        wf.write(".data\n")
        wf.write("    decimalstr db 16 DUP (0)  ; address to store dump values\n")
        wf.write("    aSymb db 97, 0\n")
        wf.write("    negativeSign db \"-\", 0    ; negativeSign     \n")
        wf.write("    nl DWORD 10               ; new line character in ascii\n")
        for i,s in enumerate(strs):
            sAsNum = ", ".join(map(str,list(bytes(s,"utf-8"))))
            wf.write(f"    str_{i} db {sAsNum}, 0 \n")
        wf.write(".data?\n")
        wf.write("    mem db ?\n")
        wf.write(".code\n")
        wf.write("    start PROC\n")

        wf.write("".join(lt))    
        with open("static\endAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)


    # assert False, "compiler not implemented"
MEM_CAPACITY = 690_000
STR_CAPACITY = 690_000
def simulate_program(program):
    stack = []
    mem = bytearray(MEM_CAPACITY + STR_CAPACITY)
    strPtr = STR_CAPACITY
    i = 0
    while i < len(program):
        op = program[i]

        assert len(Intrinsic) == 27, "Exhaustive handling of operations whilst simulating"
        if op["type"] == Intrinsic.PUSH_INT:
            stack.append(op["value"])
        
        if op["type"] == Intrinsic.PUSH_STR:
            bs = bytes(op["value"], "utf-8")
            n = len(bs)
            if "addr" not in op:
                op["addr"] = strPtr
                mem[strPtr:strPtr+n] = bs
                strPtr += n
                assert strPtr <= STR_CAPACITY+MEM_CAPACITY, "String Buffer Overflow"
            stack.append(op["addr"])
        
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
            addrStr = addr
            while mem[addr] != 0:
                print(chr(mem[addr]), end='')
                addr += 1
            # print(addrStr, mem[addrStr:addrStr+20])

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
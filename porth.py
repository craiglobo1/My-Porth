import sys
from enum import Enum,auto
import subprocess
from os import path, getcwd
from collections import deque
import time
from copy import copy


EXPANSION_LIMIT = 1000

class Token(Enum):
    INT = auto()
    WORD = auto()
    STR = auto()
    CHAR = auto()
    KEYWORD = auto()

class Keyword(Enum):
    # blocks
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    MACRO = auto()
    INCLUDE = auto()
    SYSCALL = auto()
    SYSVAL = auto()
    END = auto()

class Intrinsic(Enum):
    # win32 api operations
    STDOUT = auto()
    # FOPEN = auto()
    # FWRITE = auto()
    # FREAD = auto()
    # FCLOSE = auto()
    EXIT = auto()
    # arithmetic operations
    ADD = auto()
    SUB = auto()
    DIVMOD = auto()
    MUL = auto()
    # logical operations
    EQUAL = auto()
    NE = auto()
    GT = auto()
    LT = auto()
    # stack operations
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
    STORE32 = auto()
    LOAD32 = auto()
    # bitwise operations
    SHL= auto()
    SHR = auto()
    BAND = auto()
    BOR = auto()

class OP(Enum):
    # stack operations
    PUSH_INT = auto()
    PUSH_STR = auto()
    # syscall
    SYSCALL = auto()
    SYSVAL = auto()
    # blocks
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    END = auto()
    INTRINSIC = auto()

assert len(Keyword) == 9, f"Exhaustive handling in KEYWORD NAMES {len(Keyword)}"
KEYWORD_NAMES = {
"if"    :   Keyword.IF,
"else"  :   Keyword.ELSE,
"while" :   Keyword.WHILE,
"do"    :   Keyword.DO,
"macro" :   Keyword.MACRO,
"include":  Keyword.INCLUDE,
"syscall":  Keyword.SYSCALL,
"sysval":  Keyword.SYSVAL,
"end"   :   Keyword.END,
}

assert len(Intrinsic) == 26 , f"Exhaustive handling in INTRINSIC_WORDS {len(Intrinsic)}"
INTRINSIC_WORDS = {
"stdout" : Intrinsic.STDOUT,
"exit"  : Intrinsic.EXIT,
"+"     : Intrinsic.ADD,
"-"     : Intrinsic.SUB,
"divmod": Intrinsic.DIVMOD,
"*"     : Intrinsic.MUL,
"dump"  : Intrinsic.DUMP,
"="     : Intrinsic.EQUAL,
"!="    : Intrinsic.NE,
">"     : Intrinsic.GT,
"<"     : Intrinsic.LT,
"drop"  : Intrinsic.DROP,
"dup"   : Intrinsic.DUP,
"2dup"  : Intrinsic.DUP2,
"swap"  : Intrinsic.SWAP,
"over"  : Intrinsic.OVER,
"2over" : Intrinsic.OVER2,
"mem"   : Intrinsic.MEM,
"."     : Intrinsic.STORE,
","     : Intrinsic.LOAD,
"store32":Intrinsic.STORE32,
"load32": Intrinsic.LOAD32,
"shl"   : Intrinsic.SHL,
"shr"   : Intrinsic.SHR,
"bor"   : Intrinsic.BOR,
"band"  : Intrinsic.BAND
}



def find_col(line, start, predicate):
    while start < len(line) and predicate(line[start]):
        start += 1
    return start

def lex_line(file_path, row, line):
    col = find_col(line, 0, lambda x: x.isspace())
    assert len(Token) == 5, "Exahuastive handling of tokens in lex_line"
    while col < len(line):
        loc = (file_path, row + 1, col + 1)

        if line[col] == '"':
            col_end = find_col(line, col+1, lambda x: not x == '"')
            if col_end >= len(line) or line[col_end] != '"':
                print("%s:%d:%d error: string literal not closed" % loc )
            wordOfToken = line[col+1:col_end]
            yield (col, (Token.STR, bytes(wordOfToken, "utf-8").decode("unicode-escape")))
            col = find_col(line, col_end+1, lambda x: x.isspace())

        elif line[col] == "'":
            col_end = find_col(line, col+1, lambda x: not x == "'")
            if col_end >= len(line) or line[col_end] != "'":
                print("%s:%d:%d error: string literal not closed" % loc )
            wordOfToken = line[col+1:col_end]
            yield (col, (Token.CHAR, bytes(wordOfToken, "utf-8").decode("unicode-escape")))
            col = find_col(line, col_end+1, lambda x: x.isspace())

        else:
            col_end = find_col(line, col, lambda x: not x.isspace())
            wordOfToken = line[col:col_end]
            try:
                yield (col,(Token.INT, int(wordOfToken)))
            except:
                if wordOfToken in KEYWORD_NAMES:
                    yield (col, (Token.KEYWORD, KEYWORD_NAMES[wordOfToken]))
                else:
                    yield (col,(Token.WORD, wordOfToken))
            col = find_col(line, col_end, lambda x: x.isspace())

"""
Token is a dict with the follwing possible fields
- `type` -- The type of the OP. One of Token.INT, Token.WORD etc
- `loc` -- location of the OP in the program it contains (`file_token`,  `row`, `col`)
- `value` -- the value of the token depending on the type of the Token. For `str` it's Token.WORD and For `int` it's Token.INT
- `expanded` -- the counter for the number of tokens expanded from OP.MACRO and OP.INCLUDE
"""


def lex_file(file_path):
    with open(file_path, "r") as f:
        return [{"type": token, "loc": (file_path, row+1, col+1), "value" : tokenVal} 
                for (row, line) in enumerate(f.readlines())
                for (col, (token, tokenVal)) in lex_line(file_path, row, line.split('//')[0],)]

def expandMacro(token):
    if "expanded" not in token:
        token["expanded"] = 0
    token["expanded"] += 1
    return token

"""
Macro is a Dictionary
"macrotoken" -> (loc, tokens)
"""
def compile_tokens_to_program(tokens,includePaths=[]):
    human = lambda x: str(x).split(".")[-1].lower()
    stack = []
    program = []
    rtokens = list(reversed(tokens))
    macros = {}
    ip = 0;
    while len(rtokens) > 0:
        # TODO: some sort of safety mechanism for recursive macros
        token = rtokens.pop()
        op = {}
        assert len(Token) == 5, "Exhaustive token handling in compile_tokens_to_program"
        if token["type"] == Token.WORD:
            assert isinstance(token["value"], str), "This could be a bug in the lexer"
            if token["value"] in INTRINSIC_WORDS:
                op["type"]= OP.INTRINSIC
                op["value"]= INTRINSIC_WORDS[token["value"]]
                op["loc"] = token["loc"]
                program.append(op)
                ip += 1
            elif token["value"] in macros:
                mtk =  map(expandMacro, reversed(macros[token["value"]]["tokens"]))
                mtk = list(mtk)

                if len(list(mtk)) == 0:
                    sys.exit("%s:%d:%d: error: macro is empty" %  token["loc"])

                if len(list(mtk)) != 0:
                    rtokens += mtk

                    if EXPANSION_LIMIT < rtokens[-1]["expanded"]:
                        sys.exit("%s:%d:%d: error: macro exansion limit of %d exceeded" %  (token["loc"] + (EXPANSION_LIMIT, )))
                    continue
            else:
                sys.exit("%s:%d:%d: unknown word `%s`" % (token["loc"] + (token["value"], )))
            

        elif token["type"] == Token.INT:
            op["type"]= OP.PUSH_INT
            op["value"] = token["value"]
            op["loc"] = token["loc"]
            program.append(op)
            ip += 1

        elif token["type"] == Token.STR:
            op["type"]= OP.PUSH_STR
            op["value"] = token["value"]
            op["loc"] = token["loc"]
            program.append(op)
            ip += 1

        elif token["type"] == Token.CHAR:
            op["type"]= OP.PUSH_INT
            op["value"] = ord(token["value"])
            op["loc"] = token["loc"]
            program.append(op)
            ip += 1

        elif token["type"] == Token.KEYWORD:
            assert len(Keyword) == 9, "Exhaustive ops handling in compile_tokens_to_program. Only ops that form blocks must be handled"
            if token["value"] == Keyword.IF:
                op["type"] = OP.IF
                op["loc"] = token["loc"]
                program.append(op)
                stack.append(ip)
                ip += 1

            elif token["value"] == Keyword.ELSE:
                op["type"] = OP.ELSE
                op["loc"] = token["loc"]
                program.append(op)
                if_ip = stack.pop()
                if program[if_ip]["type"] != OP.IF:
                    sys.exit('%s:%d:%d: ERROR: `else` can only be used in `if`-blocks' % program[if_ip]["loc"])
                program[if_ip]["jmp"] = ip + 1
                stack.append(ip)
                ip += 1

            elif token["value"] == Keyword.END:
                op["type"] = OP.END
                op["loc"] = token["loc"]
                program.append(op)
                block_ip = stack.pop()
                if program[block_ip]["type"] == OP.IF or program[block_ip]["type"] == OP.ELSE:
                    program[block_ip]["jmp"] = ip
                    program[ip]["jmp"] = ip + 1
                elif program[block_ip]["type"] == OP.DO:
                    assert program[block_ip]["jmp"] is not None
                    program[ip]["jmp"] = program[block_ip]["jmp"]
                    program[block_ip]["jmp"] = ip + 1
                else:
                    sys.exit('%s:%d:%d: ERROR: `end` can only close `if`, `else` or `do` blocks for now' % program[block_ip]["loc"])
                ip += 1

            elif token["value"] == Keyword.WHILE:
                op["type"] = OP.WHILE
                op["loc"] = token["loc"]
                program.append(op)
                stack.append(ip)
                ip += 1

            elif token["value"] == Keyword.DO:
                op["type"] = OP.DO
                op["loc"] = token["loc"]
                program.append(op)
                while_ip = stack.pop()
                program[ip]["jmp"] = while_ip
                stack.append(ip)
                ip += 1
                
            elif token["value"] == Keyword.SYSCALL:
                callName = rtokens.pop()
                if callName["type"] != Token.STR:
                    sys.exit("%s:%d:%d: ERROR: expected syscall name to be %s but found %s" % (token["loc"] + (human(Token.STR), human(token["type"]))))

                op["type"] = OP.SYSCALL
                op["value"] = callName["value"]
                op["loc"] = token["loc"]
                program.append(op)
                ip += 1

            elif token["value"] == Keyword.SYSVAL:
                sysval = rtokens.pop()
                if sysval["type"] != Token.STR:
                    sys.exit("%s:%d:%d: ERROR: expected syscall name to be %s but found %s" % (token["loc"] + (human(Token.STR), human(token["type"]))))

                op["type"] = OP.SYSVAL
                op["value"] = sysval["value"]
                op["loc"] = token["loc"]
                program.append(op)
                ip += 1

            elif token["value"] == Keyword.INCLUDE:
                if len(rtokens) == 0:
                    sys.exit("%s:%d:%d: ERROR: expected include path but found nothing" % op["loc"])
                token = rtokens.pop()
                if token["type"] != Token.STR:
                    sys.exit("%s:%d:%d: ERROR: expected include path to be %s but found %s" % (token["loc"] + (human(Token.STR), human(token["type"]))))

                fileIncluded = False
                for p in includePaths:
                    try:
                        rtokens += reversed(lex_file(path.join(p,token["value"])))
                        fileIncluded = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not fileIncluded:
                    print(includePaths,token["value"])
                    sys.exit("%s:%d:%d: ERROR: `%s` file not found" % (token["loc"] + (token["value"],)))
            

                
            # TODO: capability to define macros from command line
            elif token["value"] == Keyword.MACRO:
                if len(rtokens) == 0:
                    sys.exit("%s:%d:%d: ERROR: expected macro name but found nothing" % token["loc"])
                token = rtokens.pop()

                if token["type"] != Token.WORD:
                    sys.exit("%s:%d:%d: ERROR: expected macro name to be %s but found %s" % (token["loc"] + (human(Token.WORD), human(token["type"]))))

                assert isinstance(token["value"], str), "This is probably a bug in the lexer"
                if token["value"] in macros:
                    print("%s:%d:%d: ERROR: redefinition of already existing macro `%s`" % (token["loc"] + (token["value"], )))
                    sys.exit("%s:%d:%d: NOTE: the first definition is located here" % macros[token["value"]]["loc"])

                if token["value"] in INTRINSIC_WORDS:
                    print("%s:%d:%d: ERROR: redefinition of a builtin word `%s`" % (token["loc"] + (token["value"], )))

                macro = {"loc" : token["loc"], "tokens" : []}
                macros[token["value"]] = macro

                # TODO: support for nested blocks within the macro definition
                nestAmt = 0
                while len(rtokens) > 0:
                    token = rtokens.pop()
                    assert len(Keyword) == 9, f"Exaustive handling of keywords with `end` in compile_tokens_to_program for end type starters like Keyword.IF, Keyword.DO {len(Keyword)}"
                    if token["type"] == Token.KEYWORD and token["value"] in [Keyword.IF, Keyword.DO]:
                        nestAmt += 1

                    macro["tokens"].append(token)

                    if token["type"] == Token.KEYWORD and token["value"] == Keyword.END:
                        if nestAmt == 0:
                            break
                        elif nestAmt > 0:
                            nestAmt -= 1
                        else:
                            sys.exit(f"Error: nest amt is below zero {nestAmt}")

                if token["type"] != Token.KEYWORD or token["value"] != Keyword.END:
                    sys.exit("%s:%d:%d: ERROR: expected `end` at the end of the macro definition of `%s`" % (token["loc"] + (token["value"], )))
                else:
                    macro["tokens"] = macro["tokens"][:-1]
                    
            else:
                assert False, 'unreachable'
        else:
            assert False, 'unreachable'

    if len(stack) > 0:
        op = stack.pop()
        sys.exit('%s:%d:%d: ERROR: unclosed block `%s`' % (program[op]["loc"] + (human(program[op]["type"]),)))
    program.append({"type" : OP.INTRINSIC,"value": Intrinsic.EXIT})

    return program

"""
Program is a list of Ops
OP is a dict with the follwing possible fields
- `type` -- The type of the OP. One of OP.PUSH_INT, OP.IF, OP.INTRINSIC etc
- `loc` -- location of the OP in the program it contains (`file_token`,  `row`, `col`)
- `value` -- Only exists for some OPs like OP.PUSH_INT and all OP.INTRINSIC.
- `jmp` -- It is an optional field and is used for code blocks like if,else, while, end etc. It is created in compile_tokens_to_program
"""

def load_program(program_token,includePaths=[]):
    tokens = lex_file(program_token)
    program = compile_tokens_to_program(tokens, includePaths)
    return program

def compile_program(program, outFilePath):
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)
        lt = []
        strs = []
        #add implementation of logic
        for i, op in enumerate(program):
            lt.append(f"addr_{i}:\n")
            assert len(OP) == 10, "Exhaustive handling of operations whilst compiling"

            if op["type"] == OP.PUSH_INT:
                valToPush = op["value"]
                lt.append(f"     ; -- push int {valToPush} --\n")
                lt.append(f"      push {valToPush}\n")
            
            if op["type"] == OP.PUSH_STR:
                valToPush = op["value"]
                lt.append(f"      lea edi, str_{len(strs)}\n")
                lt.append(f"      push {len(valToPush)}\n")
                lt.append(f"      push edi\n")
                strs.append(valToPush)
                # assert False, "Not Implemented yet"
            
            if op["type"] == OP.SYSCALL:
                callName = op["value"]
                lt.append(f"     ; -- syscall {callName} --\n")
                lt.append(f"      call {callName}\n")
                lt.append(f"      push eax\n")

            if op["type"] == OP.SYSVAL:
                sysval = op["value"]
                lt.append(f"     ; -- sysval {sysval} --\n")
                lt.append(f"      push {sysval}\n")
            
            if op["type"] == OP.IF:
                if "jmp" not in op:
                    sys.exit("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program[i]["loc"])
                jmpArg = op["jmp"]
                lt.append(f" ; -- if --\n")
                lt.append("      pop eax\n")
                lt.append("      cmp eax, 1\n")
                lt.append(f"      jne addr_{jmpArg}\n")
            
            if op["type"] == OP.ELSE:
                if "jmp" not in op:
                    sys.exit("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program[i]["loc"])
                jmpArg = op["jmp"]
                lt.append(f" ; -- else --\n")
                lt.append(f"      jmp addr_{jmpArg}\n")
            
            if op["type"] == OP.WHILE:
                lt.append(f" ; -- while --\n")

            if op["type"] == OP.DO:
                if "jmp" not in op:
                    sys.exit("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program[i]["loc"])
                jmp_idx = op["jmp"]
                lt.append(f" ; -- do --\n")
                lt.append( "      pop eax\n")
                lt.append( "      cmp eax, 1\n")
                lt.append(f"      jne addr_{jmp_idx}\n")
                
            if op["type"] == OP.END:
                jmp_idx = op["jmp"]
                if program[jmp_idx]["type"] == OP.WHILE:
                    lt.append(f"      ;-- endwhile --\n")
                    lt.append(f"      jmp addr_{jmp_idx}\n")
                elif program[jmp_idx]["type"] == OP.IF:
                    lt.append(f"      ;-- endif --\n")
                else:
                    lt.append(f"      ;-- end --\n")

            assert len(Intrinsic) == 26, f"Exaustive handling of Intrinsic's in Compiling {len(Intrinsic)}"
            if op["type"] == OP.INTRINSIC:

                if op["value"] == Intrinsic.STDOUT:
                    lt.append("      ;-- print --\n")
                    lt.append("      pop eax\n")
                    lt.append("      invoke StdOut, addr [eax]\n")
                
                # if op["value"] == Intrinsic.FOPEN:
                    # lt.append("      ;-- fopen --\n")
                    # lt.append("     pop eax\n")
                    # lt.append("     invoke CreateFile , eax, GENERIC_READ OR GENERIC_WRITE, FILE_SHARE_READ OR FILE_SHARE_WRITE, NULL, OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL, NULL\n")
                    # lt.append("     push eax\n")
                # 
                # if op["value"] == Intrinsic.FWRITE:
                    # lt.append("      ;-- fwrite --\n")
                    # lt.append("     pop ebx\n")
                    # lt.append("     pop edi\n")
                    # lt.append("     pop eax\n")
                    # lt.append("     invoke WriteFile, eax, edi, ebx, NULL, NULL\n")
                # 
                # if op["value"] == Intrinsic.FREAD:
                    # lt.append("      ;-- fread --\n")
                    # lt.append("     pop ebx\n")
                    # lt.append("     pop edi\n")
                    # lt.append("     pop eax\n")
                    # lt.append("     invoke ReadFile, eax, edi, ebx, NULL, NULL\n")
# 
                # if op["value"] == Intrinsic.FCLOSE:
                    # lt.append("      ;-- fclose --\n")
                    # lt.append("     pop eax\n")
                    # lt.append("     invoke CloseHandle, eax\n")

                if op["value"] == Intrinsic.EXIT:
                    lt.append("     ; -- exit --\n")
                    lt.append("     invoke ExitProcess, 0\n")

                if op["value"] == Intrinsic.DROP:
                    lt.append("      ; -- drop --\n")
                    lt.append("      pop eax\n")

                if op["value"] == Intrinsic.ADD:
                    lt.append(f"     ; -- add --\n")
                    lt.append("      pop eax\n")
                    lt.append("      pop ebx\n")
                    lt.append("      add eax, ebx\n")
                    lt.append("      push eax\n")


                if op["value"] == Intrinsic.SUB:
                    lt.append(f"     ; -- sub --\n")
                    lt.append("      pop ebx\n")
                    lt.append("      pop eax\n")
                    lt.append("      sub eax, ebx\n")
                    lt.append("      push eax\n")

                if op["value"] == Intrinsic.DIVMOD:
                    lt.append("    ; -- divmod --\n")
                    lt.append("      xor edx, edx\n")
                    lt.append("      pop ebx\n")
                    lt.append("      pop eax\n")
                    lt.append("      div ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push edx\n")
                    
                elif op["value"] == Intrinsic.MUL:
                    lt.append("    ;; -- mul --\n")
                    lt.append("    pop  eax\n")
                    lt.append("    pop  ebx\n")
                    lt.append("    mul  ebx\n")
                    lt.append("    push eax\n")

                if op["value"] == Intrinsic.EQUAL:
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
                                
                if op["value"] == Intrinsic.NE:
                    lt.append(f"     ; -- equal --\n")
                    lt.append(f"      pop eax\n")
                    lt.append(f"      pop ebx\n")
                    lt.append(f"      cmp eax, ebx\n")
                    lt.append(f"      je ZERO{i}\n")
                    lt.append(f"      push 1\n")
                    lt.append(f"      jmp END{i}\n")
                    lt.append(f"      ZERO{i}:\n")
                    lt.append(f"          push 0\n")
                    lt.append(f"      END{i}:\n")


                if op["value"] == Intrinsic.GT:
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

                if op["value"] == Intrinsic.LT:
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

                if op["value"] == Intrinsic.DUMP:
                    lt.append(f"      ; -- dump --\n")
                    lt.append("      pop eax\n")
                    lt.append("      lea edi, decimalstr\n")
                    lt.append("      call DUMP\n")

                if op["value"] == Intrinsic.DUP:
                    lt.append("      ; -- duplicate (dup) --\n")
                    lt.append("      pop eax\n")
                    lt.append("      push eax\n")
                    lt.append("      push eax\n")

                if op["value"] == Intrinsic.DUP2:
                    lt.append("      ; -- 2 duplicate (2dup) --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")

                if op["value"] == Intrinsic.OVER:
                    lt.append("      ; -- over --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ebx\n")

                if op["value"] == Intrinsic.OVER2:
                    lt.append("      ; -- over2 --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      pop  ecx\n")
                    lt.append("      push ecx\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ecx\n")

                if op["value"] == Intrinsic.SWAP:
                    lt.append("      ; -- swap --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ebx\n")


                if op["value"] == Intrinsic.MEM:
                    lt.append("      ;-- mem --\n")
                    lt.append("      lea edi, mem\n")
                    lt.append("      push edi\n")

                if op["value"] == Intrinsic.LOAD:
                    lt.append("      ;-- load (,) --\n")
                    lt.append("      pop eax\n")
                    lt.append("      xor ebx, ebx\n")
                    lt.append("      mov bl, [eax]\n")
                    lt.append("      push ebx\n")
            
                if op["value"] == Intrinsic.LOAD32:
                    lt.append("      ;-- load32 --\n")
                    lt.append("      pop eax\n")
                    lt.append("      xor ebx, ebx\n")
                    lt.append("      mov ebx, [eax]\n")
                    lt.append("      push ebx\n")


                if op["value"] == Intrinsic.STORE:
                    lt.append("      ;-- store (.) --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      mov  byte ptr [ebx], al\n")

                if op["value"] == Intrinsic.STORE32:
                    lt.append("      ;-- store32 --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      mov  [ebx], eax\n")


                if op["value"] == Intrinsic.SHL:
                    lt.append("      ;-- shl --\n")
                    lt.append("      pop ecx\n")
                    lt.append("      pop ebx\n")
                    lt.append("      shl ebx, cl\n")
                    lt.append("      push ebx\n")


                if op["value"] == Intrinsic.SHR:
                    lt.append("      ;-- shr --\n")
                    lt.append("      pop ecx\n")
                    lt.append("      pop ebx\n")
                    lt.append("      shr ebx, cl\n")
                    lt.append("      push ebx\n")

                if op["value"] == Intrinsic.BOR:
                    lt.append("      ;-- bor --\n")
                    lt.append("      pop eax\n")
                    lt.append("      pop ebx\n")
                    lt.append("      or ebx, eax\n")
                    lt.append("      push  ebx\n")

                if op["value"] == Intrinsic.BAND:
                    lt.append("      ;-- band --\n")
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
        wf.write("    mem db 100000 dup(?)\n")
        wf.write(".code\n")
        wf.write("    start PROC\n")

        wf.write("".join(lt))
        with open("static\endAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)


MEM_CAPACITY = 690_000
STR_CAPACITY = 690_000
def simulate_program(program):
    stack = []
    mem = bytearray(MEM_CAPACITY + STR_CAPACITY)
    strPtr = STR_CAPACITY
    i = 0
    while i < len(program):
        op = program[i]

        assert len(OP) == 8, f"Exhaustive handling of operations whilst simulating {len(OP)}"
        if op["type"] == OP.PUSH_INT:
            stack.append(op["value"])
            i += 1
        
        elif op["type"] == OP.PUSH_STR:
            bs = bytes(op["value"], "utf-8")
            n = len(bs)
            if "addr" not in op:
                op["addr"] = strPtr
                mem[strPtr:strPtr+n] = bs
                strPtr += n
                assert strPtr <= STR_CAPACITY+MEM_CAPACITY, "String Buffer Overflow"
            stack.append(len(op["value"]))
            stack.append(op["addr"])
            i += 1

        elif op["type"] == OP.IF:
            a = stack.pop()
            if "jmp" not in op:
                sys.exit("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program[i]["loc"])
            if a == 0:
                i = op["jmp"]
            else:
                i += 1

        elif op["type"] == OP.ELSE:
            if "jmp" not in op:
                sys.exit("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program[i]["loc"])
            i = op["jmp"]
        
        elif op["type"] == OP.WHILE:
            i += 1

        elif op["type"] == OP.DO:
            if "jmp" not in op:
                sys.exit("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program[i]["loc"])

            a = stack.pop()
            if a == 0:
                i = op["jmp"]
            else:
                i += 1

        elif op["type"] == OP.END:
            i = op["jmp"]

        elif op["type"] == OP.INTRINSIC:
        
            assert len(Intrinsic) == 26, f"Exaustive handling of Intrinsic's in Simulation {len(Intrinsic)}"
            if op["value"] == Intrinsic.EXIT:
                if i != len(program) - 1:
                    exit()
                i += 1

            if op["value"] == Intrinsic.DROP:
                stack.pop()
                i += 1

            elif op["value"] == Intrinsic.ADD:
                a = stack.pop()
                b = stack.pop()
                stack.append(a+b)
                i += 1

            elif op["value"] == Intrinsic.SUB:
                a = stack.pop()
                b = stack.pop()
                stack.append(b-a)
                i += 1
            
            elif op["value"] == Intrinsic.DIVMOD:
                a = stack.pop()
                b = stack.pop()
                stack.append(b//a)
                stack.append(b%a)
                i += 1

            elif op["value"] == Intrinsic.MUL:
                a = stack.pop()
                b = stack.pop()
                stack.append(b*a)
                i += 1

            elif op["value"] == Intrinsic.EQUAL:
                a = stack.pop()
                b = stack.pop()
                stack.append(int(a == b))
                i += 1

            elif op["value"] == Intrinsic.NE:
                a = stack.pop()
                b = stack.pop()
                stack.append(int(a != b))
                i += 1
            
            elif op["value"] == Intrinsic.NE:
                a = stack.pop()
                b = stack.pop()
                stack.append(int(a != b))
                i += 1

            elif op["value"] == Intrinsic.GT:
                b = stack.pop()
                a = stack.pop()
                stack.append(int(a > b))
                i += 1

            elif op["value"] == Intrinsic.LT:
                b = stack.pop()
                a = stack.pop()
                stack.append(int(a < b))
                i += 1


            elif op["value"] == Intrinsic.DUP:
                stack.append(stack[-1])
                i += 1

            elif op["value"] == Intrinsic.DUP2:
                stack.append(stack[-2])
                stack.append(stack[-2])
                i += 1


            elif op["value"] == Intrinsic.OVER:
                stack.append(stack[-2])
                i += 1

            elif op["value"] == Intrinsic.OVER2:
                stack.append(stack[-3])
                i += 1

            elif op["value"] == Intrinsic.SWAP:
                temp = stack[-1]
                stack[-1] = stack[-2]
                stack[-2] = temp
                i += 1

            elif op["value"] == Intrinsic.DUMP:
                a = stack.pop()
                print(a)
                i += 1

            elif op["value"] == Intrinsic.MEM:
                stack.append(0)
                i += 1

            elif op["value"] == Intrinsic.LOAD:
                addr = stack.pop()
                byte = mem[addr]
                stack.append(byte)
                i += 1

            elif op["value"] == Intrinsic.LOAD32:
                addr = stack.pop()
                stack.append(mem[addr] | (mem[addr + 1]<<8) | (mem[addr + 2]<<16) | (mem[addr + 3]<<24) )
                i += 1

            elif op["value"] == Intrinsic.STORE:
                val = stack.pop()
                addr = stack.pop()
                mem[addr] = val & 0xFF
                i += 1

            elif op["value"] == Intrinsic.STORE32:
                store_value = stack.pop()
                store_addr32 = stack.pop()
                mem[store_addr32 + 0] = store_value & 0xff
                mem[store_addr32 + 1] = (store_value>>8) & 0xff
                mem[store_addr32 + 2] = (store_value>>16) & 0xff
                mem[store_addr32 + 3] = (store_value>>24) & 0xff
                i += 1

            elif op["value"] == Intrinsic.STDOUT:
                addr = stack.pop()
                addrStr = addr
                while mem[addr] != 0:
                    print(chr(mem[addr]), end='')
                    addr += 1
                i += 1
                # print(addrStr, mem[addrStr:addrStr+20])

            elif op["value"] == Intrinsic.SHL:
                shiftAmt = stack.pop()
                val = stack.pop()
                stack.append(val << shiftAmt)
                i += 1

            elif op["value"] == Intrinsic.SHR:
                shiftAmt = stack.pop()
                val = stack.pop()
                stack.append(val >> shiftAmt)
                i += 1

            elif op["value"] == Intrinsic.BOR:
                a= stack.pop()
                b = stack.pop()
                stack.append(a | b)
                i += 1

            elif op["value"] == Intrinsic.BAND:
                a= stack.pop()
                b = stack.pop()
                stack.append(a & b)
                i += 1
        # if "value" in op: 
            # print(op["type"],op["value"] , stack, mem[:31])
        # else:
            # print(op["type"], stack, mem[:31])
        # input()

def usage(program_token):
    print("Usage: %s [OPTIONS] <SUBCOMMAND> [ARGS]" % program_token)
    print("OPTIONS:")
    print("   -I <path>             Add the path to the include search list")
    print("SUBCOMMAND:")
    print("   sim <file>  Simulate the program")
    print("   com <file>  Compile the program")
    print(    "OPTIONS:")
    print("        -r                  Run the program after successful compilation")
    print("        -o <file|dir>       Customize the output path")
    print("        -ob                 Set output path to `./build`")

def callCmd(cmd):
    cmdStr = " ".join(cmd)
    print(f"[CMD] {cmdStr}")
    subprocess.call(cmd)


def main():
    argv = sys.argv
    compilerPath, *argv = argv
    if len(sys.argv) < 2:
        usage(sys.argv[0])
        sys.exit("\n[ERROR] No subcommand Given")

    includePaths = [".", "./std/"]
    timed = False

    while len(argv) > 0:
        if argv[0] == "-I":
            argv = argv[1:]
            if len(argv) == 0:
                usage(compilerPath)
                sys.exit("[ERROR] no path is provided for `-I` flag", file=sys.stderr)

            includePath, *argv = argv
            includePaths.append(includePath)
        if argv[0] == "-t":
            timed = True
            argv = argv[1:]
        else:
            break
    
    if len(argv) < 1:
        usage(compilerPath)
        sys.exit("[ERROR] no subcommand is provided", file=sys.stderr)
    subcommand, *argv = argv 

    programPath = None

    if subcommand == "sim":
        if len(argv) < 1:
            usage(compilerPath)
            sys.exit("[ERROR] no input file is provided for the simulation", file=sys.stderr)
        programPath, *argv = argv
        if timed:
            programBuildTime = time.time()
        program = load_program(programPath, includePaths)
        if timed:
            print(f"[TIME] Program Build Time: {time.time() - programBuildTime} secs")
            programBuildTime = time.time()

        print("[INFO] loaded program")
        simulate_program(program)
        if timed:
            print(f"[TIME] Run Time: {time.time() - programBuildTime} secs")
    
    elif subcommand == "com":
        run = False
        outputPath = None
        while len(argv) > 0:
            arg, *argv = argv
            if arg == "-r":
                run = True
            elif arg == "-o":
                if len(argv) == 0:
                    usage(compilerPath)
                    sys.exit("[ERROR] no argument is provided for parameter -o", file=sys.stderr)
                outputPath, *argv = argv
            elif arg == "-ob":
                outputPath = "./build/"
            else:
                programPath = arg
                break
        if programPath == None:
            usage(compilerPath)
            sys.exit("[ERROR] no input file is provided for the compilation", file=sys.stderr)
        
        if outputPath == None:
            baseDir = getcwd()
            programFile = path.basename(programPath)
            programName = programFile.replace(".porth","")
            basePath = path.join(baseDir,programName)
        else:
            baseDir = outputPath
            if path.isdir(baseDir):
                programFile = path.basename(programPath)
                programName = programFile.replace(".porth","")
                basePath = path.join(baseDir,programName)
            else:
                usage(compilerPath)
                print("[ERROR] Invalid Path entered")
        if timed:
            start = time.time()
        program = load_program(programPath, includePaths)
        print("[INFO] loaded program")
        compile_program(program,f"{basePath}.asm")
        print(f"[INFO] Generated {basePath}.asm")
        callCmd(["ml","/Fo" ,f"{basePath}.obj", "/c", "/Zd", "/coff", f"{basePath}.asm"])
        callCmd(["Link",f"/OUT:{basePath}.exe", "/SUBSYSTEM:CONSOLE",  f"{basePath}.obj"])
        if timed:
            print(f"[TIME] Compile Time: {time.time() - start} secs")
            start = time.time()
        if run:
            callCmd([f"{basePath}.exe"])
            if timed:
                print(f"[TIME] Run Time: {time.time()- start} secs")
    

if __name__ == "__main__":
    main()
from io import FileIO
import sys
from enum import Enum,auto,IntEnum
import subprocess
from os import path, getcwd
import time
from dataclasses import dataclass
from typing import *


EXPANSION_LIMIT = 1000

class TokenType(Enum):
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
    MEMORY = auto()
    INCLUDE = auto()
    SYSCALL = auto()
    SYSVAL = auto()
    BREAK = auto()
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
    BXOR = auto()

class OpType(Enum):
    # stack operations
    PUSH_INT = auto()
    PUSH_STR = auto()
    PUSH_MEM = auto()
    # syscall
    SYSCALL = auto()
    SYSVAL = auto()
    # blocks
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    DO = auto()
    END = auto()
    BREAK = auto()
    INTRINSIC = auto()

assert len(Keyword) == 11, f"Exhaustive handling in KEYWORD NAMES {len(Keyword)}"
KEYWORD_NAMES = {
    "if"    :   Keyword.IF,
    "else"  :   Keyword.ELSE,
    "while" :   Keyword.WHILE,
    "do"    :   Keyword.DO,
    "macro" :   Keyword.MACRO,
    "memory" : Keyword.MEMORY,
    "include":  Keyword.INCLUDE,
    "syscall":  Keyword.SYSCALL,
    "sysval":  Keyword.SYSVAL,
    "break":  Keyword.BREAK,
    "end"   :   Keyword.END,
}

assert len(Intrinsic) == 27 , f"Exhaustive handling in INTRINSIC_WORDS {len(Intrinsic)}"
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
    "store8"     : Intrinsic.STORE,
    "load8"     : Intrinsic.LOAD,
    "store32":Intrinsic.STORE32,
    "load32": Intrinsic.LOAD32,
    "shl"   : Intrinsic.SHL,
    "shr"   : Intrinsic.SHR,
    "bor"   : Intrinsic.BOR,
    "band"  : Intrinsic.BAND,
    "bxor"  : Intrinsic.BXOR
}

Loc=Tuple[str, int, int]

assert len(TokenType) == 5, "Exhaustive Token type definition. The `value` field of the Token dataclass may require an update"
@dataclass
class Token:
    type: TokenType
    text: str
    loc: Loc
    value: Union[int, str, Keyword]
    # https://www.python.org/dev/peps/pep-0484/#forward-references
    expanded_from: Optional['Token'] = None
    expanded: int = 0

OpAddr=int
MemAddr=int

@dataclass
class Op:
    type: OpType
    token: Token 
    operand: Optional[Union[int, str, Intrinsic, OpAddr]] = None

@dataclass
class Program:
    ops : List[Op]
    memory_capacity : int = 0


def find_col(line : str, start : int, predicate : Callable[[str], bool]) -> int:
    while start < len(line) and predicate(line[start]):
        start += 1
    return start

def unescape_string(s: str) -> str:
    # NOTE: unicode_escape assumes latin-1 encoding, so we kinda have
    # to do this weird round trip
    return s.encode('utf-8').decode('unicode_escape').encode('latin-1').decode('utf-8')

def lex_lines(file_path : str, lines : List[str]) -> Generator[Token, None, None]:

    for row, line in enumerate(lines):
        col = find_col(line, 0, lambda x: x.isspace())
        assert len(TokenType) == 5, "Exahuastive handling of tokens in lex_lines"
        comment = False
        while col < len(line) and not comment:
            loc = (file_path, row + 1, col + 1)

            if line[col] == '"':
                col_end = find_col(line, col+1, lambda x: not x == '"')
                if col_end >= len(line) or line[col_end] != '"':
                    print("%s:%d:%d error: string literal not closed" % loc )
                text_of_token = line[col+1:col_end]
                yield Token(TokenType.STR, text_of_token, loc, unescape_string(text_of_token))
                col = find_col(line, col_end+1, lambda x: x.isspace())

            elif line[col] == "'":
                col_end = find_col(line, col+1, lambda x: not x == "'")
                if col_end >= len(line) or line[col_end] != "'":
                    print("%s:%d:%d error: string literal not closed" % loc )
                text_of_token = line[col+1:col_end]
                char = unescape_string(text_of_token)
                if len(char) != 1:
                    sys.exit("%s:%d:%d only a single byte is allowed inside of a character literal" % loc)
                yield Token(TokenType.CHAR, text_of_token, loc, ord(char))
                col = find_col(line, col_end+1, lambda x: x.isspace())

            else:
                col_end = find_col(line, col, lambda x: not x.isspace())
                text_of_token = line[col:col_end]
                try:
                    yield Token(TokenType.INT, text_of_token, loc, int(text_of_token))
                except ValueError:
                    if text_of_token in KEYWORD_NAMES:
                        yield Token(TokenType.KEYWORD, text_of_token, loc, KEYWORD_NAMES[text_of_token])
                    else:
                        comment = text_of_token.startswith('//')
                        if not comment:
                            yield Token(TokenType.WORD, text_of_token, loc, text_of_token)
                col = find_col(line, col_end, lambda x: x.isspace())

"""
Token is a dict with the follwing possible fields
- `type` -- The type of the OpType One of TokenType.INT, TokenType.WORD etc
- `loc` -- location of the OP in the program it contains (`file_token`,  `row`, `col`)
- `value` -- the value of the token depending on the type of the TokenType. For `str` it's TokenType.WORD and For `int` it's TokenType.INT
- `expanded` -- the counter for the number of tokens expanded from OpType.MACRO and OpType.INCLUDE
"""


def lex_file(file_path : str) -> List[Token]:
    with open(file_path, "r") as f:
        ans = [token for token in lex_lines(file_path, f.readlines())]
        return ans

def expandMacro(token : Token) -> Token:
    token.expanded += 1
    return token

"""
Macro is a Dictionary
"macrotoken" -> (loc, tokens)
"""
@dataclass
class Macro:
    loc: Loc
    tokens: List[Token]

def evaluate_constant_from_tokens(rtokens : List[Token]) -> int:
    stack : List[int] = []
    while len(rtokens) > 0:
        token = rtokens.pop()
        if token.type == TokenType.KEYWORD:
            if token.value == Keyword.END:
                break
            else:
                sys.exit("%s:%d:%d unsupported keyword `%s` in constant evaluation" % (token.loc + (token.text,)))
        elif token.type == TokenType.INT:
            assert isinstance(token.value, int)
            stack.append(token.value)
        elif token.type == TokenType.WORD:
            if token.value == Intrinsic.ADD:
                a = stack.pop()
                b = stack.pop()
                stack.append(a + b)
            elif token.value == Intrinsic.MUL:
                a = stack.pop()
                b = stack.pop()
                stack.append(a*b)
            else:
                sys.exit("%s:%d:%d unsupported word `%s` in constant evaluation" % (token.loc + (token.text,)))
        else:
            sys.exit("%s:%d:%d unsupported token `%s` in constant evaluation" % (token.loc + (token.text,)))

    if len(stack) != 1:
        sys.exit("%s:%d:%d memory definition expects one int" % token.loc)
    return stack.pop()

def compile_tokens_to_program(tokens : List[Token], includePaths : List[str]=[]) -> Program:
    human = lambda x: str(x).split(".")[-1].lower()
    stack : List[OpAddr] = []
    program: Program = Program(ops=[], memory_capacity=0)
    rtokens : List[Token] = list(reversed(tokens))
    macros: Dict[str, Macro] = {}
    memories : Dict[str, MemAddr] = {}
    ip : OpAddr = 0
    while len(rtokens) > 0:
        # TODO: some sort of safety mechanism for recursive macros
        token : Token = rtokens.pop()

        assert len(TokenType) == 5, "Exhaustive token handling in compile_tokens_to_program"
        if token.type == TokenType.WORD:
            assert isinstance(token.value, str), "This could be a bug in the lexer"
            if token.value in INTRINSIC_WORDS:
                op = Op(OpType.INTRINSIC, token, INTRINSIC_WORDS[token.value])
                program.ops.append(op)
                ip += 1

            elif token.value in macros:
                mtkGen =  map(expandMacro, reversed(macros[token.value].tokens))
                mtk = list(mtkGen)

                if len(list(mtk)) == 0:
                    sys.exit("%s:%d:%d: error: macro is empty" %  token.loc)

                if len(list(mtk)) != 0:
                    rtokens += mtk

                    if EXPANSION_LIMIT < rtokens[-1].expanded:
                        sys.exit("%s:%d:%d: error: macro exansion limit of %d exceeded" %  (token.loc + (EXPANSION_LIMIT, )))
                    continue
            
            elif token.value in memories:
                op = Op(OpType.PUSH_MEM, token, memories[token.value])
                program.ops.append(op)
                ip += 1
            else:
                print(memories,[ tok.text for tok in rtokens])
                sys.exit("%s:%d:%d: unknown word `%s`" % (token.loc + (token.text, )))
            

        elif token.type == TokenType.INT:
            assert isinstance(token.value, int), "This could be a bug in the lexer"
            op = Op(OpType.PUSH_INT, token, token.value)
            program.ops.append(op)
            ip += 1

        elif token.type == TokenType.STR:
            assert isinstance(token.value, str), "This could be a bug in the lexer"
            op = Op(OpType.PUSH_STR , token, token.value)
            program.ops.append(op)
            ip += 1

        elif token.type == TokenType.CHAR:
            assert isinstance(token.value, int), "This could be a bug in the lexer"
            op = Op(OpType.PUSH_INT, token, token.value)
            program.ops.append(op)
            ip += 1

        elif token.type == TokenType.KEYWORD:
            assert len(Keyword) == 11, "Exhaustive ops handling in compile_tokens_to_program. Only ops that form blocks must be handled"
            if token.value == Keyword.IF:
                op = Op(OpType.IF, token)
                program.ops.append(op)
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.ELSE:
                op = Op(OpType.ELSE, token)
                program.ops.append(op)
                if_ip = stack.pop()
                if program.ops[if_ip].type != OpType.IF:
                    sys.exit('%s:%d:%d: ERROR: `else` can only be used in `if`-blocks' % program.ops[if_ip].token.loc)
                program.ops[if_ip].operand = ip + 1
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.END:
                op = Op(OpType.END, token)
                program.ops.append(op)
                block_ip = stack.pop()
                if program.ops[block_ip].type == OpType.IF or program.ops[block_ip].type == OpType.ELSE:
                    program.ops[block_ip].operand = ip
                    program.ops[ip].operand = ip + 1

                elif program.ops[block_ip].type == OpType.DO:
                    assert program.ops[block_ip].operand is not None
                    program.ops[ip].operand = program.ops[block_ip].operand
                    program.ops[block_ip].operand = ip + 1
                else:
                    print([op.token.text for op in program.ops])
                    sys.exit('%s:%d:%d: ERROR: `end` can only close `if`, `else` or `do` blocks for now' % program.ops[block_ip].token.loc)
                ip += 1

            elif token.value == Keyword.WHILE:
                op = Op(OpType.WHILE, token)
                program.ops.append(op)
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.DO:
                op = Op(OpType.DO, token)
                program.ops.append(op)
                while_ip = stack.pop()
                program.ops[ip].operand = while_ip
                stack.append(ip)
                ip += 1

            #TODO: add show stack after break
            elif token.value == Keyword.BREAK:
                op = Op(OpType.BREAK, token)
                program.ops.append(op)
                ip += 1

            elif token.value == Keyword.SYSCALL:
                callName = rtokens.pop()
                if callName.type != TokenType.STR:
                    sys.exit("%s:%d:%d: ERROR: expected syscall name to be %s but found %s" % (token.loc + (human(TokenType.STR), human(token.type))))

                op = Op(OpType.SYSCALL, token)
                program.ops.append(op)
                ip += 1

            elif token.value == Keyword.SYSVAL:
                sysval = rtokens.pop()
                if sysval.type != TokenType.STR:
                    sys.exit("%s:%d:%d: ERROR: expected sysval name to be %s but found %s" % (token.loc + (human(TokenType.STR), human(token.type))))

                op = Op(OpType.SYSVAL, token)
                program.ops.append(op)
                ip += 1

            elif token.value == Keyword.INCLUDE:
                if len(rtokens) == 0:
                    sys.exit("%s:%d:%d: ERROR: expected include path but found nothing" % op.token.loc)

                token = rtokens.pop()
                if token.type != TokenType.STR:
                    sys.exit("%s:%d:%d: ERROR: expected include path to be %s but found %s" % (token.loc + (human(TokenType.STR), human(token.type))))

                fileIncluded = False
                for p in includePaths:
                    try:
                        assert isinstance(token.value, str)
                        rtokens += reversed(lex_file(path.join(p, token.value)))
                        # print([token.text for token in list(lex_file(path.join(p, token.value)))])
                        fileIncluded = True
                        break
                    except FileNotFoundError:
                        continue
                
                if not fileIncluded:
                    print(includePaths,token.value)
                    sys.exit("%s:%d:%d: ERROR: `%s` file not found" % (token.loc + (token.value,)))
            

            elif token.value == Keyword.MEMORY:
                if len(rtokens) == 0:
                    sys.exit("%s:%d:%d: ERROR: expected memory name but found nothing" % token.loc)
                
                token = rtokens.pop()
                if token.type != TokenType.WORD:
                    sys.exit("%s:%d:%d: ERROR: expected memory name to be %s but found %s" % (token.loc + (human(TokenType.WORD), human(token.type))))
                
                memory_name = token.value
                if memory_name in macros:
                    assert isinstance(token.value, str)
                    print("%s:%d:%d: ERROR: redefinition of already existing macro `%s`" % (token.loc + (token.value, )))
                    sys.exit("%s:%d:%d: NOTE: the first definition is located here" % macros[token.value].loc)

                if memory_name in INTRINSIC_WORDS:
                    print("%s:%d:%d: ERROR: redefinition of a builtin word `%s`" % (token.loc + (token.value, )))

                if memory_name in memories:
                    sys.exit("%s:%d:%d: ERROR: redefinition of already existing memory `%s`" % (token.loc + (token.value, )))
                    # sys.exit("%s:%d:%d: NOTE: the first definition is located here" % memories[token.value].loc)

                mem_size = evaluate_constant_from_tokens(rtokens)
                memories[memory_name] = program.memory_capacity
                program.memory_capacity += mem_size

            # TODO: capability to define macros from command line
            elif token.value == Keyword.MACRO:
                if len(rtokens) == 0:
                    sys.exit("%s:%d:%d: ERROR: expected macro name but found nothing" % token.loc)
                token = rtokens.pop()

                if token.type != TokenType.WORD:
                    sys.exit("%s:%d:%d: ERROR: expected macro name to be %s but found %s" % (token.loc + (human(TokenType.WORD), human(token.type))))

                assert isinstance(token.value, str), "This is probably a bug in the lexer"
                if token.value in macros:
                    print("%s:%d:%d: ERROR: redefinition of already existing macro `%s`" % (token.loc + (token.value, )))
                    sys.exit("%s:%d:%d: NOTE: the first definition is located here" % macros[token.value].loc)

                if token.value in INTRINSIC_WORDS:
                    print("%s:%d:%d: ERROR: redefinition of a builtin word `%s`" % (token.loc + (token.value, )))
                
                if token.value in memories:
                    sys.exit("%s:%d:%d: ERROR: redefinition of already existing memory `%s`" % (token.loc + (token.value, )))

                macro = Macro(token.loc, [])
                macros[token.value] = macro

                # TODO: support for nested blocks within the macro definition
                nestAmt = 0
                while len(rtokens) > 0:
                    token = rtokens.pop()
                    assert len(Keyword) == 11, f"Exaustive handling of keywords with `end` in compile_tokens_to_program for end type starters like Keyword.IF, Keyword.DO {len(Keyword)}"
                    if token.type == TokenType.KEYWORD and token.value in [Keyword.IF, Keyword.DO]:
                        nestAmt += 1

                    macro.tokens.append(token)

                    if token.type == TokenType.KEYWORD and token.value == Keyword.END:
                        if nestAmt == 0:
                            break
                        elif nestAmt > 0:
                            nestAmt -= 1
                        else:
                            sys.exit(f"Error: nest amt is below zero {nestAmt}")

                if token.type != TokenType.KEYWORD or token.value != Keyword.END:
                    sys.exit("%s:%d:%d: ERROR: expected `end` at the end of the macro definition of `%s`" % (token.loc + (token.value, )))
                else:
                    macro.tokens = macro.tokens[:-1]
                    
            else:
                assert False, 'unreachable'
        else:
            assert False, 'unreachable'

    if len(stack) > 0:
        opIdx = stack.pop()
        sys.exit('%s:%d:%d: ERROR: unclosed block `%s`' % (program.ops[opIdx].token.loc + (human(program.ops[opIdx].type),)))
    return program

"""
Program is a list of Ops
OP is a dict with the follwing possible fields
- `type` -- The type of the OpType. One of OpType.PUSH_INT, OpType.IF, OpType.INTRINSIC etc
- `loc` -- location of the OP in the program it contains (`file_token`,  `row`, `col`)
- `value` -- Only exists for some OPs like OpType.PUSH_INT and all OpType.INTRINSIC.
- `jmp` -- It is an optional field and is used for code blocks like if,else, while, end etc. It is created in compile_tokens_to_program
"""

def load_program(file_path : str ,includePaths : List[str]=[]) -> Program:
    tokens = lex_file(file_path)
    program : Program = compile_tokens_to_program(tokens, includePaths)
    return program

def compile_program(program : Program, outFilePath : str) -> None:
    with open(outFilePath,"w+") as wf:
        with open("static\startAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)
        lt : List[str] = []
        strs : List[str] = []
        #add implementation of logic
        for i, op in enumerate(program.ops):
            lt.append(f"addr_{i}:\n")
            assert len(OpType) == 12, "Exhaustive handling of operations whilst compiling"

            if op.type == OpType.PUSH_INT:
                valToPush = op.operand
                lt.append(f"     ; -- push int {valToPush} --\n")
                lt.append(f"      push {valToPush}\n")
            
            if op.type == OpType.PUSH_STR:
                valToPush = op.operand
                assert isinstance(valToPush, str)
                lt.append(f"      lea edi, str_{len(strs)}\n")
                lt.append(f"      push {len(valToPush)}\n")
                lt.append(f"      push edi\n")
                strs.append(valToPush)
                # assert False, "Not Implemented yet"
            
            if op.type == OpType.PUSH_MEM:
                lt.append(f"      ;-- push mem {op.token.value}--\n")
                lt.append(f"      lea edi, mem\n")
                lt.append(f"      add edi, {op.operand}\n")
                lt.append(f"      push edi\n")

            if op.type == OpType.SYSCALL:
                callName = op.operand
                lt.append(f"     ; -- syscall {callName} --\n")
                lt.append(f"      call {callName}\n")
                lt.append(f"      push eax\n")

            if op.type == OpType.SYSVAL:
                sysval = op.operand
                lt.append(f"     ; -- sysval {sysval} --\n")
                lt.append(f"      push {sysval}\n")

            if op.type == OpType.BREAK:
                pass
            
            if op.type == OpType.IF:
                if not op.operand:
                    sys.exit("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
                jmpArg = op.operand
                lt.append(f" ; -- if --\n")
                lt.append("      pop eax\n")
                lt.append("      cmp eax, 1\n")
                lt.append(f"      jne addr_{jmpArg}\n")
            
            if op.type == OpType.ELSE:
                if not op.operand:
                    sys.exit("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
                jmpArg = op.operand
                lt.append(f" ; -- else --\n")
                lt.append(f"      jmp addr_{jmpArg}\n")
            
            if op.type == OpType.WHILE:
                lt.append(f" ; -- while --\n")

            if op.type == OpType.DO:
                if not op.operand:
                    sys.exit("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
                jmp_idx = op.operand
                lt.append(f" ; -- do --\n")
                lt.append( "      pop eax\n")
                lt.append( "      cmp eax, 1\n")
                lt.append(f"      jne addr_{jmp_idx}\n")
                
            if op.type == OpType.END:
                assert isinstance(op.operand, int)
                jmp_idx = op.operand
                if program.ops[jmp_idx].type == OpType.WHILE:
                    lt.append(f"      ;-- endwhile --\n")
                    lt.append(f"      jmp addr_{jmp_idx}\n")
                elif program.ops[jmp_idx].type == OpType.IF:
                    lt.append(f"      ;-- endif --\n")
                else:
                    lt.append(f"      ;-- end --\n")

            assert len(Intrinsic) == 27, f"Exaustive handling of Intrinsic's in Compiling {len(Intrinsic)}"
            if op.type == OpType.INTRINSIC:

                if op.operand == Intrinsic.STDOUT:
                    lt.append("      ;-- print --\n")
                    lt.append("      pop eax\n")
                    lt.append("      invoke StdOut, addr [eax]\n")

                if op.operand == Intrinsic.EXIT:
                    lt.append("     ; -- exit --\n")
                    lt.append("     invoke ExitProcess, 0\n")

                if op.operand == Intrinsic.DROP:
                    lt.append("      ; -- drop --\n")
                    lt.append("      pop eax\n")

                if op.operand == Intrinsic.ADD:
                    lt.append(f"     ; -- add --\n")
                    lt.append("      pop eax\n")
                    lt.append("      pop ebx\n")
                    lt.append("      add eax, ebx\n")
                    lt.append("      push eax\n")


                if op.operand == Intrinsic.SUB:
                    lt.append(f"     ; -- sub --\n")
                    lt.append("      pop ebx\n")
                    lt.append("      pop eax\n")
                    lt.append("      sub eax, ebx\n")
                    lt.append("      push eax\n")

                if op.operand == Intrinsic.DIVMOD:
                    lt.append("    ; -- divmod --\n")
                    lt.append("      xor edx, edx\n")
                    lt.append("      pop ebx\n")
                    lt.append("      pop eax\n")
                    lt.append("      div ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push edx\n")
                    
                elif op.operand == Intrinsic.MUL:
                    lt.append("    ;; -- mul --\n")
                    lt.append("    pop  eax\n")
                    lt.append("    pop  ebx\n")
                    lt.append("    mul  ebx\n")
                    lt.append("    push eax\n")

                if op.operand == Intrinsic.EQUAL:
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
                                
                if op.operand == Intrinsic.NE:
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


                if op.operand == Intrinsic.GT:
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

                if op.operand == Intrinsic.LT:
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

                if op.operand == Intrinsic.DUMP:
                    lt.append(f"      ; -- dump --\n")
                    lt.append("      pop eax\n")
                    lt.append("      lea edi, decimalstr\n")
                    lt.append("      call DUMP\n")

                if op.operand == Intrinsic.DUP:
                    lt.append("      ; -- duplicate (dup) --\n")
                    lt.append("      pop eax\n")
                    lt.append("      push eax\n")
                    lt.append("      push eax\n")

                if op.operand == Intrinsic.DUP2:
                    lt.append("      ; -- 2 duplicate (2dup) --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")

                if op.operand == Intrinsic.OVER:
                    lt.append("      ; -- over --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ebx\n")

                if op.operand == Intrinsic.OVER2:
                    lt.append("      ; -- over2 --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      pop  ecx\n")
                    lt.append("      push ecx\n")
                    lt.append("      push ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ecx\n")

                if op.operand == Intrinsic.SWAP:
                    lt.append("      ; -- swap --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      push eax\n")
                    lt.append("      push ebx\n")


                if op.operand == Intrinsic.MEM:
                    lt.append("      ;-- mem --\n")
                    lt.append("      lea edi, mem\n")
                    lt.append("      push edi\n")

                if op.operand == Intrinsic.LOAD:
                    lt.append("      ;-- load (,) --\n")
                    lt.append("      pop eax\n")
                    lt.append("      xor ebx, ebx\n")
                    lt.append("      mov bl, [eax]\n")
                    lt.append("      push ebx\n")
            
                if op.operand == Intrinsic.LOAD32:
                    lt.append("      ;-- load32 --\n")
                    lt.append("      pop eax\n")
                    lt.append("      xor ebx, ebx\n")
                    lt.append("      mov ebx, [eax]\n")
                    lt.append("      push ebx\n")


                if op.operand == Intrinsic.STORE:
                    lt.append("      ;-- store (.) --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      mov  byte ptr [ebx], al\n")

                if op.operand == Intrinsic.STORE32:
                    lt.append("      ;-- store32 --\n")
                    lt.append("      pop  eax\n")
                    lt.append("      pop  ebx\n")
                    lt.append("      mov  [ebx], eax\n")


                if op.operand == Intrinsic.SHL:
                    lt.append("      ;-- shl --\n")
                    lt.append("      pop ecx\n")
                    lt.append("      pop ebx\n")
                    lt.append("      shl ebx, cl\n")
                    lt.append("      push ebx\n")


                if op.operand == Intrinsic.SHR:
                    lt.append("      ;-- shr --\n")
                    lt.append("      pop ecx\n")
                    lt.append("      pop ebx\n")
                    lt.append("      shr ebx, cl\n")
                    lt.append("      push ebx\n")

                if op.operand == Intrinsic.BOR:
                    lt.append("      ;-- bor --\n")
                    lt.append("      pop eax\n")
                    lt.append("      pop ebx\n")
                    lt.append("      or ebx, eax\n")
                    lt.append("      push  ebx\n")

                if op.operand == Intrinsic.BAND:
                    lt.append("      ;-- band --\n")
                    lt.append("      pop eax\n")
                    lt.append("      pop ebx\n")
                    lt.append("      and ebx, eax\n")
                    lt.append("      push  ebx\n")

                if op.operand == Intrinsic.BXOR:
                    lt.append("      ;-- bxor --\n")
                    lt.append("      pop eax\n")
                    lt.append("      pop ebx\n")
                    lt.append("      xor ebx, eax\n")
                    lt.append("      push  ebx\n")


        lt.append(f"addr_{len(program.ops)}:\n")
        wf.write(".data\n")
        wf.write("    decimalstr db 16 DUP (0)  ; address to store dump values\n")
        wf.write("    aSymb db 97, 0\n")
        wf.write("    negativeSign db \"-\", 0    ; negativeSign     \n")
        wf.write("    nl DWORD 10               ; new line character in ascii\n")
        for i,s in enumerate(strs):
            sAsNum = ", ".join(map(str,list(bytes(s,"utf-8"))))
            wf.write(f"    str_{i} db {sAsNum}, 0 \n")
        wf.write(".data?\n")
        wf.write(f"    mem db {program.memory_capacity} dup(?)\n")
        wf.write(".code\n")
        wf.write("    start PROC\n")

        wf.write("".join(lt))
        with open("static\endAsm.txt","r") as rf:
            text = rf.read()
        wf.write(text)



class SV(IntEnum):
    FILE_ATTRIBUTE_NORMAL= auto()
    OPEN_ALWAYS = auto()
    FILE_SHARE_READ_OR_FILE_SHARE_WRITE = auto()
    GENERIC_READ_OR_GENERIC_WRITE = auto()
    FILE_BEGIN = auto()
    FILE_END = auto()
    FILE_CUR = auto()

assert len(SV) == 7, f"Exaustive handling of SV in sysvalues"
sysvalues = {
    "FILE_ATTRIBUTE_NORMAL" : SV.FILE_ATTRIBUTE_NORMAL,
    "OPEN_ALWAYS" : SV.OPEN_ALWAYS,
    "FILE_SHARE_READ OR FILE_SHARE_WRITE" : SV.FILE_SHARE_READ_OR_FILE_SHARE_WRITE,
    "GENERIC_READ OR GENERIC_WRITE" : SV.GENERIC_READ_OR_GENERIC_WRITE,
    "FILE_BEGIN" : SV.FILE_BEGIN,
    "FILE_END" : SV.FILE_END,
    "FILE_CUR" : SV.FILE_CUR
}

def getStrFromAddr(addr : int, mem_buffer : bytearray) -> str:
    string = ""
    while mem_buffer[addr] != 0:
        string += chr(mem_buffer[addr])
        addr += 1
    return string
MEM_PADDING = 1
STR_CAPACITY = 690_000
def simulate_program(program : Program) -> None:
    stack : List[int] = []
    handles : List[TextIO] = []
    mem = bytearray(MEM_PADDING + program.memory_capacity + STR_CAPACITY)
    mem_buf_ptr = MEM_PADDING

    str_buf_ptr = MEM_PADDING + program.memory_capacity
    str_size = 0
    str_ptrs : Dict[int, int] = {}

    breakpoint = False
    show_strings = [False, 20]
    show_mem = [False, 50]

    i : int = 0
    while i < len(program.ops):
        op = program.ops[i]
        # print(stack)

        assert len(OpType) == 12, f"Exhaustive handling of operations whilst simulating {len(OpType)}"
        if op.type == OpType.PUSH_INT:
            assert isinstance(op.operand, int)
            valToPush = op.operand
            if valToPush < 0:
                valToPush = -valToPush
                valToPush = valToPush^0xFFFFFFFF
                valToPush += 1
            stack.append(valToPush)
            i += 1
        
        elif op.type == OpType.PUSH_STR:
            assert isinstance(op.operand, str)
            bs = bytes(op.operand, "utf-8")
            n = len(bs)
            stack.append(n)
            if i not in str_ptrs:
                str_ptr = str_buf_ptr + str_size
                str_ptrs[i] = str_ptr
                mem[str_ptr:str_ptr+n] = bs
                str_size += n
                assert str_size <= STR_CAPACITY+program.memory_capacity, "String Buffer Overflow"
            stack.append(str_ptrs[i])
            i += 1
        
        elif op.type == OpType.PUSH_MEM:
            assert isinstance(op.operand, MemAddr)
            stack.append(op.operand + mem_buf_ptr)
            i += 1

        elif op.type == OpType.SYSCALL:
            if op.operand == "CreateFile":
                fileNameIdx = stack.pop()
                stack = stack[:-6]
                fileName = getStrFromAddr(fileNameIdx, mem)

                handles.append(open(fileName, "r+"))
                stack.append(len(handles)-1)

            elif op.operand == "WriteFile":
                handleIdx = stack.pop()
                stringIdx = stack.pop()
                stack = stack[:-3]
                handle = handles[handleIdx]
                string = getStrFromAddr(stringIdx, mem)
                handle.write(string)
                stack.append(1)
            
            elif op.operand == "ReadFile":
                handleIdx = stack.pop()
                read_file_store_addr32 = stack.pop()
                amtToRead = stack.pop()
                stack = stack[:-2]
                if handleIdx >= len(handles):
                    sys.exit("%s:%d:%d ERROR: handles index %s is out" % (op.token.loc + (handleIdx,)))
                handle = handles[handleIdx]
                
                text_read = handle.read(amtToRead)
                for j in range(amtToRead):
                    mem[read_file_store_addr32 + j] = ord(text_read[j])
                stack.append(1)

            elif op.operand == "CloseHandle":
                handleIdx = stack.pop()
                handles[handleIdx].close()
                stack.append(1)
            elif op.operand == "SetFilePointer":
                handleIdx = stack.pop()
                amtToMove = stack.pop()
                stack.pop()
                moveMethod = stack.pop()
                if moveMethod == SV.FILE_BEGIN:
                    whence = 0
                elif moveMethod == SV.FILE_CUR:
                    whence = 1
                elif moveMethod == SV.FILE_END:
                    whence = 2
                else:
                    sys.exit("%s:%d:%d ERROR: invalid move method %s in SetFilePointer" % (op.token.loc + (moveMethod,)))
                
                handle = handles[handleIdx]
                handle.seek(amtToMove, whence)
                stack.append(1)
            elif op.operand == "SetEndOfFile":
                handleIdx = stack.pop()
                handle = handles[handleIdx]
                handle.truncate()
                stack.append(1)
            else:
                sys.exit("%s:%d:%d ERROR: syscall %s not found" % (op.token.loc + (op.operand,)))            
            
            i += 1
        
        elif op.type == OpType.SYSVAL:
            if op.operand in sysvalues:
                assert isinstance(op.operand, str)
                stack.append(int(sysvalues[op.operand]))
            else:
                sys.exit("%s:%d:%d ERROR: sysvalue %s not found" % (op.token.loc + (op.operand,)))
            i += 1

        elif op.type == OpType.BREAK:
            breakpoint = True
            i += 1

        elif op.type == OpType.IF:
            a = stack.pop()
            if not op.operand:
                sys.exit("%s:%d:%d ERROR: `if` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
            if a == 0:
                assert isinstance(op.operand, int)
                i = op.operand
            else:
                i += 1

        elif op.type == OpType.ELSE:
            if not op.operand:
                sys.exit("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
            assert isinstance(op.operand, int)
            i = op.operand
        
        elif op.type == OpType.WHILE:
            i += 1

        elif op.type == OpType.DO:
            if not op.operand:
                sys.exit("%s:%d:%d ERROR: `do` can only be used when `end` is mentioned" % program.ops[i].token.loc)

            a = stack.pop()
            if a == 0:
                assert isinstance(op.operand, int)
                i = op.operand
            else:
                i += 1

        elif op.type == OpType.END:
            assert isinstance(op.operand, int)
            i = op.operand

        elif op.type == OpType.INTRINSIC:
        
            assert len(Intrinsic) == 27, f"Exaustive handling of Intrinsic's in Simulation {len(Intrinsic)}"
            if op.operand == Intrinsic.EXIT:
                exit()
                i += 1

            if op.operand == Intrinsic.DROP:
                try:
                    stack.pop()
                except IndexError:
                    print("%s:%d:%d" % op.token.loc)
                    exit()
                i += 1

            elif op.operand == Intrinsic.ADD:
                a = stack.pop()
                b = stack.pop()
                stack.append(a+b)
                i += 1

            elif op.operand == Intrinsic.SUB:
                a = stack.pop()
                b = stack.pop()
                stack.append(b-a)
                i += 1
            
            elif op.operand == Intrinsic.DIVMOD:
                a = stack.pop()
                b = stack.pop()
                stack.append(b//a)
                stack.append(b%a)
                i += 1

            elif op.operand == Intrinsic.MUL:
                a = stack.pop()
                b = stack.pop()
                stack.append(b*a)
                i += 1

            elif op.operand == Intrinsic.EQUAL:
                a = stack.pop()
                b = stack.pop()
                stack.append(int(a == b))
                i += 1

            elif op.operand == Intrinsic.NE:
                a = stack.pop()
                b = stack.pop()
                stack.append(int(a != b))
                i += 1
            
            elif op.operand == Intrinsic.NE:
                a = stack.pop()
                b = stack.pop()
                stack.append(int(a != b))
                i += 1

            elif op.operand == Intrinsic.GT:
                b = stack.pop()
                a = stack.pop()
                stack.append(int(a > b))
                i += 1

            elif op.operand == Intrinsic.LT:
                b = stack.pop()
                a = stack.pop()
                stack.append(int(a < b))
                i += 1


            elif op.operand == Intrinsic.DUP:
                stack.append(stack[-1])
                i += 1

            elif op.operand == Intrinsic.DUP2:
                stack.append(stack[-2])
                stack.append(stack[-2])
                i += 1


            elif op.operand == Intrinsic.OVER:
                stack.append(stack[-2])
                i += 1

            elif op.operand == Intrinsic.OVER2:
                stack.append(stack[-3])
                i += 1

            elif op.operand == Intrinsic.SWAP:
                temp = stack[-1]
                stack[-1] = stack[-2]
                stack[-2] = temp
                i += 1

            elif op.operand == Intrinsic.DUMP:
                a = stack.pop()
                print(a)
                i += 1

            elif op.operand == Intrinsic.MEM:
                stack.append(0)
                i += 1

            elif op.operand == Intrinsic.LOAD:
                addr = stack.pop()
                byte = mem[addr]
                stack.append(byte)
                i += 1

            elif op.operand == Intrinsic.LOAD32:
                addr = stack.pop()
                stack.append(mem[addr] | (mem[addr + 1]<<8) | (mem[addr + 2]<<16) | (mem[addr + 3]<<24) )
                i += 1

            elif op.operand == Intrinsic.STORE:
                val = stack.pop()
                addr = stack.pop()
                mem[addr] = val & 0xFF
                i += 1

            elif op.operand == Intrinsic.STORE32:
                store_value = stack.pop()
                store_addr32 = stack.pop()
                mem[store_addr32 + 0] = store_value & 0xff
                mem[store_addr32 + 1] = (store_value>>8) & 0xff
                mem[store_addr32 + 2] = (store_value>>16) & 0xff
                mem[store_addr32 + 3] = (store_value>>24) & 0xff
                i += 1

            elif op.operand == Intrinsic.STDOUT:
                addr = stack.pop()
                while mem[addr] != 0:
                    print(chr(mem[addr]), end='')
                    addr += 1
                i += 1
                # print(addrStr, mem[addrStr:addrStr+20])

            elif op.operand == Intrinsic.SHL:
                shiftAmt = stack.pop()
                val = stack.pop()
                stack.append(val << shiftAmt)
                i += 1

            elif op.operand == Intrinsic.SHR:
                shiftAmt = stack.pop()
                val = stack.pop()
                stack.append(val >> shiftAmt)
                i += 1

            elif op.operand == Intrinsic.BOR:
                a= stack.pop()
                b = stack.pop()
                stack.append(a | b)
                i += 1

            elif op.operand == Intrinsic.BAND:
                a= stack.pop()
                b = stack.pop()
                stack.append(a & b)
                i += 1
            elif op.operand == Intrinsic.BXOR:
                a= stack.pop()
                b = stack.pop()
                stack.append(a ^ b)
                i += 1

        if breakpoint:
            print(f"{op.token.text}: {stack}")
            flags = input()
            for val in flags.split(" "):
                if val.startswith("s"):
                    val = val[1:]
                    show_strings[0] = not show_strings[0]
                    if val.isnumeric():
                        show_strings[1] = int(val)
                        
                elif val.startswith("m"):
                    val = val[1:]
                    show_mem[0] = not show_mem[0]
                    if val.isnumeric():
                        show_mem[1] = int(val)
            if show_strings[0]:
                print(f"strings: {mem[str_buf_ptr:str_buf_ptr + show_strings[1]]}")
            if show_mem[0]:
                print(f"mem: {mem[mem_buf_ptr:mem_buf_ptr + show_mem[1]]}")

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
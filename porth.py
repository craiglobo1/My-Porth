from io import FileIO
import sys
from enum import Enum,auto,IntEnum
import subprocess
from os import path, getcwd
import time
from dataclasses import dataclass
from typing import *
from copy import copy

EXPANSION_LIMIT = 1000
X86_32_RET_STACK_CAP = 4000

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
    ELIF = auto()
    WHILE = auto()
    DO = auto()
    MACRO = auto()
    PROC= auto()
    MEMORY = auto()
    INCLUDE = auto()
    SYSCALL = auto()
    SYSVAL = auto()
    BREAK = auto()
    END = auto()
    IN= auto()
    DASHDASH = auto()

class Intrinsic(Enum):
    # win32 api operations
    STDOUT = auto()
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
    # cast operations
    CAST_INT = auto()
    CAST_BOOL = auto()
    CAST_PTR = auto()

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
    ELIF = auto()
    WHILE = auto()
    DO = auto()
    END = auto()
    BREAK = auto()
    INTRINSIC = auto()
    SKIP_PROC=auto()
    RET=auto()
    CALL=auto()

assert len(Keyword) == 15, f"Exhaustive handling in KEYWORD NAMES {len(Keyword)}"
KEYWORD_NAMES = {
    "if"    :   Keyword.IF,
    "else"  :   Keyword.ELSE,
    "elif"    :   Keyword.ELIF,
    "while" :   Keyword.WHILE,
    "do"    :   Keyword.DO,
    "macro" :   Keyword.MACRO,
    "proc" :   Keyword.PROC,
    "memory" : Keyword.MEMORY,
    "include":  Keyword.INCLUDE,
    "syscall":  Keyword.SYSCALL,
    "sysval":  Keyword.SYSVAL,
    "break":  Keyword.BREAK,
    "end"   :   Keyword.END,
    "in"   :   Keyword.IN,
    "--"   :   Keyword.DASHDASH,
}

assert len(Intrinsic) == 29 , f"Exhaustive handling in INTRINSIC_WORDS {len(Intrinsic)}"
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
    "store8"     : Intrinsic.STORE,
    "load8"     : Intrinsic.LOAD,
    "store32":Intrinsic.STORE32,
    "load32": Intrinsic.LOAD32,
    "shl"   : Intrinsic.SHL,
    "shr"   : Intrinsic.SHR,
    "bor"   : Intrinsic.BOR,
    "band"  : Intrinsic.BAND,
    "bxor"  : Intrinsic.BXOR,
    "cast(int)"  : Intrinsic.CAST_INT,
    "cast(bool)"  : Intrinsic.CAST_BOOL,
    "cast(ptr)"  : Intrinsic.CAST_PTR
}
INTRINSIC_WORDS_TO_INTRINSIC = { val:key for key, val in INTRINSIC_WORDS.items() }

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
class SyscallData:
    name : str
    no_of_args : int


class DataType(Enum):
    INT=auto()
    PTR=auto()
    BOOL=auto()

DATATYPE_BY_NAME = {
    "int" : DataType.INT,
    "bool" : DataType.BOOL,
    "ptr" : DataType.PTR,
}

@dataclass
class Contract:
    ins : List[DataType]
    outs : List[DataType]

@dataclass
class Proc:
    name : str
    ip : int
    contract : Contract
    ret_ip : int = 0

@dataclass
class Op:
    type: OpType
    token: Token 
    operand: Optional[Union[int, str, Intrinsic, OpAddr, SyscallData, Proc]] = None

@dataclass
class Program:
    ops : List[Op]
    procs : List[Proc]
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

def lex_file(file_path : str) -> List[Token]:
    with open(file_path, "r") as f:
        ans = [token for token in lex_lines(file_path, f.readlines())]
        return ans

def expandMacro(token : Token) -> Token:
    token.expanded += 1
    return token



@dataclass
class Macro:
    loc: Loc
    tokens: List[Token]

def readable_enum(enum_val):
    return str(enum_val).split(".")[-1].lower()

def compiler_diagnostic(loc: Loc, tag: str, message: str, exits : bool =True):
    print("%s:%d:%d: %s: %s" % (loc + (tag, message)), file=sys.stderr)
    if exits:
        exit(1)

def compiler_error(loc: Loc, message: str, exits : bool = True):
    """
    Prints a compiler error message given a loc and a message
    """
    compiler_diagnostic(loc, 'ERROR', message, exits)

def compiler_note(loc: Loc, message: str, exits : bool = True):
    compiler_diagnostic(loc, 'NOTE', message,exits)

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
            if token.value == INTRINSIC_WORDS_TO_INTRINSIC[Intrinsic.ADD]:
                a = stack.pop()
                b = stack.pop()
                stack.append(a + b)
            elif token.value == INTRINSIC_WORDS_TO_INTRINSIC[Intrinsic.MUL]:
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



def compile_tokens_to_program(tokens : List[Token], includePaths : List[str]=[]) -> Tuple[Program, Dict[str, OpAddr]]:
    stack : List[OpAddr] = []
    program: Program = Program(ops=[], memory_capacity=0, procs=[])
    rtokens : List[Token] = list(reversed(tokens))
    macros: Dict[str, Macro] = {}
    memories : Dict[str, MemAddr] = {}
    current_proc : Optional[OpAddr] = None
    ip : OpAddr = 0
    while len(rtokens) > 0:
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
                    compiler_error(token.loc, "macro is empty")

                if len(list(mtk)) != 0:
                    rtokens += mtk

                    if EXPANSION_LIMIT < rtokens[-1].expanded:
                        compiler_error(token.loc, f"macro exansion limit of {EXPANSION_LIMIT} exceeded")
                    continue
            
            elif token.value in memories:
                op = Op(OpType.PUSH_MEM, token, memories[token.value])
                program.ops.append(op)
                ip += 1
            elif token.value in map(lambda x : x.name , program.procs):
                current_proc = list(filter(lambda x : x.name == token.value, program.procs))[0]
                program.ops.append(Op(OpType.CALL, token, current_proc))
                ip +=1
            else:
                print(memories,[ tok.text for tok in rtokens])
                compiler_error(token.loc, f"unknown word `{token.text}`")
            

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
            assert len(Keyword) == 15, "Exhaustive ops handling in compile_tokens_to_program. Only ops that form blocks must be handled"


            if token.value == Keyword.WHILE:
                op = Op(OpType.WHILE, token)
                program.ops.append(op)
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.DO:

                program.ops.append(Op(type=OpType.DO, token=token))
                if len(stack) == 0:
                    compiler_error(token.loc, "`do` is not preceded by `while`")

                while_ip = stack.pop()
                if program.ops[while_ip].type != OpType.WHILE:
                    compiler_error(token.loc, "`do` is not preceded by `while`")

                program.ops[ip].operand = while_ip
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.IF:
                program.ops.append(Op(type=OpType.IF, token=token))
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.ELIF:
                if len(stack) == 0:
                    compiler_error(token.loc, '`elif` can only come after `else`')

                else_ip = stack[-1]
                if program.ops[else_ip].type != OpType.ELSE:
                    compiler_error(program.ops[else_ip].token.loc, '`elif` can only come after `else`')

                program.ops.append(Op(type=OpType.ELIF, token=token))
                stack.append(ip)
                ip += 1

            elif token.value == Keyword.ELSE:
                if len(stack) == 0:
                    compiler_error(token.loc, '`else` can only come after `if` or `elif`')
                    exit(1)

                if_ip = stack.pop()
                if program.ops[if_ip].type == OpType.IF:
                    program.ops[if_ip].operand = ip + 1
                    stack.append(ip)
                    program.ops.append(Op(type=OpType.ELSE, token=token))
                    ip += 1

                elif program.ops[if_ip].type == OpType.ELIF:
                    else_before_elif_ip = None if len(stack) == 0 else stack.pop()
                    assert else_before_elif_ip is not None and program.ops[else_before_elif_ip].type == OpType.ELSE, "At this point we should've already checked that `if*` comes after `else`. Otherwise this is a compiler bug."

                    program.ops[if_ip].operand = ip + 1
                    program.ops[else_before_elif_ip].operand = ip

                    stack.append(ip)
                    program.ops.append(Op(type=OpType.ELSE, token=token))
                    ip += 1
                else:
                    compiler_error(program.ops[if_ip].token.loc, f'`else` can only come after `if` or `elif`')


            elif token.value == Keyword.END:
                block_ip = stack.pop()

                if program.ops[block_ip].type == OpType.ELSE:
                    program.ops.append(Op(OpType.END, token))
                    program.ops[block_ip].operand = ip
                    program.ops[ip].operand = ip + 1
                
                elif program.ops[block_ip].type == OpType.DO:
                    program.ops.append(Op(OpType.END, token))
                    assert isinstance(program.ops[block_ip].operand, int)
                    while_ip = program.ops[block_ip].operand

                    assert isinstance(while_ip, OpAddr)
                    if program.ops[while_ip].type != OpType.WHILE:
                        compiler_error(program.ops[while_ip].token.loc, '`end` can only close `do` blocks that are preceded by `while`')

                    program.ops[ip].operand = while_ip
                    program.ops[block_ip].operand = ip + 1
                
                elif program.ops[block_ip].type == OpType.ELIF:
                    program.ops.append(Op(OpType.END, token))
                    else_before_elif_ip = None if len(stack) == 0 else stack.pop()
                    assert else_before_elif_ip is not None and program.ops[else_before_elif_ip].type == OpType.ELSE, "At this point we should've already checked that `if*` comes after `else`. Otherwise this is a compiler bug."
                    program.ops[block_ip].operand = ip
                    program.ops[else_before_elif_ip].operand = ip
                    program.ops[ip].operand = ip + 1
                elif program.ops[block_ip].type == OpType.SKIP_PROC:
                    program.ops.append(Op(OpType.RET, token, program.ops[block_ip].operand))
                    program.ops[block_ip].operand.ret_ip = ip + 1
                    current_proc = None
                    # assert False, "Not implemented"
                else:
                    compiler_error(program.ops[block_ip].token.loc, "`end` can only close `if`, `else`, `do`, `proc` or `macro` blocks for now")
                ip += 1

            #TODO: add show stack after break
            elif token.value == Keyword.BREAK:
                op = Op(OpType.BREAK, token)
                program.ops.append(op)
                ip += 1

            elif token.value == Keyword.SYSCALL:
                noOfArgs = rtokens.pop()
                if noOfArgs.type != TokenType.INT:
                    compiler_error(token.loc, f"expected syscall no of args to be {readable_enum(TokenType.INT)} but found {readable_enum(token.type)}")
                
                callName = rtokens.pop()
                if callName.type != TokenType.STR:
                    compiler_error(token.loc, f"expected syscall name to be {readable_enum(TokenType.STR)} but found {readable_enum(token.type)}")

                assert isinstance(callName.value, str) and isinstance(noOfArgs.value, int)
                op = Op(OpType.SYSCALL, token, SyscallData(callName.value, noOfArgs.value))
                program.ops.append(op)
                ip += 1

            elif token.value == Keyword.SYSVAL:
                sysval = rtokens.pop()
                if sysval.type != TokenType.STR:
                    compiler_error(token.loc, f"expected sysval name to be {readable_enum(TokenType.STR)} but found {readable_enum(token.type)}")

                assert isinstance(sysval.value, str)
                op = Op(OpType.SYSVAL, token, sysval.value)
                program.ops.append(op)
                ip += 1

            elif token.value == Keyword.INCLUDE:
                if len(rtokens) == 0:
                    compiler_error(token.loc, "expected include path but found nothing")

                token = rtokens.pop()
                if token.type != TokenType.STR:
                    compiler_error(token.loc, f"expected include path to be {readable_enum(TokenType.STR)} but found {readable_enum(token.type)}")

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
                    compiler_error(token.loc, f"`{token.value}` file not found")            

            elif token.value == Keyword.MEMORY:
                if len(rtokens) == 0:
                    compiler_error(token.loc, f"expected memory name but found nothing")
                
                token = rtokens.pop()
                if token.type != TokenType.WORD:
                    compiler_error(token.loc, f"expected memory name to be {readable_enum(TokenType.WORD)} but found {readable_enum(token.type)}")
                
                assert isinstance(token.value, str)
                memory_name : str = token.value
                if memory_name in macros:
                    assert isinstance(token.value, str)
                    compiler_error(token.loc, f"redefinition of already existing macro `{token.value}`", exits=False)
                    compiler_note(macros[token.value].loc, f"the first definition is located here")

                if memory_name in INTRINSIC_WORDS:
                    compiler_error(token.loc, f"redefinition of a builtin word `{token.value}`")

                if memory_name in memories:
                    compiler_error(token.loc, f"redefinition of already existing memory `{token.value}`", exits=False)
                    # compiler_note(memories[token.value].loc, "the first definition is located here")

                mem_size = evaluate_constant_from_tokens(rtokens)
                memories[memory_name] = program.memory_capacity
                program.memory_capacity += mem_size

            elif token.value == Keyword.PROC:
                if current_proc is None:


                    if len(rtokens) == 0:
                        compiler_error(token.loc, "expected procedure name but found nothing")
                    token = rtokens.pop()

                    if token.type != TokenType.WORD:
                        compiler_error(token.loc, f"expected procedure name to be a word but found {readable_enum(token.type)}")
                    
                    proc_name = token.value
                    if proc_name in map(lambda x : x.name , program.procs):
                        compiler_error(token.loc, f"procedure {proc_name} already exists")

                    contract = parse_proc_contract(rtokens)
                    if len(contract.outs) > 0:
                        current_proc = ip + len(contract.ins)
                    else:
                        current_proc = ip + 1
                    if len(contract.outs) > 0:
                        current_proc += len(contract.outs)
                    proc = Proc(proc_name, current_proc, contract)
                    program.procs.append(proc)
                    op = Op(type=OpType.SKIP_PROC, token=token, operand=proc)
                    program.ops.append(op)
                    stack.append(ip)
                    ip += 1

                else:
                    compiler_error(token.loc, "defining procedures in a procedure is not allowed", exits=False)
                    compiler_note(program.ops[current_proc].token.loc, "the current_proc starts here")

            # TODO: capability to define macros from command line
            elif token.value == Keyword.MACRO:
                if len(rtokens) == 0:
                    sys.exit("%s:%d:%d: ERROR: expected macro name but found nothing" % token.loc)
                token = rtokens.pop()

                if token.type != TokenType.WORD:
                    sys.exit("%s:%d:%d: ERROR: expected macro name to be %s but found %s" % (token.loc + (readable_enum(TokenType.WORD), readable_enum(token.type))))

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
                    assert len(Keyword) == 15, f"Exaustive handling of keywords with `end` in compile_tokens_to_program for end type starters like Keyword.IF, Keyword.DO {len(Keyword)}"
                    if token.type == TokenType.KEYWORD and token.value in [Keyword.IF, Keyword.WHILE, Keyword.PROC, Keyword.MEMORY, Keyword.MACRO]:
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

            elif token.value in [Keyword.IN, Keyword.DASHDASH]:
                compiler_error(token.loc, f"unexpected keyword {token.value}")

            else:
                assert False, 'unreachable'
        else:
            assert False, 'unreachable'

    if len(stack) > 0:
        opIdx = stack.pop()
        sys.exit('%s:%d:%d: ERROR: unclosed block `%s`' % (program.ops[opIdx].token.loc + (readable_enum(program.ops[opIdx].type),)))
    return program

def load_program(file_path : str ,includePaths : List[str]=[]) -> Program:
    tokens = lex_file(file_path)
    program : Program  = compile_tokens_to_program(tokens, includePaths)
    return program

DataStack=List[Tuple[DataType, Loc]]
@dataclass
class Context:
    stack : DataStack
    ip : int

def type_check_program(program : Program):
    """
    given a program it type checks the stack for each operation
    """
    visited_dos : Dict[OpAddr, DataStack] = {}
    contexts : List[Context] = [Context(stack=[], ip=0)]
    assert len(OpType) == 13, "Exhaustive handling of ops in type_check_program"
    while len(contexts) > 0:
        ctx = contexts[-1]
        if ctx.ip >= len(program.ops):
            if len(ctx.stack) != 0:
                compiler_error(ctx.stack[0][1], f"Error: unhandled values in the stack of {[readable_enum(val[0]) for val in ctx.stack]} at the end of the program")
            contexts.pop()
            continue
        op = program.ops[ctx.ip]
        if op.type == OpType.PUSH_INT:
            ctx.stack.append((DataType.INT, op.token.loc))
            ctx.ip += 1
        elif op.type == OpType.PUSH_STR:
            ctx.stack.append((DataType.INT, op.token.loc))
            ctx.stack.append((DataType.PTR, op.token.loc))
            ctx.ip += 1
        elif op.type == OpType.PUSH_MEM:
            ctx.stack.append((DataType.PTR, op.token.loc))
            ctx.ip += 1
        elif op.type == OpType.SYSCALL:
            assert isinstance(op.operand, SyscallData)
            syscall = op.operand

            for i in range(syscall.no_of_args):
                ctx.stack.pop()
            ctx.stack.append((DataType.INT, op.token.loc))
            ctx.ip += 1
        elif op.type == OpType.SYSVAL:
            ctx.stack.append((DataType.INT, op.token.loc))
            ctx.ip += 1
        elif op.type == OpType.IF:
            if len(ctx.stack) < 1:
                compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.type)} operand")
            a_type, a_loc = ctx.stack.pop()
            if a_type != DataType.BOOL:
                compiler_error(op.token.loc, f"Argument for {readable_enum(op.type)} operand has incorrect type of {readable_enum(a_type)} expected bool")
            ctx.ip += 1
            contexts.append(Context(stack=copy(ctx.stack), ip=op.operand))
            ctx = contexts[-1]
        elif op.type == OpType.ELSE:
            ctx.ip = op.operand
        elif op.type == OpType.ELIF:
            if len(ctx.stack) < 1:
                compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.type)} operand")
            a_type, a_loc = ctx.stack.pop()
            if a_type != DataType.BOOL:
                compiler_error(op.token.loc, f"Argument for {readable_enum(op.type)} operand has incorrect type of {readable_enum(a_type)} expected bool")
            ctx.ip += 1
            contexts.append(Context(stack=copy(ctx.stack), ip=op.operand))
            ctx = contexts[-1]
        elif op.type == OpType.WHILE:
            ctx.ip += 1
        elif op.type == OpType.DO:

            if len(ctx.stack) < 1:
                compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.type)} operand")
            
            a_type, a_loc = ctx.stack.pop()
            if a_type != DataType.BOOL:
                compiler_error(op.token.loc, f"Argument for {readable_enum(op.type)} operand has incorrect type of {readable_enum(a_type)} expected bool")

            if ctx.ip in visited_dos:
                expected_types = list(map(lambda x: x[0], visited_dos[ctx.ip]))
                actual_types = list(map(lambda x: x[0], ctx.stack))
                if expected_types != actual_types:
                    compiler_error(op.token.loc, 'Loops are not allowed to alter types and amount of elements on the stack between iterations!', exits=False)
                    compiler_note(op.token.loc, '-- Stack BEFORE a single iteration --', exits=False)

                    if len(visited_dos[ctx.ip]) == 0:
                        compiler_note(op.token.loc, '<empty>', exits=False)
                    else:
                        for typ, loc in visited_dos[ctx.ip]:
                            compiler_note(loc, readable_enum(typ), exits=False)
                    compiler_note(op.token.loc, '-- Stack AFTER a single iteration --', exits=False)
                    if len(ctx.stack) == 0:
                        compiler_note(op.token.loc, '<empty>', exits=False)
                    else:
                        for typ, loc in ctx.stack:
                            compiler_note(loc, readable_enum(typ), exits=False)
                    exit(1)
                else:
                    contexts.pop()
            else:
                visited_dos[ctx.ip] = copy(ctx.stack)
                ctx.ip += 1
                contexts.append(Context(stack=copy(ctx.stack), ip=op.operand))
                ctx = contexts[-1]

        elif op.type == OpType.END:
            assert isinstance(op.operand, OpAddr)
            ctx.ip = op.operand
        elif op.type == OpType.BREAK:
            ctx.ip += 1
        elif op.type == OpType.INTRINSIC:
            assert len(Intrinsic) == 29, "Exhaustive handling of Intrinsics in type_check_program"
                # win32 api operations
            if op.operand == Intrinsic.STDOUT:
                if len(ctx.stack) < 1:
                    compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.operand)} Intrinsic")
                str_type, str_loc = ctx.stack.pop()
                if str_type != DataType.PTR:
                    sys.exit("%s:%d:%d: Error: Argument for %s Intrinsic has incorrect type %s" % (str_loc + (readable_enum(op.operand), readable_enum(str_type))))
                
                # ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            
            elif op.operand == Intrinsic.CAST_INT:
                if len(ctx.stack) < 1:
                    compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.operand)} Intrinsic")
                a_type, a_loc = ctx.stack.pop()
                ctx.stack.append((DataType.INT, a_loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.CAST_BOOL:
                if len(ctx.stack) < 1:
                    compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.operand)} Intrinsic")
                a_type, a_loc = ctx.stack.pop()
                ctx.stack.append((DataType.BOOL, a_loc))            
                ctx.ip += 1
            elif op.operand == Intrinsic.CAST_PTR:
                if len(ctx.stack) < 1:
                    compiler_error(op.token.loc, f"not enough arguments for {readable_enum(op.operand)} Intrinsic")
                a_type, a_loc = ctx.stack.pop()
                ctx.stack.append((DataType.PTR, a_loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.EXIT:
                return

            elif op.operand == Intrinsic.ADD:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))

                if a_type == DataType.PTR and b_type == DataType.PTR:
                    sys.exit("%s:%d:%d: Error: both argument for %s Intrinsic are type %s which is a incorrect type" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))

                if a_type == DataType.PTR and b_type == DataType.INT or b_type == DataType.PTR and a_type == DataType.INT:
                    ctx.stack.append((DataType.PTR, op.token.loc))
                else:
                    ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.SUB:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))

                if a_type == DataType.PTR and b_type == DataType.PTR:
                    sys.exit("%s:%d:%d: Error: both argument for %s Intrinsic are type %s which is a incorrect type" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))

                if a_type == DataType.PTR and b_type == DataType.INT or b_type == DataType.PTR and a_type == DataType.INT:
                    ctx.stack.append((DataType.PTR, op.token.loc))
                else:
                    ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1

            elif op.operand == Intrinsic.DIVMOD:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1

            elif op.operand == Intrinsic.MUL:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
                
            elif op.operand == Intrinsic.EQUAL:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.BOOL, op.token.loc))
                ctx.ip += 1

            elif op.operand == Intrinsic.NE:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.BOOL, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.GT:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.BOOL, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.LT:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type not in [DataType.INT, DataType.PTR]:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.ip += 1
                ctx.stack.append((DataType.BOOL, op.token.loc))
            elif op.operand == Intrinsic.DROP:
                if len(ctx.stack) < 1:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                ctx.stack.pop()
                ctx.ip += 1
            elif op.operand == Intrinsic.DUMP:
                if len(ctx.stack) < 1:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))

                a_type, a_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                ctx.ip += 1
            elif op.operand == Intrinsic.DUP:
                if len(ctx.stack) < 1:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                ctx.stack.append((a_type, a_loc))
                ctx.stack.append((a_type, op.token.loc))
                ctx.ip += 1

            elif op.operand == Intrinsic.DUP2:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc  = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                ctx.stack.append((b_type, b_loc))
                ctx.stack.append((a_type, a_loc))
                ctx.stack.append((b_type, op.token.loc))
                ctx.stack.append((a_type, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.OVER:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                ctx.stack.append((b_type, b_loc))
                ctx.stack.append(a)
                ctx.stack.append((b_type, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.OVER2:
                if len(ctx.stack) < 3:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a = ctx.stack.pop()
                b = ctx.stack.pop()
                c = ctx.stack.pop()
                ctx.stack.append(c)
                ctx.stack.append(b)
                ctx.stack.append(a)
                ctx.stack.append(c)
                ctx.ip += 1
            elif op.operand == Intrinsic.SWAP:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a = ctx.stack.pop()
                b = ctx.stack.pop()
                ctx.stack.append(a)
                ctx.stack.append(b)
                ctx.ip += 1
            elif op.operand == Intrinsic.STORE:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                if b_type != DataType.PTR:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.ip += 1
            elif op.operand == Intrinsic.LOAD:
                a_type, a_loc = ctx.stack.pop()
                if a_type != DataType.PTR:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.STORE32:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                if b_type != DataType.PTR:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.ip += 1  
            elif op.operand == Intrinsic.LOAD32:
                a_type, a_loc = ctx.stack.pop()
                if a_type != DataType.PTR:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.SHL:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))

                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.SHR:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.BAND:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.BOR:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
                ctx.ip += 1
            elif op.operand == Intrinsic.BXOR:
                if len(ctx.stack) < 2:
                    sys.exit("%s:%d:%d: Error: not enough arguments for %s Intrinsic" % (op.token.loc + (readable_enum(op.operand),)))
                a_type, a_loc = ctx.stack.pop()
                b_type, b_loc = ctx.stack.pop()
                if a_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: First argument for %s Intrinsic has incorrect type %s" % (a_loc + (readable_enum(op.operand), readable_enum(a_type))))
                
                if b_type != DataType.INT:
                    sys.exit("%s:%d:%d: Error: Second argument for %s Intrinsic has incorrect type %s" % (b_loc + (readable_enum(op.operand), readable_enum(b_type))))
                ctx.stack.append((DataType.INT, op.token.loc))
        # compiler_diagnostic(op.token.loc,"", f"ctx:{len(contexts)-1} `{op.token.text}` ip:{ctx.ip} type check: {[ readable_enum(val[0]) for val in ctx.stack]} {readable_enum(op.type)} {readable_enum(op.operand)}",exits=False)

def parse_proc_contract(rtokens : List[Token]) -> Contract:
    contract = Contract(ins=[], outs=[])
    while len(rtokens) > 0:
        token = rtokens.pop()
        if token.type == TokenType.WORD:
            if token.value in DATATYPE_BY_NAME:
                contract.ins.append(DATATYPE_BY_NAME[token.value])
            else:
                compiler_error(token.loc, f"unknown datatype {token.value}")
        elif token.type == TokenType.KEYWORD:
            if token.value == Keyword.DASHDASH:
                break
            elif token.value == Keyword.IN:
                return contract
            else:
                compiler_error(token.loc, f"unknown keyword {token.value}")
        else:
            compiler_error(token.loc, f"unexpected token of type {token.type}")
    
    while len(rtokens) > 0:
        token = rtokens.pop()
        if token.type == TokenType.WORD:
            if token.value in DATATYPE_BY_NAME:
                contract.outs.append(DATATYPE_BY_NAME[token.value])
            else:
                compiler_error(token.loc, f"unknown datatype {token.value}")
        elif token.type == TokenType.KEYWORD:
            if token.value == Keyword.IN:
                return contract
            else:
                compiler_error(token.loc, f"unknown keyword {token.value}")
        else:
            compiler_error(token.loc, f"unexpected token of type {token.type}")
    compiler_error(token.loc, f"keyword `in`not encountered")

def compile_program(program : Program, outFilePath : str) -> None:
    content : Dict[str:str] = {"main" : "", "procs" : "", "strs" : ""}
    current_proc = ""
    writer : str = "main"
    no_of_strs : int = 0
    call_reg_order = ["eax", "ebx", "ecx", "edx"]

    #add implementation of logic
    for i, op in enumerate(program.ops):
        content[writer] += "\n" + 3*"  " +  f"addr_{i}:\n"
        assert len(OpType) == 16, f"Exhaustive handling of operations whilst compiling {len(OpType)}"

        if op.type == OpType.PUSH_INT:
            valToPush = op.operand
            content[writer] += f"     ; -- push int {valToPush} --\n"
            content[writer] += f"      push {valToPush}\n"
        
        elif op.type == OpType.PUSH_STR:
            no_of_strs += 1
            valToPush = op.operand
            assert isinstance(valToPush, str)
            content[writer] += f"      lea edi, str_{no_of_strs}\n"
            content[writer] += f"      push {len(valToPush)}\n"
            content[writer] += f"      push edi\n"
            str_as_nums = ", ".join(map(str,list(bytes(valToPush, "utf-8"))))
            content["strs"] += f"    str_{no_of_strs} db {str_as_nums}, 0 \n"
        
        elif op.type == OpType.PUSH_MEM:
            content[writer] += f"      ;-- push mem {op.token.value}--\n"
            content[writer] += f"      lea edi, mem\n"
            content[writer] += f"      add edi, {op.operand}\n"
            content[writer] += f"      push edi\n"

        elif op.type == OpType.SYSCALL:
            assert isinstance(op.operand, SyscallData)
            syscall = op.operand
            content[writer] += f"     ; -- syscall {syscall.name} --\n"
            content[writer] += f"      call {syscall.name}\n"
            content[writer] += f"      push eax\n"

        elif op.type == OpType.SYSVAL:
            sysval = op.operand
            content[writer] += f"     ; -- sysval {sysval} --\n"
            content[writer] += f"      push {sysval}\n"

        elif op.type == OpType.BREAK:
            pass
        
        elif op.type in [OpType.IF, OpType.ELIF]:
            jmp_idx = op.operand
            content[writer] += f" ; -- if --\n"
            content[writer] +=  "      pop eax\n"
            content[writer] +=  "      cmp eax, 1\n"
            content[writer] += f"      jne addr_{jmp_idx}\n"

        elif op.type == OpType.ELSE:
            if not op.operand:
                sys.exit("%s:%d:%d ERROR: `else` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
            jmpArg = op.operand
            content[writer] += f" ; -- else --\n"
            content[writer] += f"      jmp addr_{jmpArg}\n"
        
        elif op.type == OpType.WHILE:
            content[writer] += f" ; -- while --\n"

        elif op.type == OpType.DO:
            if not op.operand:
                sys.exit("%s:%d:%d ERROR: `do` can only be used when an `end` is mentioned" % program.ops[i].token.loc)
            jmp_idx = op.operand
            content[writer] += f" ; -- do --\n"
            content[writer] +=  "      pop eax\n"
            content[writer] +=  "      cmp eax, 1\n"
            content[writer] += f"      jne addr_{jmp_idx}\n"
            
        elif op.type == OpType.END:
            assert isinstance(op.operand, int)
            jmp_idx = op.operand
            if jmp_idx:
                content[writer] += f"      ;-- end --\n"
                content[writer] += f"      jmp addr_{jmp_idx}\n"

        elif op.type == OpType.SKIP_PROC:
            content[writer] += f"      ;-- skip proc --\n"
            writer = "procs"
            current_proc = op.token.value
            content[writer] += f"\n  {current_proc} PROC\n"
            print(op.operand)
            for i in range(len(op.operand.contract.ins)-1,-1,-1):
                content[writer] += f"      push {call_reg_order[i]}\n"

        elif op.type == OpType.RET:
            content[writer] += f"      ;-- RET proc --\n"
            for i in range(len(op.operand.contract.outs)-1,-1,-1):
                content[writer] += f"      pop {call_reg_order[i]}\n"
            content[writer] += f"      ret\n"
            content[writer] += f"  {current_proc} ENDP\n"
            writer = "main"
        
        elif op.type == OpType.CALL:
            content[writer] += f"      ;-- call proc --\n"
            for i in range(len(op.operand.contract.ins)):
                content[writer] += f"      pop {call_reg_order[i]}\n"
            content[writer] += f"      call {op.token.value}\n"
            for i in range(len(op.operand.contract.outs)):
                content[writer] += f"      push {call_reg_order[i]}\n"

        assert len(Intrinsic) == 29, f"Exaustive handling of Intrinsic's in Compiling {len(Intrinsic)}"
        if op.type == OpType.INTRINSIC:

            if op.operand == Intrinsic.STDOUT:
                content[writer] += "      ;-- print --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      invoke StdOut, addr [eax]\n"
            
            elif op.operand in [Intrinsic.CAST_INT, Intrinsic.CAST_BOOL, Intrinsic.CAST_PTR]:
                pass

            elif op.operand == Intrinsic.EXIT:
                content[writer] += "     ; -- exit --\n"
                content[writer] += "     invoke ExitProcess, 0\n"

            elif op.operand == Intrinsic.DROP:
                content[writer] += "      ; -- drop --\n"
                content[writer] += "      pop eax\n"

            elif op.operand == Intrinsic.ADD:
                content[writer] += f"     ; -- add --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      add eax, ebx\n"
                content[writer] += "      push eax\n"


            elif op.operand == Intrinsic.SUB:
                content[writer] += f"     ; -- sub --\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      sub eax, ebx\n"
                content[writer] += "      push eax\n"

            elif op.operand == Intrinsic.DIVMOD:
                content[writer] += "    ; -- divmod --\n"
                content[writer] += "      xor edx, edx\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      div ebx\n"
                content[writer] += "      push eax\n"
                content[writer] += "      push edx\n"
                
            elif op.operand == Intrinsic.MUL:
                content[writer] += "    ;; -- mul --\n"
                content[writer] += "    pop  eax\n"
                content[writer] += "    pop  ebx\n"
                content[writer] += "    mul  ebx\n"
                content[writer] += "    push eax\n"

            if op.operand == Intrinsic.EQUAL:
                content[writer] += f"     ; -- equal --\n"
                content[writer] += f"      pop eax\n"
                content[writer] += f"      pop ebx\n"
                content[writer] += f"      cmp eax, ebx\n"
                content[writer] += f"      jne ZERO{i}\n"
                content[writer] += f"      push 1\n"
                content[writer] += f"      jmp END{i}\n"
                content[writer] += f"      ZERO{i}:\n"
                content[writer] += f"          push 0\n"
                content[writer] += f"      END{i}:\n"
                            
            if op.operand == Intrinsic.NE:
                content[writer] += f"     ; -- equal --\n"
                content[writer] += f"      pop eax\n"
                content[writer] += f"      pop ebx\n"
                content[writer] += f"      cmp eax, ebx\n"
                content[writer] += f"      je ZERO{i}\n"
                content[writer] += f"      push 1\n"
                content[writer] += f"      jmp END{i}\n"
                content[writer] += f"      ZERO{i}:\n"
                content[writer] += f"          push 0\n"
                content[writer] += f"      END{i}:\n"


            if op.operand == Intrinsic.GT:
                content[writer] += f"     ; -- greater than --\n"
                content[writer] += f"      pop eax\n"
                content[writer] += f"      pop ebx\n"
                content[writer] += f"      cmp eax, ebx\n"
                content[writer] += f"      jge ZERO{i}\n"
                content[writer] += f"      push 1\n"
                content[writer] += f"      jmp END{i}\n"
                content[writer] += f"      ZERO{i}:\n"
                content[writer] += f"          push 0\n"
                content[writer] += f"      END{i}:\n"

            if op.operand == Intrinsic.LT:
                content[writer] += f"     ; -- less than --\n"
                content[writer] += f"      pop eax\n"
                content[writer] += f"      pop ebx\n"
                content[writer] += f"      cmp eax, ebx\n"
                content[writer] += f"      jle ZERO{i}\n"
                content[writer] += f"      push 1\n"
                content[writer] += f"      jmp END{i}\n"
                content[writer] += f"      ZERO{i}:\n"
                content[writer] += f"          push 0\n"
                content[writer] += f"      END{i}:\n"

            if op.operand == Intrinsic.DUMP:
                content[writer] += f"      ; -- dump --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      lea edi, decimalstr\n"
                content[writer] += "      call DUMP\n"

            if op.operand == Intrinsic.DUP:
                content[writer] += "      ; -- duplicate (dup) --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      push eax\n"
                content[writer] += "      push eax\n"

            if op.operand == Intrinsic.DUP2:
                content[writer] += "      ; -- 2 duplicate (2dup) --\n"
                content[writer] += "      pop  eax\n"
                content[writer] += "      pop  ebx\n"
                content[writer] += "      push ebx\n"
                content[writer] += "      push eax\n"
                content[writer] += "      push ebx\n"
                content[writer] += "      push eax\n"

            if op.operand == Intrinsic.OVER:
                content[writer] += "      ; -- over --\n"
                content[writer] += "      pop  eax\n"
                content[writer] += "      pop  ebx\n"
                content[writer] += "      push ebx\n"
                content[writer] += "      push eax\n"
                content[writer] += "      push ebx\n"

            if op.operand == Intrinsic.OVER2:
                content[writer] += "      ; -- over2 --\n"
                content[writer] += "      pop  eax\n"
                content[writer] += "      pop  ebx\n"
                content[writer] += "      pop  ecx\n"
                content[writer] += "      push ecx\n"
                content[writer] += "      push ebx\n"
                content[writer] += "      push eax\n"
                content[writer] += "      push ecx\n"

            if op.operand == Intrinsic.SWAP:
                content[writer] += "      ; -- swap --\n"
                content[writer] += "      pop  eax\n"
                content[writer] += "      pop  ebx\n"
                content[writer] += "      push eax\n"
                content[writer] += "      push ebx\n"

            if op.operand == Intrinsic.LOAD:
                content[writer] += "      ;-- load (,) --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      xor ebx, ebx\n"
                content[writer] += "      mov bl, [eax]\n"
                content[writer] += "      push ebx\n"
        
            if op.operand == Intrinsic.LOAD32:
                content[writer] += "      ;-- load32 --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      mov ebx, [eax]\n"
                content[writer] += "      push ebx\n"


            if op.operand == Intrinsic.STORE:
                content[writer] += "      ;-- store (.) --\n"
                content[writer] += "      pop  eax\n"
                content[writer] += "      pop  ebx\n"
                content[writer] += "      mov  byte ptr [ebx], al\n"

            if op.operand == Intrinsic.STORE32:
                content[writer] += "      ;-- store32 --\n"
                content[writer] += "      pop  eax\n"
                content[writer] += "      pop  ebx\n"
                content[writer] += "      mov  [ebx], eax\n"


            if op.operand == Intrinsic.SHL:
                content[writer] += "      ;-- shl --\n"
                content[writer] += "      pop ecx\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      shl ebx, cl\n"
                content[writer] += "      push ebx\n"


            if op.operand == Intrinsic.SHR:
                content[writer] += "      ;-- shr --\n"
                content[writer] += "      pop ecx\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      shr ebx, cl\n"
                content[writer] += "      push ebx\n"

            if op.operand == Intrinsic.BOR:
                content[writer] += "      ;-- bor --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      or ebx, eax\n"
                content[writer] += "      push  ebx\n"

            if op.operand == Intrinsic.BAND:
                content[writer] += "      ;-- band --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      and ebx, eax\n"
                content[writer] += "      push  ebx\n"

            if op.operand == Intrinsic.BXOR:
                content[writer] += "      ;-- bxor --\n"
                content[writer] += "      pop eax\n"
                content[writer] += "      pop ebx\n"
                content[writer] += "      xor ebx, eax\n"
                content[writer] += "      push  ebx\n"
    content[writer] += f"addr_{len(program.ops)}:\n"

    with open(outFilePath,"w+") as wf:
        wf.write(".386\n")
        wf.write(".model flat, stdcall\n")
        wf.write("option casemap:none\n")
        wf.write("include C:\masm32\include\windows.inc\n")
        wf.write("include C:\masm32\include\kernel32.inc\n")
        wf.write("include C:\masm32\include\\user32.inc\n")
        wf.write("include C:\masm32\include\masm32.inc\n")
        wf.write("includelib C:\masm32\lib\kernel32.lib\n")
        wf.write("includelib C:\masm32\lib\\user32.lib\n")
        wf.write("includelib C:\masm32\lib\masm32.lib\n")
        wf.write(".data\n")
        wf.write("    decimalstr db 16 DUP (0)  ; address to store dump values\n")
        wf.write("    aSymb db 97, 0\n")
        wf.write("    negativeSign db \"-\", 0    ; negativeSign     \n")
        wf.write("    nl DWORD 10               ; new line character in ascii\n")

        wf.write(content["strs"])

        wf.write(".data?\n")
        wf.write(f"    mem db {program.memory_capacity} dup(?)\n")
        wf.write(".code\n")
        wf.write("    start PROC\n")

        wf.write(content["main"])

        wf.write("  start ENDP\n")
        wf.write("\n")
        wf.write("  DUMP PROC             ; ARG: EDI pointer to string buffer ; EAX is the number to dump ; ECX,ESI,EBX is used\n")
        wf.write("    mov ecx, eax\n")
        wf.write("    shr ecx, 31\n")
        wf.write("\n")
        wf.write("    .if ecx == 1\n")
        wf.write("      xor eax, 0FFFFFFFFh\n")
        wf.write("      inc eax\n")
        wf.write("      mov esi, 1\n")
        wf.write("    .else\n")
        wf.write("      mov esi,0\n")
        wf.write("    .endif\n")
        wf.write("\n")
        wf.write("    mov ebx, 10             ; Divisor = 10\n")
        wf.write("    xor ecx, ecx            ; ECX=0 (digit counter)\n")
        wf.write("  @@:                       ; First Loop: store the remainders\n")
        wf.write("    xor edx, edx\n")
        wf.write("    div ebx                 ; EDX:EAX / EBX = EAX remainder EDX\n")
        wf.write("    push dx                 ; push the digit in DL (LIFO)\n")
        wf.write("    add cl,1                ; = inc cl (digit counter)\n")
        wf.write("    or  eax, eax            ; AX == 0?\n")
        wf.write("    jnz @B                  ; no: once more (jump to the first @@ above)\n")
        wf.write("  @@:                       ; Second loop: load the remainders in reversed order\n")
        wf.write("    pop ax                  ; get back pushed digits\n")
        wf.write("    or al, 00110000b        ; to ASCII\n")
        wf.write("    stosb                   ; Store AL to [EDI] (EDI is a pointer to a buffer)\n")
        wf.write("    loop @B                 ; until there are no digits left\n")
        wf.write("    mov byte ptr [edi], 0   ; ASCIIZ terminator (0)\n")
        wf.write("  .if esi == 1\n")
        wf.write("      invoke StdOut, addr negativeSign\n")
        wf.write("  .endif\n")
        wf.write("  invoke StdOut, addr decimalstr\n")
        wf.write("  invoke StdOut, addr nl\n")
        wf.write("  ret                     ; RET: EDI pointer to ASCIIZ-string\n")
        wf.write("\n")
        wf.write("  DUMP ENDP\n")
        wf.write(content["procs"])
        wf.write("end start\n")



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

#region simulate_program constants
MEM_PADDING = 1
STR_CAPACITY = 690_000
ARGS_CAPACITY = 10_000
#endregion
def simulate_program(program : Program, argv : List[str]) -> None:
    stack : List[int] = []
    return_stack : List[OpAddr] = []
    handles : List[TextIO] = []
    mem = bytearray(MEM_PADDING + program.memory_capacity + STR_CAPACITY + ARGS_CAPACITY)
    mem_buf_ptr = MEM_PADDING

    str_buf_ptr = MEM_PADDING + program.memory_capacity
    str_size = 0
    str_ptrs : Dict[int, int] = {}

    args_buf_ptr = MEM_PADDING + program.memory_capacity + STR_CAPACITY

    breakpoint = False
    show_strings = [False, 20]
    show_mem = [False, 50]
    show_args = [False, 50]

    i : int = 0
    while i < len(program.ops):
        op = program.ops[i]
        # print(stack)

        assert len(OpType) == 16, f"Exhaustive handling of operations whilst simulating {len(OpType)}"
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
                # make string null terminated
                mem[str_ptr+n+1] = 0
                str_size += n + 1
                assert str_size <= STR_CAPACITY+program.memory_capacity, "String Buffer Overflow"
            stack.append(str_ptrs[i])
            i += 1
        
        elif op.type == OpType.PUSH_MEM:
            assert isinstance(op.operand, MemAddr)
            stack.append(op.operand + mem_buf_ptr)
            i += 1

        elif op.type == OpType.SYSCALL:
            assert isinstance(op.operand, SyscallData)
            syscall = op.operand
            if syscall.name == "CreateFile":
                fileNameIdx = stack.pop()
                stack = stack[:-6]
                fileName = getStrFromAddr(fileNameIdx, mem)

                handles.append(open(fileName, "r+"))
                stack.append(len(handles)-1)

            elif syscall.name == "WriteFile":
                handleIdx = stack.pop()
                stringIdx = stack.pop()
                stack = stack[:-3]
                handle = handles[handleIdx]
                string = getStrFromAddr(stringIdx, mem)
                handle.write(string)
                stack.append(1)
            
            elif syscall.name == "ReadFile":
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

            elif syscall.name == "CloseHandle":
                handleIdx = stack.pop()
                handles[handleIdx].close()
                stack.append(1)
            elif syscall.name == "SetFilePointer":
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
            elif syscall.name == "SetEndOfFile":
                handleIdx = stack.pop()
                handle = handles[handleIdx]
                handle.truncate()
                stack.append(1)
            elif syscall.name == "GetCommandLine":
                bs = bytes("simulated_program " + " ".join(argv), "utf-8")
                n = len(bs)
                if i not in str_ptrs:
                    mem[args_buf_ptr:args_buf_ptr+n] = bs
                    assert args_buf_ptr+n <= args_buf_ptr+ARGS_CAPACITY, "String Buffer Overflow"
                stack.append(args_buf_ptr)
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

        elif op.type in [OpType.IF, OpType.ELIF]:
            a = stack.pop()
            if a == 0:
                assert isinstance(op.operand, OpAddr), "This could be a bug in the parsing step"
                i = op.operand
            else:
                i += 1


        elif op.type == OpType.ELSE:
            assert isinstance(op.operand, OpAddr), "This could be a bug in the parsing step"
            i = op.operand


        elif op.type == OpType.WHILE:
            i += 1

        elif op.type == OpType.DO:
            a = stack.pop()
            if a == 0:
                assert isinstance(op.operand, OpAddr), "This could be a bug in the parsing step"
                i = op.operand
            else:
                i += 1

        elif op.type == OpType.END:
            assert isinstance(op.operand, OpAddr), "This could be a bug in the parsing step"
            i = op.operand

        elif op.type == OpType.SKIP_PROC:
            i = op.operand.ret_ip

        elif op.type == OpType.CALL:
            return_stack.append(i + 1)
            current_proc = list(filter(lambda x : x.name == op.token.value, program.procs))[0]
            i = current_proc.ip

        elif op.type == OpType.RET:
            i = return_stack.pop()

        elif op.type == OpType.INTRINSIC:
        
            assert len(Intrinsic) == 29, f"Exaustive handling of Intrinsic's in Simulation {len(Intrinsic)}"

            if op.operand == Intrinsic.EXIT:
                exit()
                i += 1
            
            elif op.operand in [Intrinsic.CAST_INT, Intrinsic.CAST_BOOL, Intrinsic.CAST_PTR]:
                i +=1

            elif op.operand == Intrinsic.DROP:
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
            print(f"{i}: {op.token.text} {op.operand}: {stack}")
            flags = input()
            flagsLst : List[str] = flags.split(" ")
            for flag in flagsLst:
                assert isinstance(flag, str)
                if flag.startswith("s"):
                    flag = flag[1:]
                    show_strings[0] = not show_strings[0]
                    if flag.isnumeric():
                        show_strings[1] = int(flag)
                        
                elif flag.startswith("m"):
                    flag = flag[1:]
                    show_mem[0] = not show_mem[0]
                    if flag.isnumeric():
                        show_mem[1] = int(flag)
                elif flag.startswith("a"):
                    flag = flag[1:]
                    show_args[0] = not show_args[0]
                    if flag.isnumeric():
                        show_args[1] = int(flag)
            if show_strings[0]:
                print(f"strings: {mem[str_buf_ptr:str_buf_ptr + show_strings[1]]}")
            if show_mem[0]:
                print(f"mem: {mem[mem_buf_ptr:mem_buf_ptr + show_mem[1]]}")
            if show_args[0]:
                print(f"args: {mem[args_buf_ptr:args_buf_ptr + show_args[1]]}")

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
    argv : List[str] = sys.argv
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
        # type_check_program(program)
        simulate_program(program, argv)
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
                print(f"[ERROR] Invalid Path {baseDir} entered")
                exit(1)
        if timed:
            start = time.time()
        program = load_program(programPath, includePaths)
        print("[INFO] loaded program")
        # type_check_program(program)
        compile_program(program,f"{basePath}.asm")
        print(f"[INFO] Generated {basePath}.asm")
        callCmd(["ml.exe","/Fo" ,f"{basePath}.obj", "/c", "/Zd", "/coff", f"{basePath}.asm"])
        callCmd(["Link.exe",f"/OUT:{basePath}.exe", "/SUBSYSTEM:CONSOLE",  f"{basePath}.obj"])
        if timed:
            print(f"[TIME] Compile Time: {time.time() - start} secs")
            start = time.time()
        if run:
            callCmd([f"{basePath}.exe",*argv])
            if timed:
                print(f"[TIME] Run Time: {time.time()- start} secs")
    

if __name__ == "__main__":
    main()
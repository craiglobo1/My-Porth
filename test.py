import time
import numpy as np

def listBase():
    initTime = time.time()
    lst = []
    for i in range(5_000_000):
        lst.append(25)


        lst.pop()

    print(f"completed time for list base: {time.time() - initTime}")

def listWithPtr():
    initTime = time.time()
    lst = [ None for i in range(1000)]
    lstPointer = 0
    for i in range(5_000_000):
        lst[lstPointer] = 25
        lstPointer += 1


        lst[lstPointer-1] = None
        lstPointer -= 1

    print(f"completed time for with list ptr: {time.time() - initTime}")


def arrayImp():
    initTime = time.time()

    arr = np.empty((1000))
    arrPtr = 0
    for i in range(5_000_000):
        arr[arrPtr] = 25
        arrPtr += 1
        
        arr[arrPtr-1] = 0
        arrPtr -= 1

    print(f"completed time for with np arr: {time.time() - initTime}")
    # print(arr)

# listBase()
# listWithPtr()
# arrayImp()
# def twos_comp(val, bits):
#     """compute the 2's complement of int value val"""
#     if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
#         val = val - (1 << bits)        # compute negative value
#     return val       

# n1  = bin(4294967291)
# n2 =  bin(int('FFFFFFFF',16))
# print(int(n1,2)^int(n2,2))


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

print(lex_file("./test.porth"))
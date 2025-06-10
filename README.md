# Porth

**Porth** is a minimalist, stack-based programming language inspired by [Porth](https://github.com/tsoding/porth), a concatenative language created by @tsoding. This project is a Python-based interpreter built from scratch as a learning exercise in compiler and language design.

## 🚀 What is Porth?

Porth is a low-level, stack-oriented programming language that mimics the behaviour of Forth. It operates on a simple execution model where values are pushed and popped from a stack, and all computation flows through manipulating this stack.

## 📦 Features

* 🧠 **Stack-based semantics** — All operations occur by pushing/popping from a single stack
* ⚙️ **Custom-built interpreter in Python**
* 🧪 **Real-world usage via puzzle solving** — Includes solutions to [Project Euler](https://projecteuler.net/) and [Advent of Code](https://adventofcode.com/) written in Porth
* 📁 **Modular project structure** — Easy to explore and extend

## 📂 Project Structure

```
My-Porth/
├── examples/          # Sample Porth programs
├── euler/             # Project Euler solutions in Porth
├── advent_of_code/    # Advent of Code solutions
├── porth.py           # Main interpreter file
├── link.exe / ml.exe  # (Optional) Toolchain binaries for Windows
└── README.md
```

## 💡 Language Example

A simple Porth program:

```porth
10 20 + print
```

This pushes 10 and 20 to the stack, adds them, and prints the result.

## 🛠️ How to Run

1. Clone the repository:

```bash
git clone https://github.com/craiglobo1/My-Porth.git
cd My-Porth
```

2. Run a Porth program:

```bash
python3 porth.py examples/hello.porth
```

> Note: You must have Python 3 installed.

## 🎯 Learning Goals

This project was built to explore:

* Stack-based language design
* Parsing and tokenization
* Building an interpreter from scratch
* Systems-level programming and toolchain basics
* Solving complex problems using a custom language

## 🙏 Credits

* Inspired by [Porth by @tsoding](https://github.com/tsoding/porth)
* Puzzle inputs from [Project Euler](https://projecteuler.net/) and [Advent of Code](https://adventofcode.com/)

## 🧪 Future Work

* Add compiler or transpiler support
* Improve error handling and debugging
* Explore bytecode generation or WebAssembly backend

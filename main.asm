.386
.model flat, stdcall
  option casemap:none
  include C:\masm32\include\windows.inc
  include C:\masm32\include\kernel32.inc
  include C:\masm32\include\user32.inc
  include C:\masm32\include\\masm32.inc
  includelib C:\masm32\lib\kernel32.lib
  includelib C:\masm32\lib\user32.lib
  includelib C:\masm32\lib\masm32.lib
.data
    decimalstr db 16 DUP (0)  ; address to store dump values
    negativeSign db "-", 0    ; negativeSign     
    nl DWORD 10               ; new line character in ascii

.code

  start PROC
     ; -- push --
      push 34
     ; -- push --
      push 32
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
     ; -- dump --
      pop eax
      push eax
      lea edi, decimalstr
      call DUMP
     ; -- push --
      push 42
     ; -- push --
      push 2
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
     ; -- dump --
      pop eax
      push eax
      lea edi, decimalstr
      call DUMP
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
     ; -- dump --
      pop eax
      push eax
      lea edi, decimalstr
      call DUMP

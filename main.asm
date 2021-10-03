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
    aSymb db 97, 0
    negativeSign db "-", 0    ; negativeSign     
    nl DWORD 10               ; new line character in ascii
.data?
  mem db ?

.code

  start PROC
      ;-- mem --
      lea edi, mem
      push edi
     ; -- push 100 --
      push 100
     ; -- push 2 --
      push 2
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
     ; -- push 1 --
      push 1
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push 0 --
      push 0
 ; -- while --
     WHILE_8:
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push 100 --
      push 100
     ; -- push 2 --
      push 2
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO13
      push 1
      jmp END13
      ZERO13:
          push 0
      END13:
 ; -- do --
      pop eax
      cmp eax, 1
      jne END_100
     ; -- push 0 --
      push 0
 ; -- while --
     WHILE_16:
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push 100 --
      push 100
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO19
      push 1
      jmp END19
      ZERO19:
          push 0
      END19:
 ; -- do --
      pop eax
      cmp eax, 1
      jne END_43
      ; -- duplicate --
      pop eax
      push eax
      push eax
      ;-- mem --
      lea edi, mem
      push edi
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
 ; -- if --
      pop eax
      cmp eax, 1
      jne NEXT32
      ;-- mem --
      lea edi, mem
      push edi
     ; -- push 100 --
      push 100
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push 42 --
      push 42
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
 ; -- else --
      jmp NEXT39
      NEXT32:
      ;-- mem --
      lea edi, mem
      push edi
     ; -- push 100 --
      push 100
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push 32 --
      push 32
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
      NEXT39:
 ; -- end --
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
     ; -- push 1 --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      jmp WHILE_16
      END_43:
 ; -- end while --
      ; -- drop --
      pop eax
      ;-- mem --
      lea edi, mem
      push edi
     ; -- push 100 --
      push 100
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push 10 --
      push 10
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
      ;-- mem --
      lea edi, mem
      push edi
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
     ; -- push 1 --
      push 1
      ;-- shl --
      pop ecx
      pop ebx
      shl ebx, cl
      push ebx
      ;-- mem --
      lea edi, mem
      push edi
     ; -- push 1 --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
      ;-- bor --
      pop eax
      pop ebx
      or ebx, eax
      push  ebx
     ; -- push 1 --
      push 1
 ; -- while --
     WHILE_62:
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push 100 --
      push 100
     ; -- push 2 --
      push 2
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO67
      push 1
      jmp END67
      ZERO67:
          push 0
      END67:
 ; -- do --
      pop eax
      cmp eax, 1
      jne END_95
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
     ; -- push 1 --
      push 1
      ;-- shl --
      pop ecx
      pop ebx
      shl ebx, cl
      push ebx
     ; -- push 7 --
      push 7
      ;-- bor --
      pop eax
      pop ebx
      and ebx, eax
      push  ebx
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
     ; -- push 1 --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ;-- mem --
      lea edi, mem
      push edi
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
      ;-- bor --
      pop eax
      pop ebx
      or ebx, eax
      push  ebx
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
      push eax
     ; -- push 110 --
      push 110
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
      ;-- shr --
      pop ecx
      pop ebx
      shr ebx, cl
      push ebx
     ; -- push 1 --
      push 1
      ;-- bor --
      pop eax
      pop ebx
      and ebx, eax
      push  ebx
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
      ;-- mem --
      lea edi, mem
      push edi
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
     ; -- push 1 --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      jmp WHILE_62
      END_95:
 ; -- end while --
      ; -- drop --
      pop eax
      ; -- drop --
      pop eax
     ; -- push 1 --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      jmp WHILE_8
      END_100:
 ; -- end while --
      ; -- drop --
      pop eax
      invoke ExitProcess, 0
  start ENDP

  DUMP PROC             ; ARG: EDI pointer to string buffer ; EAX is the number to dump ; ECX,ESI,EBX is used
    mov ecx, eax
    shr ecx, 31

    .if ecx == 1
      xor eax, 0FFFFFFFFh
      inc eax
      mov esi, 1
    .else
      mov esi,0
    .endif

    mov ebx, 10             ; Divisor = 10
    xor ecx, ecx            ; ECX=0 (digit counter)
  @@:                       ; First Loop: store the remainders
    xor edx, edx
    div ebx                 ; EDX:EAX / EBX = EAX remainder EDX
    push dx                 ; push the digit in DL (LIFO)
    add cl,1                ; = inc cl (digit counter)
    or  eax, eax            ; AX == 0?
    jnz @B                  ; no: once more (jump to the first @@ above)
  @@:                       ; Second loop: load the remainders in reversed order
    pop ax                  ; get back pushed digits
    or al, 00110000b        ; to ASCII
    stosb                   ; Store AL to [EDI] (EDI is a pointer to a buffer)
    loop @B                 ; until there are no digits left
    mov byte ptr [edi], 0   ; ASCIIZ terminator (0)
  .if esi == 1
      invoke StdOut, addr negativeSign
  .endif
  invoke StdOut, addr decimalstr
  invoke StdOut, addr nl
  ret                     ; RET: EDI pointer to ASCIIZ-string

  DUMP ENDP

end start
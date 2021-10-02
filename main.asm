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
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 72
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 101
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 108
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 108
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 111
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 44
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 32
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 87
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 111
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 114
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 108
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 100
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 10
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 1
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
      ;-- mem --
      lea edi, mem
      push edi
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
      ;-- mem --
      lea edi, mem
      push edi
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
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
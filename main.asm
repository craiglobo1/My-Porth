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
    whileCondition db 1 DUP (0)  ; address to store dump values
    negativeSign db "-", 0    ; negativeSign     
    nl DWORD 10               ; new line character in ascii

.code

  start PROC
     ; -- push --
      push 10
 ; -- while --
     WHILE_1:
      ; -- duplicate --
      pop eax
      push eax
      push eax
     ; -- push --
      push 0
     ; -- greater than --
      pop ebx
      pop eax
      .if eax > ebx
          push 1
      .else
          push 0
      .endif
 ; -- do --
      pop eax
      cmp eax, 1
      jne END_10
      ; -- duplicate --
      pop eax
      push eax
      push eax
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
     ; -- push --
      push 1
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
      jmp WHILE_1
      END_10:
 ; -- end while --
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
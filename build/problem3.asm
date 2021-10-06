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
addr_0:
     ; -- push int 13195 --
      push 13195
addr_1:
     ; -- push int 2 --
      push 2
addr_2:
 ; -- while --
addr_3:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_4:
     ; -- push int 1 --
      push 1
addr_5:
     ; -- greater than --
      pop eax
      pop ebx
      cmp eax, ebx
      jge ZERO5
      push 1
      jmp END5
      ZERO5:
          push 0
      END5:
addr_6:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_24
addr_7:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
      push eax
addr_8:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_9:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_10:
      ; -- drop --
      pop eax
addr_11:
     ; -- push int 0 --
      push 0
addr_12:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO12
      push 1
      jmp END12
      ZERO12:
          push 0
      END12:
addr_13:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_20
addr_14:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_15:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_16:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_17:
      ; -- drop --
      pop eax
addr_18:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_19:
 ; -- else --
      jmp addr_22
addr_20:
     ; -- push int 1 --
      push 1
addr_21:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_22:
      ;-- end --
addr_23:
      ;-- endwhile --
      jmp addr_2
addr_24:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_25:
      ; -- drop --
      pop eax
addr_26:
     ; -- exit --
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
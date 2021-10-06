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
     ; -- push int 0 --
      push 0
addr_1:
     ; -- push int 0 --
      push 0
addr_2:
 ; -- while --
addr_3:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_4:
     ; -- push int 1000 --
      push 1000
addr_5:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO5
      push 1
      jmp END5
      ZERO5:
          push 0
      END5:
addr_6:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_31
addr_7:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_8:
     ; -- push int 3 --
      push 3
addr_9:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_10:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_11:
      ; -- drop --
      pop eax
addr_12:
     ; -- push int 0 --
      push 0
addr_13:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO13
      push 1
      jmp END13
      ZERO13:
          push 0
      END13:
addr_14:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_15:
     ; -- push int 5 --
      push 5
addr_16:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_17:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_18:
      ; -- drop --
      pop eax
addr_19:
     ; -- push int 0 --
      push 0
addr_20:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO20
      push 1
      jmp END20
      ZERO20:
          push 0
      END20:
addr_21:
      ;-- bor --
      pop eax
      pop ebx
      or ebx, eax
      push  ebx
addr_22:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_27
addr_23:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_24:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_25:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_26:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_27:
      ;-- end --
addr_28:
     ; -- push int 1 --
      push 1
addr_29:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_30:
      ;-- endwhile --
      jmp addr_2
addr_31:
      ; -- drop --
      pop eax
addr_32:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_33:
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
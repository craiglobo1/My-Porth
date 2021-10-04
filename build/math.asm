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
     ; -- push int 34 --
      push 34
addr_1:
     ; -- push int 35 --
      push 35
addr_2:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_3:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_4:
     ; -- push int 500 --
      push 500
addr_5:
     ; -- push int 80 --
      push 80
addr_6:
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
addr_7:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_8:
     ; -- push int 10 --
      push 10
addr_9:
     ; -- push int 20 --
      push 20
addr_10:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_11:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_12:
     ; -- push int 10 --
      push 10
addr_13:
     ; -- push int 20 --
      push 20
addr_14:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO14
      push 1
      jmp END14
      ZERO14:
          push 0
      END14:
addr_15:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_16:
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
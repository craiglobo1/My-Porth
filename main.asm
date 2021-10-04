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
    str_0 db 110, 111, 116, 32, 119, 101, 108, 99, 111, 109, 101, 32, 119, 111, 114, 108, 100, 10, 0 
    str_1 db 104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100, 10, 0 
.data?
    mem db ?
.code
    start PROC
addr_0:
     ; -- push int 0 --
      push 0
addr_1:
 ; -- while --
addr_2:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_3:
     ; -- push int 10 --
      push 10
addr_4:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO4
      push 1
      jmp END4
      ZERO4:
          push 0
      END4:
addr_5:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_19
addr_6:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_7:
     ; -- push int 5 --
      push 5
addr_8:
     ; -- greater than --
      pop eax
      pop ebx
      cmp eax, ebx
      jge ZERO8
      push 1
      jmp END8
      ZERO8:
          push 0
      END8:
addr_9:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_13
addr_10:
      lea edi, str_0
      push edi
addr_11:
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
addr_12:
 ; -- else --
      jmp addr_15
addr_13:
      lea edi, str_1
      push edi
addr_14:
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
addr_15:
      ;-- end --
addr_16:
     ; -- push int 1 --
      push 1
addr_17:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_18:
      ;-- endwhile --
      jmp addr_1
addr_19:
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
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
     ; -- push int 1 --
      push 1
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
      jne addr_15
addr_6:
      ;-- mem --
      lea edi, mem
      push edi
addr_7:
     ; -- push int 21 --
      push 21
addr_8:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_9:
      ;-- mem --
      lea edi, mem
      push edi
addr_10:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_11:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_12:
     ; -- push int 1 --
      push 1
addr_13:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_14:
      ;-- endwhile --
      jmp addr_1
addr_15:
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
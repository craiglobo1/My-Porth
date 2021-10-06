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
      ;-- mem --
      lea edi, mem
      push edi
addr_1:
     ; -- push int 0 --
      push 0
addr_2:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_3:
      ;-- mem --
      lea edi, mem
      push edi
addr_4:
     ; -- push int 4 --
      push 4
addr_5:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_6:
     ; -- push int 1 --
      push 1
addr_7:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_8:
 ; -- while --
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
     ; -- push int 4000000 --
      push 4000000
addr_12:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO12
      push 1
      jmp END12
      ZERO12:
          push 0
      END12:
addr_13:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_54
addr_14:
      ;-- mem --
      lea edi, mem
      push edi
addr_15:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_16:
     ; -- push int 2 --
      push 2
addr_17:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_18:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_19:
      ; -- drop --
      pop eax
addr_20:
     ; -- push int 0 --
      push 0
addr_21:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO21
      push 1
      jmp END21
      ZERO21:
          push 0
      END21:
addr_22:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_34
addr_23:
      ;-- mem --
      lea edi, mem
      push edi
addr_24:
     ; -- push int 8 --
      push 8
addr_25:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_26:
      ;-- mem --
      lea edi, mem
      push edi
addr_27:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_28:
      ;-- mem --
      lea edi, mem
      push edi
addr_29:
     ; -- push int 8 --
      push 8
addr_30:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_31:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_32:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_33:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_34:
      ;-- end --
addr_35:
      ;-- mem --
      lea edi, mem
      push edi
addr_36:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_37:
      ;-- mem --
      lea edi, mem
      push edi
addr_38:
     ; -- push int 4 --
      push 4
addr_39:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_40:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_41:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_42:
      ;-- mem --
      lea edi, mem
      push edi
addr_43:
      ;-- mem --
      lea edi, mem
      push edi
addr_44:
     ; -- push int 4 --
      push 4
addr_45:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_46:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_47:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_48:
      ;-- mem --
      lea edi, mem
      push edi
addr_49:
     ; -- push int 4 --
      push 4
addr_50:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_51:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_52:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_53:
      ;-- endwhile --
      jmp addr_8
addr_54:
      ;-- mem --
      lea edi, mem
      push edi
addr_55:
     ; -- push int 8 --
      push 8
addr_56:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_57:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_58:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_59:
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
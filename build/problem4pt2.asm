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
     ; -- push int 100 --
      push 100
addr_1:
 ; -- while --
addr_2:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_3:
     ; -- push int 1000 --
      push 1000
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
      jne addr_59
addr_6:
     ; -- push int 100 --
      push 100
addr_7:
 ; -- while --
addr_8:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_9:
     ; -- push int 1000 --
      push 1000
addr_10:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO10
      push 1
      jmp END10
      ZERO10:
          push 0
      END10:
addr_11:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_55
addr_12:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
      push eax
addr_13:
    ;; -- mul --
    pop  eax
    pop  ebx
    mul  ebx
    push eax
addr_14:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_15:
     ; -- push int 0 --
      push 0
addr_16:
 ; -- while --
addr_17:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_18:
     ; -- push int 0 --
      push 0
addr_19:
     ; -- greater than --
      pop eax
      pop ebx
      cmp eax, ebx
      jge ZERO19
      push 1
      jmp END19
      ZERO19:
          push 0
      END19:
addr_20:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_35
addr_21:
     ; -- push int 10 --
      push 10
addr_22:
    ;; -- mul --
    pop  eax
    pop  ebx
    mul  ebx
    push eax
addr_23:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_24:
     ; -- push int 10 --
      push 10
addr_25:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_26:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_27:
      ; -- drop --
      pop eax
addr_28:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_29:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_30:
     ; -- push int 10 --
      push 10
addr_31:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_32:
      ; -- drop --
      pop eax
addr_33:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_34:
      ;-- endwhile --
      jmp addr_16
addr_35:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_36:
      ; -- drop --
      pop eax
addr_37:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
      push eax
addr_38:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO38
      push 1
      jmp END38
      ZERO38:
          push 0
      END38:
addr_39:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_49
addr_40:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_41:
      ;-- mem --
      lea edi, mem
      push edi
addr_42:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_43:
     ; -- greater than --
      pop eax
      pop ebx
      cmp eax, ebx
      jge ZERO43
      push 1
      jmp END43
      ZERO43:
          push 0
      END43:
addr_44:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_48
addr_45:
      ;-- mem --
      lea edi, mem
      push edi
addr_46:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_47:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_48:
      ;-- end --
addr_49:
      ;-- end --
addr_50:
      ; -- drop --
      pop eax
addr_51:
      ; -- drop --
      pop eax
addr_52:
     ; -- push int 1 --
      push 1
addr_53:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_54:
      ;-- endwhile --
      jmp addr_7
addr_55:
      ; -- drop --
      pop eax
addr_56:
     ; -- push int 1 --
      push 1
addr_57:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_58:
      ;-- endwhile --
      jmp addr_1
addr_59:
      ; -- drop --
      pop eax
addr_60:
      ;-- mem --
      lea edi, mem
      push edi
addr_61:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_62:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_63:
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
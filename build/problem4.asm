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
      jne addr_82
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
      jne addr_78
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
      ;-- mem --
      lea edi, mem
      push edi
addr_16:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_17:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_18:
      ;-- mem --
      lea edi, mem
      push edi
addr_19:
     ; -- push int 4 --
      push 4
addr_20:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_21:
     ; -- push int 0 --
      push 0
addr_22:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_23:
 ; -- while --
addr_24:
      ;-- mem --
      lea edi, mem
      push edi
addr_25:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_26:
     ; -- push int 0 --
      push 0
addr_27:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      je ZERO27
      push 1
      jmp END27
      ZERO27:
          push 0
      END27:
addr_28:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_49
addr_29:
      ;-- mem --
      lea edi, mem
      push edi
addr_30:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_31:
     ; -- push int 10 --
      push 10
addr_32:
      xor edx, edx
      pop ebx
      pop eax
      div ebx
      push eax
      push edx
addr_33:
      ;-- mem --
      lea edi, mem
      push edi
addr_34:
     ; -- push int 4 --
      push 4
addr_35:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_36:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_37:
     ; -- push int 10 --
      push 10
addr_38:
    ;; -- mul --
    pop  eax
    pop  ebx
    mul  ebx
    push eax
addr_39:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_40:
      ;-- mem --
      lea edi, mem
      push edi
addr_41:
     ; -- push int 4 --
      push 4
addr_42:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_43:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_44:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_45:
      ;-- mem --
      lea edi, mem
      push edi
addr_46:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_47:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_48:
      ;-- endwhile --
      jmp addr_23
addr_49:
      ;-- mem --
      lea edi, mem
      push edi
addr_50:
     ; -- push int 4 --
      push 4
addr_51:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_52:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_53:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      jne ZERO53
      push 1
      jmp END53
      ZERO53:
          push 0
      END53:
addr_54:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_74
addr_55:
      ;-- mem --
      lea edi, mem
      push edi
addr_56:
     ; -- push int 4 --
      push 4
addr_57:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_58:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_59:
      ;-- mem --
      lea edi, mem
      push edi
addr_60:
     ; -- push int 8 --
      push 8
addr_61:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_62:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_63:
     ; -- greater than --
      pop eax
      pop ebx
      cmp eax, ebx
      jge ZERO63
      push 1
      jmp END63
      ZERO63:
          push 0
      END63:
addr_64:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_73
addr_65:
      ;-- mem --
      lea edi, mem
      push edi
addr_66:
     ; -- push int 8 --
      push 8
addr_67:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_68:
      ;-- mem --
      lea edi, mem
      push edi
addr_69:
     ; -- push int 4 --
      push 4
addr_70:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_71:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_72:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_73:
      ;-- end --
addr_74:
      ;-- end --
addr_75:
     ; -- push int 1 --
      push 1
addr_76:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_77:
      ;-- endwhile --
      jmp addr_7
addr_78:
      ; -- drop --
      pop eax
addr_79:
     ; -- push int 1 --
      push 1
addr_80:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_81:
      ;-- endwhile --
      jmp addr_1
addr_82:
      ; -- drop --
      pop eax
addr_83:
      ;-- mem --
      lea edi, mem
      push edi
addr_84:
     ; -- push int 8 --
      push 8
addr_85:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_86:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_87:
      ; -- dump --
      pop eax
      lea edi, decimalstr
      call DUMP
addr_88:
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
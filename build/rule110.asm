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
     ; -- push int 100 --
      push 100
addr_2:
     ; -- push int 2 --
      push 2
addr_3:
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
addr_4:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_5:
     ; -- push int 1 --
      push 1
addr_6:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
addr_7:
     ; -- push int 0 --
      push 0
addr_8:
 ; -- while --
addr_9:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_10:
     ; -- push int 100 --
      push 100
addr_11:
     ; -- push int 2 --
      push 2
addr_12:
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
addr_13:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO13
      push 1
      jmp END13
      ZERO13:
          push 0
      END13:
addr_14:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_101
addr_15:
     ; -- push int 0 --
      push 0
addr_16:
 ; -- while --
addr_17:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_18:
     ; -- push int 100 --
      push 100
addr_19:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO19
      push 1
      jmp END19
      ZERO19:
          push 0
      END19:
addr_20:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_44
addr_21:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_22:
      ;-- mem --
      lea edi, mem
      push edi
addr_23:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_24:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
addr_25:
 ; -- if --
      pop eax
      cmp eax, 1
      jne addr_33
addr_26:
      ;-- mem --
      lea edi, mem
      push edi
addr_27:
     ; -- push int 100 --
      push 100
addr_28:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_29:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_30:
     ; -- push int 42 --
      push 42
addr_31:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
addr_32:
 ; -- else --
      jmp addr_39
addr_33:
      ;-- mem --
      lea edi, mem
      push edi
addr_34:
     ; -- push int 100 --
      push 100
addr_35:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_36:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_37:
     ; -- push int 32 --
      push 32
addr_38:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
addr_39:
      ;-- end --
addr_40:
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
addr_41:
     ; -- push int 1 --
      push 1
addr_42:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_43:
      ;-- endwhile --
      jmp addr_16
addr_44:
      ; -- drop --
      pop eax
addr_45:
      ;-- mem --
      lea edi, mem
      push edi
addr_46:
     ; -- push int 100 --
      push 100
addr_47:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_48:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_49:
     ; -- push int 10 --
      push 10
addr_50:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
addr_51:
      ;-- print --
      pop eax
      invoke StdOut, addr [eax]
addr_52:
      ;-- mem --
      lea edi, mem
      push edi
addr_53:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
addr_54:
     ; -- push int 1 --
      push 1
addr_55:
      ;-- shl --
      pop ecx
      pop ebx
      shl ebx, cl
      push ebx
addr_56:
      ;-- mem --
      lea edi, mem
      push edi
addr_57:
     ; -- push int 1 --
      push 1
addr_58:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_59:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
addr_60:
      ;-- bor --
      pop eax
      pop ebx
      or ebx, eax
      push  ebx
addr_61:
     ; -- push int 1 --
      push 1
addr_62:
 ; -- while --
addr_63:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_64:
     ; -- push int 100 --
      push 100
addr_65:
     ; -- push int 2 --
      push 2
addr_66:
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
addr_67:
     ; -- less than --
      pop eax
      pop ebx
      cmp eax, ebx
      jle ZERO67
      push 1
      jmp END67
      ZERO67:
          push 0
      END67:
addr_68:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_96
addr_69:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_70:
     ; -- push int 1 --
      push 1
addr_71:
      ;-- shl --
      pop ecx
      pop ebx
      shl ebx, cl
      push ebx
addr_72:
     ; -- push int 7 --
      push 7
addr_73:
      ;-- bor --
      pop eax
      pop ebx
      and ebx, eax
      push  ebx
addr_74:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
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
      ;-- mem --
      lea edi, mem
      push edi
addr_78:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_79:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
addr_80:
      ;-- bor --
      pop eax
      pop ebx
      or ebx, eax
      push  ebx
addr_81:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
      push eax
addr_82:
     ; -- push int 110 --
      push 110
addr_83:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_84:
      ;-- shr --
      pop ecx
      pop ebx
      shr ebx, cl
      push ebx
addr_85:
     ; -- push int 1 --
      push 1
addr_86:
      ;-- bor --
      pop eax
      pop ebx
      and ebx, eax
      push  ebx
addr_87:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_88:
      ;-- mem --
      lea edi, mem
      push edi
addr_89:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_90:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_91:
      ;-- store (.) --
      pop  eax
      pop  ebx
      mov  byte ptr [ebx], al
addr_92:
      ; -- duplicate --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_93:
     ; -- push int 1 --
      push 1
addr_94:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_95:
      ;-- endwhile --
      jmp addr_62
addr_96:
      ; -- drop --
      pop eax
addr_97:
      ; -- drop --
      pop eax
addr_98:
     ; -- push int 1 --
      push 1
addr_99:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_100:
      ;-- endwhile --
      jmp addr_8
addr_101:
      ; -- drop --
      pop eax
addr_102:
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
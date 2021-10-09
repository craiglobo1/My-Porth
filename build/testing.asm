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
    str_0 db 110, 101, 119, 102, 105, 108, 101, 50, 46, 116, 120, 116, 0 
    str_1 db 99, 108, 101, 0 
.data?
    mem db ?
.code
    start PROC
addr_0:
     ; -- sysval NULL --
      push NULL
addr_1:
     ; -- sysval FILE_ATTRIBUTE_NORMAL --
      push FILE_ATTRIBUTE_NORMAL
addr_2:
     ; -- sysval OPEN_ALWAYS --
      push OPEN_ALWAYS
addr_3:
     ; -- sysval NULL --
      push NULL
addr_4:
     ; -- sysval FILE_SHARE_READ OR FILE_SHARE_WRITE --
      push FILE_SHARE_READ OR FILE_SHARE_WRITE
addr_5:
     ; -- sysval GENERIC_READ OR GENERIC_WRITE --
      push GENERIC_READ OR GENERIC_WRITE
addr_6:
      lea edi, str_0
      push edi
addr_7:
     ; -- syscall CreateFile --
      call CreateFile
      push eax
addr_8:
      ;-- mem --
      lea edi, mem
      push edi
addr_9:
      ; -- swap --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_10:
      ;-- store32 --
      pop  eax
      pop  ebx
      mov  [ebx], eax
addr_11:
     ; -- sysval FILE_BEGIN --
      push FILE_BEGIN
addr_12:
     ; -- push int 0 --
      push 0
addr_13:
     ; -- push int 0 --
      push 0
addr_14:
      ;-- mem --
      lea edi, mem
      push edi
addr_15:
      ;-- load32 --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_16:
     ; -- syscall SetFilePointer --
      call SetFilePointer
      push eax
addr_17:
      ;-- mem --
      lea edi, mem
      push edi
addr_18:
      ;-- load32 --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_19:
     ; -- syscall SetEndOfFile --
      call SetEndOfFile
      push eax
addr_20:
     ; -- push int 0 --
      push 0
addr_21:
     ; -- push int 0 --
      push 0
addr_22:
      lea edi, str_1
      push edi
addr_23:
      ; -- duplicate (dup) --
      pop eax
      push eax
      push eax
addr_24:
 ; -- while --
addr_25:
      ; -- duplicate (dup) --
      pop eax
      push eax
      push eax
addr_26:
      ;-- load (,) --
      pop eax
      xor ebx, ebx
      mov bl, [eax]
      push ebx
addr_27:
     ; -- push int 0 --
      push 0
addr_28:
     ; -- equal --
      pop eax
      pop ebx
      cmp eax, ebx
      je ZERO28
      push 1
      jmp END28
      ZERO28:
          push 0
      END28:
addr_29:
 ; -- do --
      pop eax
      cmp eax, 1
      jne addr_33
addr_30:
     ; -- push int 1 --
      push 1
addr_31:
     ; -- add --
      pop eax
      pop ebx
      add eax, ebx
      push eax
addr_32:
      ;-- endwhile --
      jmp addr_24
addr_33:
      ; -- over --
      pop  eax
      pop  ebx
      push ebx
      push eax
      push ebx
addr_34:
     ; -- sub --
      pop ebx
      pop eax
      sub eax, ebx
      push eax
addr_35:
      ; -- swap --
      pop  eax
      pop  ebx
      push eax
      push ebx
addr_36:
      ;-- mem --
      lea edi, mem
      push edi
addr_37:
      ;-- load32 --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_38:
     ; -- syscall WriteFile --
      call WriteFile
      push eax
addr_39:
      ;-- mem --
      lea edi, mem
      push edi
addr_40:
      ;-- load32 --
      pop eax
      xor ebx, ebx
      mov ebx, [eax]
      push ebx
addr_41:
     ; -- syscall CloseHandle --
      call CloseHandle
      push eax
addr_42:
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
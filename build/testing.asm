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
    str_1 db 104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100, 10, 0 
    str_2 db 104, 101, 108, 108, 111, 32, 119, 111, 114, 108, 100, 10, 0 
.data?
    mem db ?
.code
    start PROC
addr_0:
      lea edi, str_0
      push edi
addr_1:
     pop eax
     invoke CreateFile , eax, GENERIC_READ OR GENERIC_WRITE, FILE_SHARE_READ OR FILE_SHARE_WRITE, NULL, OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL, NULL
     push eax
addr_2:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_3:
      ; -- duplicate --
      pop eax
      push eax
      push eax
addr_4:
      lea edi, str_1
      push edi
addr_5:
     ; -- push int 12 --
      push 12
addr_6:
     pop ebx
     pop edi
     pop eax
     invoke WriteFile, eax, edi, ebx, NULL, NULL
addr_7:
      lea edi, str_2
      push edi
addr_8:
     ; -- push int 12 --
      push 12
addr_9:
     pop ebx
     pop edi
     pop eax
     invoke WriteFile, eax, edi, ebx, NULL, NULL
addr_10:
     pop eax
     invoke CloseHandle, eax
addr_11:
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
@ Increase memory size from 0x140000 to 0x160000
@ Every additional character requires an additional 16 * 16 / 2 = 128 bytes of memory
@ The original font only contained ~2200 characters, which is far from enough for Chinese

arepl_202A984:
  mov r0, #0x160000
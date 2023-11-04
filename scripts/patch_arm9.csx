#!/usr/bin/env dotnet-script

// Edit arm9.bin
var arm9 = File.ReadAllBytes($"original_files/arm9.bin");

// Modify line height
EditBinary(ref arm9, 0x02D540, "10 00 A0 E3"); // mov r0, #0x10

// Increase memory size
EditBinary(ref arm9, 0x02A984, "16 08 A0 E3"); // mov r0, #0x160000
EditBinary(ref arm9, 0x02A9AC, "16 28 81 E2"); // add r2, r1, #0x160000
EditBinary(ref arm9, 0x02A9B0, "16 38 A0 E3"); // mov r3, #0x160000
EditBinary(ref arm9, 0x02E1A4, "16 38 80 E2"); // add r3, r0, #0x160000

File.WriteAllBytes($"temp_files/arm9.bin", arm9);
Console.WriteLine($"Edited: arm9.bin");

void EditBinary(ref byte[] bytes, int offset, string newHexString)
{
  var newBytes = newHexString.Split(' ').Select(x => Convert.ToByte(x, 16)).ToArray();
  Array.Copy(newBytes, 0, bytes, offset, newBytes.Length);
  Console.WriteLine($"Edited binary at 0x{offset:X06} (length: 0x{newBytes.Length:X}): {newHexString}");
}
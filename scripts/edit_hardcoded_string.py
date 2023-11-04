#!/bin/env python3
# -*- coding: UTF-8 -*-

import json

def edit_binary(original_bytes: str, offset: int, new_bytes: bytes) -> bytes:
  return original_bytes[:offset] + new_bytes + original_bytes[offset + len(new_bytes):]

if __name__ == "__main__":
  with open("temp_files/char_map.json", "r", -1, "utf8") as reader:
    char_map = json.load(reader)
  unicode_to_shift_jis = {
    i["ReplacedCharacter"]: i["OriginalCharacter"] for i in char_map
  }
  new_string = "选择春日的同行者"
  new_string_bytes = b""
  for char in new_string:
    if char in unicode_to_shift_jis:
      char = unicode_to_shift_jis[char]
    try:
      new_string_bytes += char.encode("shift-jis")
    except:
      print(char)
  new_string_bytes += b"\0" * (0x14 - len(new_string_bytes))

  with open("original_files/overlay/overlay_0012.bin", "rb") as reader:
    original_bytes = reader.read()
  
  original_bytes = edit_binary(original_bytes, 0x53B0, new_string_bytes)
  with open("temp_files/overlay_0012.bin", "wb") as writer:
    writer.write(original_bytes)
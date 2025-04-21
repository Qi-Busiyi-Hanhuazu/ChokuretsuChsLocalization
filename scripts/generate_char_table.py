import json
import os
import struct
from typing import Any, Generator

from helper import (
  CHAR_TABLE_PATH,
  CHS_TO_JPN_DICT_PATH,
  DIR_TEXT_FILES,
  get_used_characters,
)


def generate_shift_jis(used_characters: set[str]) -> Generator[tuple[int, str], Any, None]:
  for high in range(0x88, 0xA0):
    for low in range(0x40, 0xFD):
      if low == 0x7F:
        continue

      code = (high << 8) | low

      try:
        char = struct.pack(">H", code).decode("cp932")
        if char in used_characters:
          continue

      except UnicodeDecodeError:
        continue
      yield code, char


def generate_char_table(chs_to_jpn_dict: dict[str, str], json_root: str) -> dict[str, str]:
  characters = get_used_characters(json_root)
  generator = generate_shift_jis(characters)

  char_table: dict[str, str] = {}
  shift_jis_characters = set()

  def insert_char(chs_char: str):
    code, shift_jis_char = next(generator)
    while shift_jis_char in shift_jis_characters:
      code, shift_jis_char = next(generator)
    char_table[shift_jis_char] = char
    shift_jis_characters.add(shift_jis_char)

  for char in sorted(characters):
    if not 0x4E00 <= ord(char) <= 0x9FFF:
      try:
        char.encode("cp932")
        char_table[char] = char
        continue
      except UnicodeEncodeError:
        pass

    try:
      encoded = char.encode("cp932")
      if len(encoded) == 2 and encoded[0] < 0xA0:
        if char in shift_jis_characters:
          insert_char(char_table[char])
        char_table[char] = char
        shift_jis_characters.add(char)
        continue
    except UnicodeEncodeError:
      pass

    if char in chs_to_jpn_dict and chs_to_jpn_dict[char] not in shift_jis_characters:
      char_table[chs_to_jpn_dict[char]] = char
      shift_jis_characters.add(chs_to_jpn_dict[char])
      continue

    insert_char(char)

  return char_table


if __name__ == "__main__":
  with open(CHS_TO_JPN_DICT_PATH, "r", -1, "utf8") as reader:
    chs_to_jpn_dict = {k: v for k, v in json.load(reader).items() if v.encode("cp932")[0] < 0xA0}

  char_table = generate_char_table(chs_to_jpn_dict, f"{DIR_TEXT_FILES}/zh_Hans")
  os.makedirs(os.path.dirname(CHAR_TABLE_PATH), exist_ok=True)
  with open(CHAR_TABLE_PATH, "w", -1, "utf8") as writer:
    json.dump(char_table, writer, ensure_ascii=False, indent=2)
  print(f"Collected {len(char_table)} characters.")

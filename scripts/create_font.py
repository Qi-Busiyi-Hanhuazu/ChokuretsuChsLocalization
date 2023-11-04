#!/bin/env python3
# -*- coding: UTF-8 -*-

import json
import os
import re
import struct
from PIL import Image, ImageDraw, ImageFont

CHAR_CODE_START = 0
CHINESE_PUNCTUATION = "，、。！？…—：“”‘’（）％．·；～"
FULL_WIDTH_LATIN = "０１２３４５６７８９ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
UNAVAILABLE_CHARACTERS = "α＠☆♪・―「■"
CHINESE_TO_JAPANESE = {
  "·": "・",
  "—": "―",
  "，": "「",
}
NEW_CHARMAP_SIZE = 3002

def load_shift_jis_characters(original_path: str, modified_path: str):
  with open(original_path, "rb") as reader:
    unk1, file_size, unk2, unk3, unk4 = struct.unpack("<5I", reader.read(0x14))
    shift_jis_chars = list(filter(lambda x: x, struct.unpack(f">{(file_size - 0x14) // 2}H", reader.read(file_size - 0x14))))
  
  def generate_cp932():
    for high in range(0x88, 0xa0):
      for low in range(0x40, 0xfd):
        if low == 0x7f:
          continue
        code = (high << 8) | low
        try:
          struct.pack(">H", code).decode("cp932")
        except:
          continue
        yield code

  i = 1
  generator = generate_cp932()
  while i + 1 < len(shift_jis_chars) < NEW_CHARMAP_SIZE - 2:
    next_char = next(generator)
    while next_char > shift_jis_chars[i]:
      i += 1

    if shift_jis_chars[i] != next_char:
      shift_jis_chars.insert(i, next_char)
    i += 1
  
  shift_jis_chars_bytes = struct.pack(f">{len(shift_jis_chars)}H", *shift_jis_chars)
  with open(modified_path, "wb") as writer:
    writer.write(struct.pack("<5I", unk1, len(shift_jis_chars) * 2 + 4 + 0x14, unk2, unk3, unk4))
    writer.write(shift_jis_chars_bytes)
    writer.write(b"\0\0\0\0")
    writer.write(b"\0" * ((16 - writer.tell() % 16) % 16))

  return shift_jis_chars_bytes.decode("cp932").strip("\0")

def load_chinese_characters(path: str, file_name_pattern: re.Pattern | None = None, print_usage: bool = False):
  char_count = {}
  for file_name in os.listdir(path):
    if not file_name.endswith(".json"):
      continue
    if file_name_pattern and not file_name_pattern.match(file_name):
      continue
    with open(f"{path}/{file_name}", "r", -1, "utf8") as reader:
      messages = json.load(reader)
      for message in messages:
        speaker, text = message
        for char in text:
          if char in CHINESE_PUNCTUATION or char in FULL_WIDTH_LATIN or (0x4e00 <= ord(char) < 0xa000):
            char_count[char] = char_count.get(char, 0) + 1
  char_count = {
    k: char_count[k] for k in sorted(char_count.keys(), key=lambda x: char_count[x], reverse=True)
  }
  if print_usage:
    print("Character usage:\n|", end="")
    try:
      terminal_width = os.get_terminal_size().columns
    except OSError:
      terminal_width = 110
    char_per_line = (terminal_width - 10) // 9 or 1
    for i, (char, count) in enumerate(char_count.items()):
      print(f"{char}{count: 6d}", end=("|\n|" if i % char_per_line == char_per_line - 1 else "|"))
    print("")
  characters_sorted = "".join(char_count.keys())
  return characters_sorted

def create_charmap(chinese_chars: str, shift_jis_chars: str) -> list[str, any]:
  char_map = []
  char_code = CHAR_CODE_START
  chinese_chars = "".join(sorted(chinese_chars[:len(shift_jis_chars) - len(UNAVAILABLE_CHARACTERS) + len(CHINESE_TO_JAPANESE)]))
  for char in chinese_chars:
    if char in shift_jis_chars:
      next_char_code = char_code
      char_code = shift_jis_chars.index(char)
    elif char in CHINESE_TO_JAPANESE:
      next_char_code = char_code
      char_code = shift_jis_chars.index(CHINESE_TO_JAPANESE[char])
    else:
      while shift_jis_chars[char_code] in chinese_chars or shift_jis_chars[char_code] in UNAVAILABLE_CHARACTERS:
        char_code += 1
      next_char_code = char_code + 1
    if char_code >= len(shift_jis_chars):
      print(f"Waring: max char code reached, from {char}")
      break
    char_data = {
      "Position": char_code,
      "OriginalCharacter": shift_jis_chars[char_code],
      "ReplacedCharacter": char,
      "Code": struct.unpack(">H", shift_jis_chars[char_code].encode("cp932"))[0],
      "Offset": 14,
    }
    char_map.append(char_data)
    char_code = next_char_code
  
  return char_map

def create_charmap_image(char_map: dict[str, any], font: ImageFont, font_ms_gothic: ImageFont, base_image: Image, colors: list[int], output_path: str, upscale_rate: int = 1, font_x_offset: int = 0, font_y_offset: int = 0, square_image_path: str = ""):
  char_code_map = {
    x["Position"]: x["ReplacedCharacter"] for x in char_map
  }

  square_image = Image.new("RGB", (1024 * upscale_rate, 1024 * upscale_rate), (0, 0, 0))
  draw_square = ImageDraw.Draw(square_image)
  draw_square.fontmode = "L"

  for i in range(4096):
    x = i % 64
    y = i // 64
    if i in char_code_map:
      char = char_code_map[i]
      draw_square.text(((x * 16 + 7 + font_x_offset) * upscale_rate, (y * 16 + 14 + font_y_offset) * upscale_rate), char, "#fff", font_ms_gothic if char in FULL_WIDTH_LATIN else font, "ms", 0)

  palette_image = Image.new("P", (16, 16))
  palette_image.putpalette(colors)

  square_image = square_image.quantize(method=Image.Quantize.MAXCOVERAGE, palette=palette_image, dither=0)
  square_image = square_image.resize((1024, 1024))
  if square_image_path:
    square_image.save(square_image_path)
  
  e50_image = Image.new("RGB", (16, 16 * NEW_CHARMAP_SIZE), (0, 0, 0))

  for i in range(4096):
    if i * 16 >= e50_image.height:
      break
    x = i % 64
    y = i // 64

    if i in char_code_map:
      tile = square_image.crop((x * 16, y * 16, x * 16 + 16, y * 16 + 16))
    else:
      tile = base_image.crop((0, i * 16, 16, i * 16 + 16))
    e50_image.paste(tile, (0, i * 16))

  e50_image.save(output_path)

if __name__ == "__main__":
  # CHS: Chess
  # TR: Training?
  # EV: Main events
  # CA: Asahina Mikuru topics
  # CK: Koizumi Itsuki topics
  # CG: Nagato Yuki topics
  # CH: Suzumiya Haruhi topics
  # MA/MT: Main topics
  # Ref: https://dakuratsuki.web.fc2.com/capture/haruhi-chokuretsu/topic.html
  chinese_chars = load_chinese_characters("texts/zh_Hans/", None, True)
  shift_jis_chars = load_shift_jis_characters("temp_files/dat_071.bin", "temp_files/071.bin")
  char_map = create_charmap(chinese_chars, shift_jis_chars)
  with open("temp_files/char_map.json", "w", -1, "utf8") as writer:
    json.dump(char_map, writer, ensure_ascii=False, indent=2)

  base_image = Image.open("temp_files/grp_E50.png")
  font = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 14)
  font_ms_gothic = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 14)
  with open("files/16.act", "rb") as reader:
    colors = list(reader.read(768))
  with open("temp_files/E50.bin", "wb") as writer:
    writer.write(b"\0" * (16 * 16 * NEW_CHARMAP_SIZE // 2))
  create_charmap_image(char_map, font, font_ms_gothic, base_image, colors, "temp_files/E50.png", font_y_offset=-2, square_image_path="temp_files/E50_square.png")
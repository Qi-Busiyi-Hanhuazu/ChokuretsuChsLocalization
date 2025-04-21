import json
import os
import struct

from helper import CHAR_TABLE_PATH, DIR_TEMP_FONT, DIR_TEMP_IMPORT
from PIL import Image, ImageDraw, ImageFont

if __name__ == "__main__":
  with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
    char_table: dict[str, str] = json.load(reader)

  with open(f"{DIR_TEMP_FONT}/071_dat.bin", "rb") as reader:
    data = reader.read()

  unk1, file_size, unk2, unk3, unk4 = struct.unpack_from("<5I", data, 0)
  original_characters = [
    data[i : i + 2].decode("cp932") for i in range(0x14, file_size, 2) if data[i : i + 2] != b"\0\0"
  ]

  new_characters = list(char_table.keys())
  for char in original_characters:
    if 0x3040 <= ord(char) <= 0x30FF:
      continue
    if 0x4E00 <= ord(char) <= 0x9FFF:
      continue
    if char in new_characters:
      continue

    new_characters.append(char)

  new_characters.sort(key=lambda x: int.from_bytes(x.encode("cp932"), "big"))

  os.makedirs(DIR_TEMP_IMPORT, exist_ok=True)
  with open(f"{DIR_TEMP_IMPORT}/071_dat.bin", "wb") as writer:
    writer.write(struct.pack("<5I", unk1, len(new_characters) * 2 + 4 + 0x14, unk2, unk3, unk4))
    for char in new_characters:
      writer.write(char.encode("cp932").rjust(2, b"\0"))
    writer.write(b"\0\0\0\0")
    writer.write(b"\0" * ((16 - writer.tell() % 16) % 16))

  with open(f"{DIR_TEMP_FONT}/E50_grp.bin", "rb") as reader:
    original_bytes = reader.read()

  font = ImageFont.truetype("C:/Windows/Fonts/simsun.ttc", 14)
  new_bytes = bytearray()
  for char in new_characters:
    if char in original_characters and not 0x4E00 <= ord(char) <= 0x9FFF:
      index = original_characters.index(char)
      offset = index * 0x80
      new_bytes.extend(original_bytes[offset : offset + 0x80])
    else:
      tile = Image.new("L", (16, 16), 0x00)
      draw = ImageDraw.Draw(tile)
      draw.text((0, 12), f"{char_table.get(char, char)}　　黑鼠龙龟", 0xFF, font, "ls")
      tile_bytes = bytearray()
      for y in range(0, tile.height, 8):
        for x in range(0, tile.width, 8):
          for y2 in range(8):
            for x2 in range(0, 8, 2):
              pixel_1 = tile.getpixel((x + x2, y + y2)) >> 4  # type: ignore
              pixel_2 = tile.getpixel((x + x2 + 1, y + y2)) >> 4  # type: ignore
              tile_bytes.append(pixel_1 | (pixel_2 << 4))

      new_bytes.extend(tile_bytes)

  new_bytes.extend(b"\0" * 0x80)
  new_bytes.extend(b"\0" * ((0x800 - len(new_bytes) % 0x800) % 0x800))

  with open(f"{DIR_TEMP_IMPORT}/E50_grp.bin", "wb") as writer:
    writer.write(new_bytes)

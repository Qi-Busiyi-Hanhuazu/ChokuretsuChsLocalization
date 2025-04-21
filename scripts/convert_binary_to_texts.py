import io
import json
import os

from helper import (
  CONTROL_PATTERN,
  DIR_ORIGINAL_FILES,
  DIR_TEXT_FILES,
  TRASH_PATTERN,
)
from xzonn_mt_tools.helper import TranslationItem

HARDCODED_TEXTS = {
  "overlay/overlay_0012.bin": (("ハルヒ同行者選択", "ハルヒ同行者選択"),),
}


def parse_binary(
  reader: io.BufferedReader,
  sheet_name: str,
) -> list[TranslationItem]:
  output = []

  data = reader.read()
  offset = 0
  for text_from, text_to in HARDCODED_TEXTS[f"{sheet_name}.bin"]:
    bytes_from = text_from.encode("cp932")
    bytes_to = text_to.encode("cp932")
    offset = data.find(bytes_from, offset)
    if offset == -1:
      raise ValueError(f"String not found: {text_from}")

    while True:
      zero = data.find(b"\x00", offset)
      if zero == -1:
        raise ValueError(f"String not terminated: {text_from}")
      text_bytes = data[offset:zero]
      if len(text_bytes) == 0:
        offset = zero + 1
        continue

      key = f"{sheet_name.replace('/', '__')}_{offset:06x}"
      content = text_bytes.decode("cp932")
      content = CONTROL_PATTERN.sub(lambda x: f"[{x.group(0)}]", content)
      max_length = len(text_bytes) + (4 - len(text_bytes) % 4) - 1
      item: TranslationItem = {
        "offset": offset,
        "key": key,
        "original": content,
        "translation": content,
        "max_length": max_length,
      }
      if TRASH_PATTERN.search(content):
        item["trash"] = True
      output.append(item)
      if text_bytes == bytes_to:
        break
      offset = zero + 1

  return output


def convert_json_to_texts(
  input_root: str,
  json_root: str,
  language: str,
):
  ext = ".bin"
  for file_path in HARDCODED_TEXTS:
    if not os.path.exists(f"{input_root}/{file_path}"):
      continue

    output_path = f"{json_root}/{language}/{file_path.removesuffix(ext)}.json"
    sheet_name = file_path.removesuffix(ext).replace("\\", "/")

    with open(f"{input_root}/{file_path}", "rb") as reader:
      parsed = parse_binary(reader, sheet_name)

    if len(parsed) > 0:
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "w", -1, "utf8", None, "\n") as writer:
        json.dump(parsed, writer, ensure_ascii=False, indent=2)
      continue

    if os.path.exists(output_path):
      os.remove(output_path)


if __name__ == "__main__":
  convert_json_to_texts(DIR_ORIGINAL_FILES, DIR_TEXT_FILES, "ja")

import io
import json
import logging
import os

from convert_binary_to_texts import HARDCODED_TEXTS
from helper import (
  CHAR_TABLE_PATH,
  CONVERTED_CONTROL_PATTERN,
  DIR_ORIGINAL_FILES,
  DIR_TEMP_OUT,
  DIR_TEXT_FILES,
  convert_special_characters,
  load_translation_items,
)
from xzonn_mt_tools.helper import TranslationItem


def encode_binary(
  reader: io.BufferedReader,
  sheet_name: str,
  char_table: dict[str, str],
  translation_dict: dict[str, TranslationItem],
) -> str:
  def replace_characters(text: str) -> str:
    text = convert_special_characters(text)
    for key, value in char_table.items():
      text = text.replace(value, key)
    return text

  data = reader.read()
  for key, item in translation_dict.items():
    offset_str = key.rsplit("_")[-1]
    assert len(offset_str) == 6
    offset = int(offset_str, 16)

    content = translation_dict[key]["translation"]
    controls = [x[1:-1] for x in CONVERTED_CONTROL_PATTERN.findall(content)]
    content_without_controls = [replace_characters(x) for x in CONVERTED_CONTROL_PATTERN.split(content)]
    content = "".join([f"{x[0]}{x[1]}" for x in zip(controls, content_without_controls)]) + content_without_controls[-1]

    encoded_bytes = content.encode("cp932")
    if len(encoded_bytes) > item["max_length"]:
      logging.warning(f"Max length exceeded: {item['translation']}")

    encoded_bytes = encoded_bytes + b"\0" * (item["max_length"] - len(encoded_bytes))
    data = data[:offset] + encoded_bytes + data[offset + len(encoded_bytes) :]

  return data


def convert_json_from_texts(
  input_root: str,
  json_root: str,
  language: str,
  char_table: dict[str, str],
  output_root: str,
):
  ext = ".bin"
  for file_path in HARDCODED_TEXTS:
    if not os.path.exists(f"{input_root}/{file_path}"):
      continue

    sheet_name = file_path.removesuffix(ext).replace("\\", "/")
    original_json_path = f"{json_root}/ja/{sheet_name}.json"
    translation_json_path = f"{json_root}/{language}/{sheet_name}.json"
    if (
      not os.path.exists(original_json_path)
      or not os.path.exists(translation_json_path)
      or not os.path.exists(f"{input_root}/{file_path}")
    ):
      continue

    translation_dict: dict[str, TranslationItem] = load_translation_items(original_json_path, translation_json_path)

    with open(f"{input_root}/{file_path}", "rb") as reader:
      new_binary = encode_binary(reader, sheet_name, char_table, translation_dict)

    output_path = f"{output_root}/{file_path}"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as writer:
      writer.write(new_binary)


if __name__ == "__main__":
  with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
    char_table: dict[str, str] = json.load(reader)

  convert_json_from_texts(DIR_ORIGINAL_FILES, DIR_TEXT_FILES, "zh_Hans", char_table, DIR_TEMP_OUT)

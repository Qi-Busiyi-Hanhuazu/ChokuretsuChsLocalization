import io
import json
import os

from helper import (
  CHAR_TABLE_PATH,
  CONVERTED_CONTROL_PATTERN,
  DIR_TEMP_EDITED_TEXTS,
  DIR_TEMP_ORIGINAL_TEXTS,
  DIR_TEXT_FILES,
  convert_special_characters,
  load_translation_items,
)
from xzonn_mt_tools.helper import TranslationItem


def encode_json(
  reader: io.TextIOWrapper,
  sheet_name: str,
  char_table: dict[str, str],
  translation_dict: dict[str, TranslationItem],
) -> str:
  def replace_characters(text: str) -> str:
    text = convert_special_characters(text)
    for key, value in char_table.items():
      text = text.replace(value, key)
    return text

  data: list[list[str]] = json.load(reader)
  for index, (speaker, content) in enumerate(data):
    key = f"{sheet_name}_{index:04d}"
    if key in translation_dict:
      content = translation_dict[key]["translation"]
      controls = [x[1:-1] for x in CONVERTED_CONTROL_PATTERN.findall(content)]
      content_without_controls = [replace_characters(x) for x in CONVERTED_CONTROL_PATTERN.split(content)]
      content = (
        "".join([f"{x[0]}{x[1]}" for x in zip(controls, content_without_controls)]) + content_without_controls[-1]
      )
      data[index] = [speaker, content]

  return json.dumps(data, ensure_ascii=False, indent=2)


def convert_json_from_texts(
  input_root: str,
  json_root: str,
  language: str,
  char_table: dict[str, str],
  output_root: str,
):
  ext = ".json"
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(ext):
        continue

      file_path = os.path.relpath(f"{root}/{file_name}", input_root)
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

      with open(f"{input_root}/{file_path}", "r", -1, "utf8") as reader:
        new_json = encode_json(reader, sheet_name, char_table, translation_dict)

      output_path = f"{output_root}/{file_path}"
      os.makedirs(os.path.dirname(output_path), exist_ok=True)
      with open(output_path, "w", -1, "utf8") as writer:
        writer.write(new_json)


if __name__ == "__main__":
  with open(CHAR_TABLE_PATH, "r", -1, "utf8") as reader:
    char_table: dict[str, str] = json.load(reader)

  convert_json_from_texts(DIR_TEMP_ORIGINAL_TEXTS, DIR_TEXT_FILES, "zh_Hans", char_table, DIR_TEMP_EDITED_TEXTS)

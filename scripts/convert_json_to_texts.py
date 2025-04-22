import io
import json
import os

from helper import (
  CONTROL_PATTERN,
  DIR_TEMP_ORIGINAL_TEXTS,
  DIR_TEXT_FILES,
  NAME_FILTER,
  TRASH_PATTERN,
)
from xzonn_mt_tools.helper import TranslationItem


def parse_json(
  reader: io.TextIOWrapper,
  sheet_name: str,
) -> list[TranslationItem]:
  output = []

  data: list[list[str]] = json.load(reader)
  all_trash = True
  for index, (speaker, content) in enumerate(data):
    key = f"{sheet_name}_{index:04d}"
    content = CONTROL_PATTERN.sub(lambda x: f"[{x.group(0)}]", content)
    item: TranslationItem = {
      "index": index,
      "key": key,
      "original": content,
      "translation": content,
      "speaker": speaker,
    }
    if TRASH_PATTERN.search(content):
      item["trash"] = True
    else:
      all_trash = False

    output.append(item)

  if all_trash:
    return []
  return output


def convert_json_to_texts(
  input_root: str,
  json_root: str,
  language: str,
):
  ext = ".json"
  for root, dirs, files in os.walk(input_root):
    for file_name in files:
      if not file_name.endswith(ext):
        continue

      file_path = os.path.relpath(f"{root}/{file_name}", input_root)
      sheet_name = file_path.removesuffix(ext).replace("\\", "/")
      output_path = f"{json_root}/{language}/{sheet_name}.json"

      if not NAME_FILTER.match(sheet_name):
        continue

      with open(f"{input_root}/{file_path}", "r", -1, "utf8") as reader:
        parsed = parse_json(reader, sheet_name)

      if len(parsed) > 0:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", -1, "utf8", None, "\n") as writer:
          json.dump(parsed, writer, ensure_ascii=False, indent=2)
        continue

      if os.path.exists(output_path):
        os.remove(output_path)


if __name__ == "__main__":
  convert_json_to_texts(DIR_TEMP_ORIGINAL_TEXTS, DIR_TEXT_FILES, "ja")

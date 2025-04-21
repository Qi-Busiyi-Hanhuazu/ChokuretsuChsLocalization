import json
import os
import re
from typing import Any

from xzonn_mt_tools.helper import TranslationItem

DIR_ARM9_PATCH = "arm9_patch"
DIR_ORIGINAL_FILES = "original_files"
DIR_OUT = "out"
DIR_TEXT_FILES = "texts"

DIR_TEMP_EDITED_TEXTS = "temp/edited_texts"
DIR_TEMP_FONT = "temp/font"
DIR_TEMP_IMPORT = "temp/import"
DIR_TEMP_ORIGINAL_TEXTS = "temp/original_texts"
DIR_TEMP_OUT = "temp/out"

BANNER_OUT_PATH = "out/banner.bin"
BANNER_PATH = "original_files/banner.bin"
CHS_TO_JPN_DICT_PATH = "files/chs_to_jpn_dict.json"
CHAR_TABLE_PATH = "out/char_table.json"
SYMBOL_PATH = "out/symbols.txt"

TRASH_PATTERN = re.compile(
  r"^$|^[0-9a-zA-Z_ \.,!\?<>=\"\'\/\+\|\{\}&・]+$|"
  r"[\x00-\x09\x0b-\x1f\x7f\ue000-\uf8ff\uff61-\uffff]|"
  r"（仮）|ダミー|"
  r"＠、。．・：？！＿々ー―～…‘’“”（）《》「」『』－＝％☆♪|"
  r"^(?:＿々ー―～…|‘’“”（）《》「」『』－＝％☆♪|―+|\s+)$"
)
CONTROL_PATTERN = re.compile(r"[\$#][A-Za-z0-9]+")
CONVERTED_CONTROL_PATTERN = re.compile(r"\[[\$#][A-Za-z0-9]+\]")
KANA_PATTERN = re.compile(r"[\u3040-\u309F\u30A0-\u30FF]+")

# CHS: Chess
# TR: Training?
# EV: Main events
# CA: Asahina Mikuru topics
# CK: Koizumi Itsuki topics
# CG: Nagato Yuki topics
# CH: Suzumiya Haruhi topics
# MA/MT: Main topics
# Ref: https://dakuratsuki.web.fc2.com/capture/haruhi-chokuretsu/topic.html
NAME_FILTER = re.compile(
  r"^(?:overlay.+|dat_.+|"
  r"evt_(?:[A-Z]+|"
  r"CHS_.+|"
  r"CA(?:[0]\d|1[0-2])S|"
  r"CK(?:[0]\d|1[0-2])S|"
  r"CN(?:[0]\d|1[0-2])S|"
  r"CH0[0-6]S|"
  r"EV[01]_\d+S|"
  r"M[AT](?:0[0-3]|30)S|"
  r"TR\d+S"
  r"))$"
)

SPECIAL_CHARACTERS_REPLACE_DICT = {
  "-": "－",
  " ": "　",
  ",": "，",
  ".": "．",
  "%": "％",
  "=": "＝",
  "·": "・",
  "—": "一",
  "!": "！",
  "?": "？",
  "0": "０",
  "1": "１",
  "2": "２",
  "3": "３",
  "4": "４",
  "5": "５",
  "6": "６",
  "7": "７",
  "8": "８",
  "9": "９",
  "a": "ａ",
  "b": "ｂ",
  "c": "ｃ",
  "d": "ｄ",
  "e": "ｅ",
  "f": "ｆ",
  "g": "ｇ",
  "h": "ｈ",
  "i": "ｉ",
  "j": "ｊ",
  "k": "ｋ",
  "l": "ｌ",
  "m": "ｍ",
  "n": "ｎ",
  "o": "ｏ",
  "p": "ｐ",
  "q": "ｑ",
  "r": "ｒ",
  "s": "ｓ",
  "t": "ｔ",
  "u": "ｕ",
  "v": "ｖ",
  "w": "ｗ",
  "x": "ｘ",
  "y": "ｙ",
  "z": "ｚ",
  "A": "Ａ",
  "B": "Ｂ",
  "C": "Ｃ",
  "D": "Ｄ",
  "E": "Ｅ",
  "F": "Ｆ",
  "G": "Ｇ",
  "H": "Ｈ",
  "I": "Ｉ",
  "J": "Ｊ",
  "K": "Ｋ",
  "L": "Ｌ",
  "M": "Ｍ",
  "N": "Ｎ",
  "O": "Ｏ",
  "P": "Ｐ",
  "Q": "Ｑ",
  "R": "Ｒ",
  "S": "Ｓ",
  "T": "Ｔ",
  "U": "Ｕ",
  "V": "Ｖ",
  "W": "Ｗ",
  "X": "Ｘ",
  "Y": "Ｙ",
  "Z": "Ｚ",
}


def convert_special_characters(content: str) -> str:
  for k, v in SPECIAL_CHARACTERS_REPLACE_DICT.items():
    content = content.replace(k, v)
  return content


def load_translation_items(original_path: str, translation_path: str, key: str = "key") -> dict[Any, TranslationItem]:
  output = {}
  with open(original_path, "r", -1, "utf8") as reader:
    original: list[TranslationItem] = json.load(reader)

  with open(translation_path, "r", -1, "utf8") as reader:
    translation: list[TranslationItem] = json.load(reader)

  translation_dict = {item["key"]: item for item in translation}

  for item in original:
    if item.get("trash", False):
      continue
    item_key = item["key"]
    if item_key in translation_dict:
      item["translation"] = translation_dict[item_key]["translation"]
    output[item[key]] = item

  return output


def load_translation_dict(path: str) -> dict[str, str]:
  with open(path, "r", -1, "utf8") as reader:
    translation_list: list[TranslationItem] = json.load(reader)

  translations = {}
  for item_dict in translation_list:
    if item_dict.get("trash", False):
      continue
    if item_dict.get("untranslated", False) and item_dict["original"] == item_dict["translation"]:
      continue
    translations[item_dict["key"]] = item_dict["translation"]

  return translations


def get_used_characters(json_root: str) -> set[str]:
  characters = set()
  for root, dirs, files in os.walk(json_root):
    for file_name in files:
      if not file_name.endswith(".json"):
        continue

      translations = load_translation_dict(f"{root}/{file_name}")

      for key, content in translations.items():
        content = CONVERTED_CONTROL_PATTERN.sub("", content).replace("\n", "")
        if KANA_PATTERN.search(content):
          continue

        content = convert_special_characters(content)

        for char in content:
          characters.add(char)

  return characters

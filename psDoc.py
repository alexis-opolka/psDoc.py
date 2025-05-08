### psDoc is a script made to create an HTML documentation of a given powershell script
import os
from sys import argv
from bs4 import BeautifulSoup

from libs.parsers.baseParser import BaseParser
from libs.parsers.powershell import PowerShellParser

### This is the version of this script
version = "0.9"


def check_args_size(args: list[str]):
  try:
    assert len(args) == 2

    print(f"The given arguments are: {args}")
  except AssertionError as e:
    if len(args) > 2:
      print("Cannot contain more than 1 argument!")
    elif len(args) < 2:
      print("Cannot contain less than 1 argument!")
    else:
      print(f"Unrecognized error: {e}")

    exit(1)

if __name__ == "__main__":
  ### We check for the args
  check_args_size(argv)

  ### If we're here, we haven't failed the check
  file = argv[1]
  folder = "docs"
  parser = BaseParser


  if file.endswith(".ps1"):
    parser = PowerShellParser(file, version)

  parser.parse()
  html_page = parser.generate_html()

  ### Copied and adapted from: https://stackoverflow.com/questions/6150108/how-to-pretty-print-html-to-a-file-with-indentation#6167432
  soup = BeautifulSoup(html_page, features="html.parser")
  prettyHTML = soup.prettify()

  if not os.path.exists(folder):
    os.mkdir(folder)


  with open(f"{folder}/index.html", "+wt", encoding="utf-8") as fout:
    fout.write(prettyHTML)

### psDoc is a script made to create an HTML documentation of a given powershell script


### External libraries
import os

from os import path, listdir
from sys import argv
from bs4 import BeautifulSoup

### Internal libraries
from libs.parsers.baseParser import BaseParser
from libs.parsers.powershell import PowerShellParser
from libs.parsers.markdown import MarkdownParser

### Extra Libraries
from typing import Union

### This is the version of this script
version = "0.12.0"

def check_args_size(args: list[str]):
  try:
    assert len(args) > 1
    print(f"The given arguments are: {args}")

  except AssertionError as e:
    if len(args) < 2:
      print("Cannot contain less than 1 argument!")
    else:
      print(f"Unrecognized error: {e}")

    exit(1)

def main(parser: BaseParser) -> str:

  parser.parse()
  html_page = parser.generate_html()

  ### Copied and adapted from: https://stackoverflow.com/questions/6150108/how-to-pretty-print-html-to-a-file-with-indentation#6167432
  soup = BeautifulSoup(html_page, features="html.parser")
  prettyHTML = soup.prettify()

  return prettyHTML


def parse_file(file: str, out_folder: str, write_to_file: bool = True) -> Union[str,None]:
  parser = None

  for supported_extension in supported_files:
    if file.endswith(supported_extension):
      parser = supported_files[supported_extension](file, version)

  if parser is None:
    print(f"Couldn't parse the file '{file}', are you sure it's supported?")

    return

  prettyHTML = main(parser)

  if write_to_file:
    if not os.path.exists(out_folder):
      os.mkdir(out_folder)

    with open(f"{out_folder}/index.html", "+wt", encoding="utf-8") as fout:
      fout.write(prettyHTML)

  else:

    return prettyHTML


def parse_folder(folder: str, out_folder: str):
  if not os.path.exists(out_folder):
    os.mkdir(out_folder)

  README_string = ""
  links = "<ul>"

  for dir_element in listdir(folder):
    isfile = False
    isdir = False

    if path.isfile(dir_element):
      relative_path = folder + os.sep + dir_element

      isfile = True
    else:
      relative_path = folder + os.sep + dir_element + os.sep

      isdir = True

    if (relative_path in ignored) or (dir_element in ignored):

      continue

    # We should take all files and parse them
    if isfile:
      HTML = parse_file(dir_element, out_folder, False)

      _link = f"{dir_element}.html"

      if not dir_element == "README.md":
        with open(f"{out_folder}/{dir_element}.html", "wt", encoding="utf-8") as fout:
          fout.write(HTML)

        links += f"<li><a href='{_link}'>{relative_path}</a></li>"

      else:
        README_string = HTML

  links += "</ol>"

  index_string = f"""
  <!DOCTYPE html>
  <html>
    <head>
      <title> Documentation Homepage </title>
      {base_parser.html.head_dependencies}
    </head>
    <body>
      <section id="homepage-description">
        <header id="homepage-description-title"> About this project / directory </header>

        <section id="homepage-description-content"> {README_string} </section>
      </section>

      <main>
        <header> Links to files documented </header>
        {links}
      </main>
      {base_parser.html.footer}
    </body>
  </html>
  """

  with open(f"{out_folder}/index.html", "wt", encoding="utf-8") as fout:
    fout.write(index_string)


### Parameters
ignore_keyword = "--ignore"

### Supported files
supported_files = {
  ".ps1": PowerShellParser,
  ".md": MarkdownParser
}

if __name__ == "__main__":
  ### We check for the args
  check_args_size(argv)

  ### If we're here, we haven't failed the check
  file = argv[1]

  ### Elements to ignore
  ignored = []
  if ignore_keyword in argv:
    ignored = argv[argv.index(ignore_keyword)+1].strip().split(",")

    print("Elements to ignore:", ignored)

  folder = "docs"
  base_parser = BaseParser("", version)

  ### We're adding a protection against non existing paths
  if not path.exists(file):
    print("Cannot parse a path that does not exist!")

    exit(1)

  if path.isfile(file):
    parse_file(file, folder)

  if path.isdir(file):
    parse_folder(file, folder)

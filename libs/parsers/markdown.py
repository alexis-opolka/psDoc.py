from libs.parsers.baseParser import BaseParser

markdown_rendering = False

try:
  from markdown_it import MarkdownIt

  markdown_rendering = True
except ModuleNotFoundError:
  print("Markdown rendering disabled - If required, please install Markdown-it-py via pip.")

class MarkdownParser(BaseParser):

  def __init__(self, filename: str, version: str):
    super().__init__(filename, version)

    self.enabled = {
      ### MarkdownIt Parser: MarkdownIt.parse
      "markdownit": False
    }
    self.markdownit = None

    self.content = ""

    if markdown_rendering:
      self.enabled["markdownit"] = True

      ### If markdownit rendering is enabled, we enable it inside the class
      self.markdownit = MarkdownIt("commonmark")


  def parse(self):
    with open(self.file, "rt", encoding="utf-8") as fin:
      fin_readable = fin.read()

      if self.enabled["markdownit"]:
        self.content = self.markdownit.render(fin_readable)

      else:
        self.content = fin_readable

  def generate_html(self):

    return self.content

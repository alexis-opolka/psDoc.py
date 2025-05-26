
class BaseParser:
  def __init__(self, filename: str, version: str):
    self.file = filename

    ### This holds the names of all the functions
    self.function_names = []

    ### This holds the comments documenting the functions
    self.comments = {}

    ### This holds the entirety of the script
    self.other = []

    ### This is a dictionary with the function name as the key and the function definition as its value
    self.functions_dict = {}

    self.version = version


    ### we're defining utils for the HTML rendering
    self.html = HTMLUtils(version)


class HTMLUtils:
  def __init__(self, version: str):
    self.version = version

    self.footer = f"""
    <footer>
      <hr />

      <section>
        Made by <a href="https://github.com/alexis-opolka/psDoc.py">psDoc.py</a> v{self.version}.
      </section>
    </footer>
    """

    self.head_dependencies = """
    <link rel="stylesheet" href="master.css" />
    <link rel="stylesheet" href="prism/prism.css" />
    <script src="prism/prism.js"></script>
    """

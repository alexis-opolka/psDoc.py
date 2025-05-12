
class BaseParser:
  def __init__(self, filename, version):
    self.file = filename

    ### This holds the comments documenting the functions
    self.comments = {}
    ### This holds the names of all the functions
    self.function_names = []
    ### This holds the entirety of the script
    self.other = []

    ### This is a dictionary with the function name as the key and the function definition as its value
    self.functions_dict = {}

    self.version = version

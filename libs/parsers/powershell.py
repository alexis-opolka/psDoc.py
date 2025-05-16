from libs.parsers.baseParser import BaseParser


class PowerShellParser(BaseParser):

  def __init__(self, filename: str, version: str):
    super().__init__(filename, version)

    self.parsed_comment = ""

    self.is_description = False
    self.is_links = False
    self.is_components = False
    self.is_notes = False
    self.is_example = False

    self.curr_element = ""
    self.curr_text = ""

    self.functions_args = {}

  def retrieve_function_name(self, line: str) -> str:
    syntax = line.strip().split(" ")
    function_name = syntax[1].replace("{", "")

    return function_name

  def parse(self):
    global_comment = False
    consumes_comment = False
    consumes_function = False
    curr_comment = []
    curr_function = []
    curr_function_name = ""

    with open(self.file, "+rt", encoding="utf-8") as fin:
      lines = fin.readlines()

      for i in range(0, len(lines)):
        line = lines[i]
        stripped_line = line.strip()

        if stripped_line.startswith("<#"):
          if line.startswith("<# @global"):
            global_comment = True

          consumes_comment = True

        if stripped_line.startswith("#>"):
          consumes_comment = False
          curr_comment.append(line)

          if global_comment:
            self.comments.update({
              "script": curr_comment
            })

            global_comment = False
          else:
            if lines[i+1].startswith("function"):

              ### We verify if we can get the name of the function we're commenting
              curr_function_name = self.retrieve_function_name(lines[i+1])

            self.comments.update({
              curr_function_name: curr_comment
            })

          curr_comment = []

        if stripped_line.startswith("function"):
          if curr_function_name == "":
            curr_function_name = self.retrieve_function_name(line)

          self.function_names.append(curr_function_name)

          if curr_function_name not in self.comments.keys():
            self.comments.update({
              curr_function_name: ""
            })

          consumes_function = True

        if stripped_line.startswith("}") and consumes_function:
          consumes_function = False

          curr_function.append(stripped_line)


          ### We're parsing the function before putting it inside the dictionary
          self.parse_functions(curr_function_name, curr_function)
          curr_function = []


          curr_function_name = ""

        if consumes_comment:
          curr_comment.append(line)

        if consumes_function:
          curr_function.append(line)


        ### We are not part of either a function definition or a function documentation
        ### i.e. In a script, you have the actual script
        self.other.append(line)

  def generate_html(self) -> str:
    script_name_parsed = ""

    ### We parse the name and try to get the filename at the end of the path
    if "/" in self.file:
      script_name_parsed = self.file.strip().split("/")[-1]
    elif "\\" in self.file:
      script_name_parsed = self.file.strip().split("\\")[-1]
    else:
      script_name_parsed = self.file

    body_code = ""
    script_code = ""
    toc = ""

    for i in range(0, len(self.function_names)):
      function = self.function_names[i]
      code = self.functions_dict[function]

      ### We're constructing the header
      toc += f"<a href='#definition-{function}'>{function}</a><br />"

      self.__parse_comments(function)
      parsed_code = ""

      has_args = function in self.functions_args.keys()

      for code_line in code:

        parsed_code += code_line

      body_code += f"""
      <section id="definition-{function}" class="function-section">
        <header class="function-title"> {function} {f'({self.__generate_html_parameters(function)})' if has_args else ''} </header>
  
        <div class="function-content">
          <div class="description">
            {self.parsed_comment}
          </div>
  
          <hr style="width: 85%; margin: 25px" />

          <section class="code">
            <details>
              <summary> See code for {function} </summary>
  
              <div class="code">
                <pre><code class="language-powershell">{parsed_code}</code></pre>
              </div>
            </details>
          </section>
        </div>
      </section>
      """

    for script_line in self.other:
      script_code += script_line

    html_code = f"""<!DOCTYPE html>
  <html>
    <head>
      <title> Documentation of {script_name_parsed} </title>
  
      <link rel="stylesheet" href="master.css" />
      <link rel="stylesheet" href="prism/prism.css" />
      <script src="prism/prism.js" />
    </head>
    <body>
  
      <header>
        Documentation of {script_name_parsed}
      </header>
  
      <main>
        <section id="table-of-content" class="toc">
          <header>Table of contents</header>
          <section class="toc-links">
            {toc}
          </section>
        </section>

        <section id="script-description" class="global-description">
          <header class="h2">Script Description</header>
          <section>
            {self.__parse_comments("script")}
          </section>
        </section>
  
        <section class="definitions">
          <header class="h2">Functions Definitions</header>
          {body_code}
        </section>
  
        <hr />
  
        <section class="script">
          <header> Below is the entire file parsed by this script </header>
          <pre><code class="language-powershell">{script_code}</code></pre>
        </section>
  
      </main>
      <footer>
        <hr />
  
        <section>
          Made by <a href="https://github.com/alexis-opolka/psDoc.py">psDoc.py</a> v{self.version}.
        </section>
      </footer>
    </body>
  </html>
  """

    return html_code

  def clean_curr_element(self, end_element: str) -> None:
    ### Variable to know when we are inside a child element
    ### Currently does nothing
    is_child = False
    is_list = False
    indentation_count = 0

    if "```" in self.curr_text:
      is_code = False
      language = ""
      parsed_block = ""


      for line in self.curr_text.split("\n"):
        stripped_line = line.strip()

        if stripped_line.startswith("<br />"):
          stripped_line = stripped_line.replace("<br />", "")

          ### We're taking into account the possibility of a child element
          if stripped_line.startswith(4*" "):
            is_child = True
            stripped_line = stripped_line.strip()

        if stripped_line.startswith("-"):
          is_list = True
          indentation_count = self.__get_indentation(line)

          if is_list:
            parsed_block += "</ul>"

          parsed_block += f"<ul><li>{stripped_line.replace('-', '').strip()}</li>"
          continue


        if stripped_line.startswith("```"):

          if not is_code:
            is_code = True
            line = stripped_line.replace("```", "").replace("\t<br />", "")

            if line == "":
              language = "powershell"
            else:
              language = stripped_line

            parsed_block += f"<pre><code class='language-{language}'>"
          else:
            is_code = False

            parsed_block += "</pre></code>"

        else:
          ### If the line is not empty, we check to see if the line is still indented or not
          if len(line) > 0:
            if is_list and self.__get_indentation(line) <= indentation_count:
              is_list = False

              parsed_block += "</ul>"

          if is_code:
            line = stripped_line.replace("<br />", "\n")

          if not line.endswith("\n"):
            line += "\n"

          parsed_block += line

      self.curr_text = parsed_block

    self.curr_element = self.curr_element + self.curr_text + end_element
    self.parsed_comment += self.curr_element

    self.curr_element = ""
    self.curr_text = ""

  def __handle_endof_section(self):
    if self.is_description:
      self.is_description = False

      self.clean_curr_element("</p></section>")

    if self.is_components:
      self.is_components = False

      self.clean_curr_element("</ul></section>")

    if self.is_links:
      self.is_links = False

      self.clean_curr_element("</p></section>")

    if self.is_notes:
      self.is_notes = False

      self.clean_curr_element("</p></section>")

    if self.is_example:
      self.is_example = False

      self.clean_curr_element("</div></section>")

  def __handle_next_section(self, line: str) -> str:

    self.__handle_endof_section()

    if ".DESCRIPTION" in line:
      line = line.replace(".DESCRIPTION", "")
      self.is_description = True

      self.curr_element = "<section class='description'><p>"

    if ".COMPONENT" in line:
      line = line.replace(".COMPONENT", "")
      self.is_components = True

      self.curr_element = "<section class='components'><header>Related components</header><ul>"

    if ".LINK" in line:
      line = line.replace(".LINK", "")
      self.is_links = True

      self.curr_element = "<section class='links'><header>Related links</header><p>"

    if ".NOTES" in line:
      line = line.replace(".NOTES", "")
      self.is_notes = True

      self.curr_element = "<section class='notes'><header>Notes</header><p>"

    if ".EXAMPLE" in line:
      line = line.replace(".EXAMPLE", "")
      self.is_example = True

      self.curr_element = "<section class='examples'><header>Examples</header><div>"

    return line

  def __parse_comments(self, key: str, debug: bool = False) -> str:

    ### We're cleaning possible old comments
    self.parsed_comment = ""

    for comment_line in self.comments[key]:
      if debug:
        print("LINE:", comment_line)

      if "<#" in comment_line:
        comment_line = comment_line.replace("<#", "")

      if comment_line.strip().startswith(".") or comment_line.startswith("#>"):
        comment_line = self.__handle_next_section(comment_line)

      if self.is_description:
        self.curr_text += comment_line.replace("\n", "\t<br />\n")

      if self.is_components:
        if comment_line.strip() != "":

          self.curr_text += f"<li> {comment_line} </li>"

      if self.is_links:
        if comment_line.strip() == "":
          continue

        line = comment_line.strip().split(": ")

        if len(line) > 1:
          label = line[0]
          href = line[1]
        else:
          label = comment_line
          href = comment_line

        self.curr_text += f"<a href='{href}'> {label} </a><br />"

      if self.is_notes:
        self.curr_text += comment_line + "<br />"

      if self.is_example:
        self.curr_text += comment_line


    return self.parsed_comment

  def parse_functions(self, key: str, function_body: list[str], debug: bool = False) -> str:
    is_params = False
    function_args = {}
    arg_opts = ""

    def parse_parameter(arg_name: str, arg_type: str | None, arg_opts: str):
      is_optional = False

      if "=" in arg_name:
        is_optional = True

      if arg_type is None:
        _arg_type = arg_type
      else:
        _arg_type = arg_type.strip().lower()

      arg_name = arg_name.replace("$", "").strip()

      function_args[arg_name] = {
        "type": _arg_type,
        "is_optional": is_optional,
        "options": arg_opts
      }

      ### We're cleaning the arg_opts
      arg_opts = ""

    for line in function_body:
      line_stripped = line.strip()

      if line_stripped.startswith("param("):
        is_params = True

      if is_params & line_stripped.endswith(")"):
        is_params = False
        self.functions_args[key] = function_args

      if is_params:
        ### Example of a Powershell parameter string
        ### param(
        ###   [Parameter(Mandatory=$true)]
        ###   $config
        ### )

        ### If we fall on a Parameter instruction
        if line_stripped.startswith("[Parameter"):
          start_block = line_stripped.index("[")
          end_block = line_stripped.index("]")
          arg_opts = line_stripped[start_block+1:end_block]

          continue

        ### If the parameter has typing
        if line_stripped.startswith("["):
          start_block = line_stripped.index("[")
          end_block = line_stripped.index("]")
          arg_block = line_stripped.index("$")

          arg_type = line_stripped[start_block+1:end_block]
          arg_name = line_stripped[arg_block::].replace(",", "")

          ### We handle possible comment in the end line
          if "#" in arg_name:
            comment_block = line_stripped.index("#")
            arg_name = line_stripped[arg_block:comment_block]

          parse_parameter(arg_name, arg_type, arg_opts)

        ### If the parameter doesn't have typing
        if line_stripped.startswith("$"):
          arg_block = line_stripped.index("$")
          arg_name = line_stripped[arg_block::].replace(",", "").replace("$", "").strip()

          ### We handle possible comment in the end line
          if "#" in arg_name:
            comment_block = line_stripped.index("#")
            arg_name = line_stripped[arg_block:comment_block]

          parse_parameter(arg_name, None, arg_opts)

    ### At the end, we add the body to the dictionary
    self.functions_dict[key] = function_body

  def __generate_html_parameters(self, key: str) -> str:
    html = ""

    ### Early break if the function doesn't have any arguments
    if not key in self.functions_args.keys():
      return html

    for arg_key, arg_dict in self.functions_args[key].items():
      arg_type: str | None = arg_dict['type']
      is_optional = arg_dict["is_optional"]

      html += f"<span class='parameter {'parameter-optional' if is_optional else ''}'>"

      if arg_type is not None:
        html += f"<span class='parameter-type type-{arg_type}'>{arg_type}</span><span class='parameter-name'>{arg_key.strip()}</span>"
      else:
        html += f"<span class='parameter-name'>{arg_key.strip()}</span>"

      html += "</span>"

    if html.endswith(",&nbsp;</span></span>"):
      html = html[:-21] + "</span></span>"


    return html


  def __get_indentation(self, line: str):
    indentation_count = 0

    ### We're taking the indentation count as a basis to differentiate
    ### between an indented block and one outside.
    for char in line:
      if char == " ":
        indentation_count += 1
      else:
        ### At the first non-empty char encountered, we break
        break

    return indentation_count

from libs.parsers.baseParser import BaseParser


class PowerShellParser(BaseParser):

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

        if line.startswith("<#"):
          if line.startswith("<# @global"):
            global_comment = True

          consumes_comment = True

        if line.startswith("#>"):
          consumes_comment = False

          if global_comment == True:
            self.comments.update({
              "script": curr_comment
            })

            global_comment = False
          else:
            if lines[i+1].startswith("function"):

              ### We verify if we can get the name of the function we're commenting
              curr_function_name = self.retrieve_function_name(lines[i+1])

            curr_comment.append(line)
            self.comments.update({
              curr_function_name: curr_comment
            })

          curr_comment = []

        if line.startswith("function"):
          if curr_function_name == "":
            curr_function_name = self.retrieve_function_name(line)

          self.function_names.append(curr_function_name)

          if curr_function_name not in self.comments.keys():
            self.comments.update({
              curr_function_name: ""
            })

          consumes_function = True

        if line.startswith("}") and consumes_function:
          consumes_function = False

          curr_function.append(line)

          self.functions_dict[curr_function_name] = curr_function
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
      comment = self.comments[function]
      code = self.functions_dict[function]

      ### We're constructing the header
      toc += f"<a href='#definition-{function}'>{function}</a><br />"

      parsed_comment = parse_comments(comment)
      parsed_code = ""

      for code_line in code:

        parsed_code += code_line

      body_code += f"""
      <section id="definition-{function}" class="function-section">
        <header class="function-title"> {function} </header>
  
        <div class="function-content">
          <div class="description">
            {parsed_comment}
          </div>
  
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
            {parse_comments(self.comments["script"])}
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


def parse_comments(comment_list):

  parsed_comment = ""

  is_description = False
  is_links = False
  is_components = False

  curr_element = ""
  curr_text = ""

  for comment_line in comment_list:
    if "<#" in comment_line:
      comment_line = comment_line.replace("<#", "")

    if ".DESCRIPTION" in comment_line:
      comment_line = comment_line.replace(".DESCRIPTION", "")
      is_description = True

      curr_element = "<section class='description'><p>"

    if ".COMPONENT" in comment_line:
      comment_line = comment_line.replace(".COMPONENT", "")
      is_components = True

      curr_element = "<section class='components'><header>Related components</header><ul>"

    if ".LINK" in comment_line:
      comment_line = comment_line.replace(".LINK", "")
      is_links = True

      curr_element = "<section class='links'><header>Related links</header><p>"
    if comment_line == "\n" or "#>" in comment_line:
      if is_description:
        is_description = False

        curr_element = curr_element + curr_text + "</p></section>"
        parsed_comment += curr_element

        curr_element = ""
        curr_text = ""

      if is_components:
        is_components = False

        curr_element = curr_element + curr_text + "</ul></section>"
        parsed_comment += curr_element

        curr_element = ""
        curr_text = ""

      if is_links:
        is_links = False

        curr_element = curr_element + curr_text + "</p></section>"
        parsed_comment += curr_element

        curr_element = ""
        curr_text = ""

    if is_description:
      curr_text += comment_line + "<br />"

    if is_components:
      if comment_line.strip() != "":

        curr_text += f"<li> {comment_line} </li>"

    if is_links:
      if comment_line.strip() == "":
        continue

      line = comment_line.strip().split(": ")

      if len(line) > 1:
        label = line[0]
        href = line[1]
      else:
        label = comment_line
        href = comment_line

      curr_text += f"<a href='{href}'> {label} </a><br />"

  return parsed_comment

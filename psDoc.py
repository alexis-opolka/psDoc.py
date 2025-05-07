### psDoc is a script made to create an HTML documentation of a given powershell script

from sys import argv

### This is the version of this script
version = "0.4"


def checkArgsSize(args):
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

def parsePowerShellScript(file):
  comments = []
  function_names = []
  code_by_function = {}

  consumes_comment = False
  consumes_function = False

  with open(file, "+rt", encoding="utf-8") as fin:
    lines = fin.readlines()

    curr_comment = []
    curr_function = []
    curr_function_name = ""
    other = []

    for line in lines:

      if line.startswith("<#"):
        consumes_comment = True

      if line.startswith("#>"):
        consumes_comment = False

        curr_comment.append(line)
        comments.append(curr_comment)
        curr_comment = []

      if line.startswith("function"):
        syntax = line.strip().split(" ")
        function_name = syntax[1].replace("{", "")
        curr_function_name = function_name

        function_names.append(function_name)
        consumes_function = True

      if line.startswith("}") and consumes_function:
        consumes_function = False

        curr_function.append(line)

        code_by_function[curr_function_name] = curr_function
        curr_function = []

      if consumes_comment:
        curr_comment.append(line)

      if consumes_function:
        curr_function.append(line)


      ### We are not part of either a function definition or a function documentation
      ### i.e. In a script, you have the actual script
      other.append(line)

  return (function_names, comments, code_by_function, other)

def generate_html_code(script_name, functions, comments, code_dict, script):
  script_name_parsed = ""

  ### We parse the name and try to get the filename at the end of the path
  if "/" in script_name:
    script_name_parsed = script_name.strip().split("/")[-1]
  elif "\\" in script_name:
    script_name_parsed = script_name.strip().split("\\")[-1]
  else:
    script_name_parsed = script_name

  body_code = ""
  script_code = ""

  for i in range(0, len(functions)):
    function = functions[i]
    comment = comments[i]
    code = code_dict[function]

    parsed_comment = parse_comments(comment)
    parsed_code = ""

    for code_line in code:
      # code_line = code_line.replace("\n", "<br />")

      parsed_code += code_line

    body_code += f"""
    <section class="function-section">
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

  for script_line in script:
    script_code += script_line

  html_code = f"""<!DOCTYPE html>
<html>
  <head>
    <title> Documentation of {script_name_parsed} </title>

    <link rel="stylesheet" href="master.css" />
    <link rel="stylesheet" href="prism/prism.css" />
    <script src="prism/prism.js"></script>
  </head>
  <body>

    <header>
      Documentation of {script_name_parsed}
    </header>

    <main>
      {body_code}

      <hr />

      <section class="script">
        <header> Below is the entire script parsed by this script </header>
        <pre><code class="language-powershell">{script_code}</code></pre>
      </section>

    </main>
    <footer>
      <hr />

      <section>
        Made by <a href="https://github.com/alexis-opolka/psDoc.py">psDoc.py</a> v{version}.
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

if __name__ == "__main__":
  ### We check for the args
  checkArgsSize(argv)

  ### If we're here, we haven't failed the check
  file = argv[1]

  functions, comments, code_dict, script = parsePowerShellScript(file)
  html_page = generate_html_code(file, functions, comments, code_dict, script)

  with open("help/index.html", "+wt", encoding="utf-8") as fout:
    fout.write(html_page)

# UrduPy command line and Python entry points

The installed `urdupy` console script and `python -m urdupy` call the same CLI.
Use the latter to select an interpreter/environment explicitly.

```text
urdupy --help
urdupy --version
urdupy run FILE [program arguments...]
urdupy translate FILE [-o OUTPUT]
urdupy check FILE [FILE ...]
urdupy repl
```

## Run

```powershell
python -m urdupy run examples/03_functions.urdu
python -m urdupy run app.urdu -- --user "علی"
```

`run` executes top-level code without requiring a special `main` function. Program
arguments reach `sys.argv`; the script name is its first element. Script execution
uses the script directory for local import discovery, installs the Urdu importer
for its scope, and restores owned path/argument state afterward. Imports may have
ordinary lasting effects such as successful `sys.modules` entries.

Normal completion returns exit status 0. Program `SystemExit` is honored; program
errors produce a nonzero status and show the Python exception type. An argument
usage error has argparse's exit status 2. Exact diagnostic and exit cases are
tested in the implementation handoff; no exception is converted into a silent
successful run.

## Translate and check

```powershell
python -m urdupy translate hello.urdu
python -m urdupy translate hello.urdu -o hello.py
python -m urdupy check hello.urdu examples/01_conditions.urdu
```

`translate` emits the intermediate Python spelling. It does not execute the input.
Aliases such as `دکھاؤ` remain ordinary names, so the emitted source is not a
standalone script unless the caller supplies UrduPy's alias environment or makes
explicit imports/bindings. Keep it as an inspection/export tool.

`check` translates and compiles each requested file without running its top-level
code or imports. It catches syntax/translation errors; it cannot prove names will
exist or that a program's runtime behavior is correct. A failed file causes a
nonzero result. UTF-8 BOM and LF/CRLF source are handled according to the compiler
tests; output files are UTF-8.

## REPL

`repl` accepts statements and indented suites using Python-style prompts. End a
multiline block with a blank line. Expression results use ordinary Python
representation. EOF ends the session; interrupt behavior follows the console's
documented implementation. This is a small terminal REPL, without completion,
history portability, notebook integration or a custom RTL editor.

## Python embedding

```python
from urdupy.compiler import compile_urdu, translate
from urdupy.runtime import execute_source, run_path

source = "فنکشن مربع(عدد):\n    واپس عدد * عدد\nجواب = مربع(4)\n"
print(translate(source, filename="sample.urdu"))
code = compile_urdu(source, filename="sample.urdu")
namespace = execute_source(source, filename="sample.urdu")
assert namespace["جواب"] == 16
run_path("hello.urdu", args=["example"])
```

`execute_source(source, filename='<urdupy>', globals=None, *, install_importer=True)`
returns its execution dictionary. `run_path(path, args=None)` runs a file and
returns its dictionary. These execute trusted source with ordinary Python powers.
Supplying a dictionary exposes the normal consequences of namespace mutation.
Anonymous execution uses a temporary module identity; put classes/functions that
need persistent import/pickle identity in a proper imported module.

Importing `urdupy` installs no global hook. For `.py` code that imports `.urdu`:

```python
from urdupy.importer import install_importer

with install_importer():
    import my_urdu_module
```

The owned handle supports cleanup; successful imported modules retain ordinary
cache identity after the hook scope ends. See the
[language reference](language-reference.md) for import priority/package rules and
[security policy](../SECURITY.md) for the execution boundary.

# Local editor support

`vscode/` is a small VS Code language extension containing a TextMate grammar,
`.urdu` file association, comments, bracket pairs and basic colon indentation.
It builds on the editor's `source.python` grammar. No JavaScript, network access,
language server, package installation or extension publication is required.

To try it from a terminal with the VS Code command available:

```powershell
code --extensionDevelopmentPath=./editor/vscode .
```

For a persistent local install, copy the **contents of `editor/vscode`** into a
new directory `urdupy-local-0.1.0` beneath your VS Code user extensions directory,
then reload the editor. Typical locations are
`%USERPROFILE%\.vscode\extensions` on Windows and `~/.vscode/extensions` on
Linux/macOS. Remove only that directory to uninstall. If using a different
VS Code profile/product, use its actual extension directory instead.

Choose **UrduPy** in the language selector for a `.urdu` file. If Python string
or comment highlighting is absent, enable the editor's Python language grammar.
This local extension is not registered with the Marketplace; `urdupy-local` is
only a local manifest identifier and makes no public publisher claim.

The grammar highlights tokens; it does not validate the program. Highlighting
soft keywords and collision contexts is approximate, and f-string highlighting
depends on the available Python grammar. No completion, debugger, formatter,
type checker or measured RTL rendering guarantee is included. JSON parsing and
keyword-registry checks can be automated; actual editor rendering still needs
human verification in the chosen editor/font.

Use UTF-8, visible whitespace and a left-to-right code layout. Keep ASCII
punctuation and digits in syntax. Do not insert invisible direction controls to
rearrange a line. See [tutorial](../docs/tutorial.md) and
[language reference](../docs/language-reference.md).

Reference: [VS Code syntax highlighting guide](https://code.visualstudio.com/api/language-extensions/syntax-highlight-guide).

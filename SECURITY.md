# Security policy

UrduPy executes ordinary CPython code. A `.urdu` file can read files, start
processes, access the network and import installed packages with the same
permissions as its Python process. Translation, an alias dictionary and an
import hook do not create a sandbox. Run source you trust in an environment
appropriate to that program.

This checkout is a local prerelease, with no hosted security reporting service
or public support lifetime established. Report a suspected vulnerability privately
to the maintainer who supplied the checkout. Include the version, interpreter,
minimal source, observed behavior and expected behavior; omit credentials and
personal data. A public release must add an actual private reporting channel and
supported-version policy before advertising either.

Compiler/importer security issues include unexpected execution during `check`,
corrupted strings/API names, imports escaping their documented precedence, and
unrestored shared interpreter state. Ordinary behavior of an explicitly run
Python program is governed by that program's permissions. `check` compiles source;
it does not establish that running the program is safe.

Keep Python and optional libraries maintained, install from chosen trusted
sources, and review unfamiliar `.urdu` files as executable source. Optional AI
examples use synthetic data and local random weights; no credentials or model
weights belong in this repository. Preserve actual failures and report skipped
security-related checks accurately.

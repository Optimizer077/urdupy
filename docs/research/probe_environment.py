"""Offline CPython observations only; this is not an UrduPy importer or runner."""

import importlib.machinery
import io
import json
import pathlib
import platform
import sys
import tempfile
import token
import tokenize


def main():
    print("python=" + sys.version.replace("\n", " "))
    print("platform=" + platform.platform())
    print("machine=" + platform.machine())
    source = 'value = f"start {x + 1} end"\n'
    tokens = [
        (token.tok_name[item.type], item.string)
        for item in tokenize.generate_tokens(io.StringIO(source).readline)
    ]
    print("tokens=" + json.dumps(tokens, ensure_ascii=True))

    # This demonstrates the namespace precedence issue described in ADR-007.
    # Create a unique directory beside this file and remove only known children.
    base = pathlib.Path(__file__).resolve().parent
    probe_root = pathlib.Path(tempfile.mkdtemp(prefix="namespace-probe-", dir=base))
    assert probe_root.resolve().parent == base
    package_dir = probe_root / "urdu_only_package"
    package_dir.mkdir()
    initializer = package_dir / "__init__.urdu"
    initializer.write_text("marker = 1\n", encoding="utf-8")
    try:
        spec = importlib.machinery.PathFinder.find_spec(
            "urdu_only_package", [str(probe_root)]
        )
        observed = {
            "loader": None if spec.loader is None else type(spec.loader).__name__,
            "origin": spec.origin,
            "has_package_path": spec.submodule_search_locations is not None,
        }
        print("namespace_probe=" + json.dumps(observed))
    finally:
        initializer.unlink()
        package_dir.rmdir()
        probe_root.rmdir()


if __name__ == "__main__":
    main()

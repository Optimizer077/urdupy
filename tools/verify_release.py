"""Verify local wheel/sdist in disposable, dependency-free environments.

Example: python tools/verify_release.py --python python --wheel dist/FILE.whl
         --sdist dist/FILE.tar.gz --report dist/verification.json
Repeat --python to validate additional installed CPython interpreters.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from email.parser import Parser

from packaging.requirements import Requirement


ROOT = Path(__file__).resolve().parents[1]


def run(command, *, cwd=ROOT, input=None):
    result = subprocess.run(command, cwd=cwd, input=input, capture_output=True,
                            text=True, encoding="utf-8", errors="replace", timeout=180)
    if result.returncode:
        raise RuntimeError(
            f"Command failed ({result.returncode}): {command!r}\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout, result.stderr


def inspect_artifacts(wheel, sdist):
    with ZipFile(wheel) as archive:
        names = archive.namelist()
        assert "urdupy/compiler.py" in names
        assert "urdupy/runtime.py" in names
        assert "urdupy/importer.py" in names
        assert all(name.startswith("urdupy/") or ".dist-info/" in name for name in names)
        metadata = archive.read(next(name for name in names if name.endswith(".dist-info/METADATA"))).decode()
        message = Parser().parsestr(metadata)
        requirements = [Requirement(value) for value in message.get_all("Requires-Dist", [])]
        assert set(message.get_all("Provides-Extra", [])) == {"science", "ai"}
        assert requirements, "Feature dependencies are missing from the built wheel"
        assert all(r.marker is not None and not r.marker.evaluate({"extra": ""}) for r in requirements), \
            "Base wheel must have zero active runtime dependencies"
        for extra in ("science", "ai"):
            active = {r.name.lower() for r in requirements if r.marker.evaluate({"extra": extra})}
            assert {"numpy", "pillow", "opencv-python-headless"} <= active
            if extra == "ai":
                assert {"torch", "torchvision", "transformers", "matplotlib", "arabic-reshaper", "python-bidi"} <= active
        for requirement in requirements:
            if requirement.name.lower() == "torch":
                assert requirement.specifier.contains("2.14.1+cu130")
                assert requirement.specifier.contains("2.14.1+cpu")
        assert "Requires-Python: <3.16,>=3.12" in metadata
    with tarfile.open(sdist, "r:gz") as archive:
        paths = [Path(member.name).parts for member in archive.getmembers()]
        relative = {"/".join(parts[1:]) for parts in paths if len(parts) > 1}
        for required in ("pyproject.toml", "LICENSE", "urdupy/compiler.py", "urdupy/runtime.py",
                         "urdupy/cli.py", "tests/test_runtime.py", "examples/01_conditions.urdu",
                         "tools/verify_release.py", "docs/language-reference.md"):
            assert required in relative, f"sdist is missing {required}"
        assert any(name.startswith("editor/") and name.endswith(".json") for name in relative)
        assert not any(part.startswith(".venv") or part in {".runtimes", "__pycache__", ".verification"}
                       for parts in paths for part in parts)
    return {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in (wheel, sdist)}


def verify_install(interpreter, artifact, workspace, *, full_suite):
    with TemporaryDirectory(prefix="install-", dir=workspace) as directory:
        directory = Path(directory)
        environment = directory / "environment"
        run([interpreter, "-m", "venv", str(environment)])
        scripts = environment / ("Scripts" if os.name == "nt" else "bin")
        python = scripts / ("python.exe" if os.name == "nt" else "python")
        console = scripts / ("urdupy.exe" if os.name == "nt" else "urdupy")
        run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
             "--index-url", "https://pypi.org/simple", "--no-deps", str(artifact)], cwd=directory)
        output, _ = run([str(python), "-I", "-c",
            "import json,sys,importlib.util,urdupy; "
            "print(json.dumps({'python':sys.version,'file':urdupy.__file__,"
            "'version':urdupy.__version__,'language':urdupy.LANGUAGE_SPEC_VERSION,"
            "'numpy':importlib.util.find_spec('numpy') is not None,"
            "'torch':importlib.util.find_spec('torch') is not None}))"], cwd=directory)
        info = json.loads(output)
        assert Path(info["file"]).resolve().is_relative_to(environment.resolve())
        assert not info["numpy"] and not info["torch"], "Core environment unexpectedly contains AI packages"
        run([str(python), "-m", "pip", "check"], cwd=directory)
        run([str(console), "--version"], cwd=directory)
        (directory / "helper.urdu").write_text("فنکشن double(x):\n    واپس x * 2\n", encoding="utf-8")
        script = directory / "مثال.urdu"
        script.write_text("درآمد helper\nدکھاؤ(helper.double(21), 'سلام')\n", encoding="utf-8")
        output, _ = run([str(console), "run", str(script)], cwd=directory)
        assert output == "42 سلام\n", output
        run([str(console), "check", str(script)], cwd=directory)
        run([str(console), "translate", str(script), "-o", str(directory / "translated.py")], cwd=directory)
        output, _ = run([str(console), "repl"], cwd=directory, input="دکھاؤ(6 * 7)\n")
        assert "42" in output
        if full_suite:
            output, error = run([str(python), "-I", "-X", "utf8", "-m", "unittest",
                                 "discover", "-s", str(ROOT / "tests"), "-q"])
            info["suite_summary"] = (output + error).strip()
        info.update(artifact=artifact.name, status="PASS", isolated_import=True,
                    optional_libraries_absent=True, installed_console_commands=["run", "check", "translate", "repl"])
        return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", action="append", required=True, dest="interpreters")
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--sdist", type=Path, required=True)
    parser.add_argument("--report", type=Path, default=ROOT / "dist/verification.json")
    args = parser.parse_args()
    wheel, sdist = args.wheel.resolve(), args.sdist.resolve()
    hashes = inspect_artifacts(wheel, sdist)
    workspace = ROOT / ".verification"
    workspace.mkdir(exist_ok=True)
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "sha256": hashes, "runs": []}
    for interpreter in args.interpreters:
        result = verify_install(interpreter, wheel, workspace, full_suite=True)
        report["runs"].append(result)
        print(f"PASS wheel/core/installed CLI: {result['python'].splitlines()[0]}")
    result = verify_install(args.interpreters[-1], sdist, workspace, full_suite=True)
    report["runs"].append(result)
    print(f"PASS clean sdist build/install/core/CLI: {result['python'].splitlines()[0]}")
    report["status"] = "PASS"
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    checksums = "".join(f"{digest}  {name}\n" for name, digest in hashes.items())
    (wheel.parent / "SHA256SUMS").write_text(checksums, encoding="ascii")
    print(f"Report: {args.report}")


if __name__ == "__main__":
    main()

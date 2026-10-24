"""What each site is built from, and the check that keeps that list true.

Every Netlify build costs credits, so each site is built only when one of its own inputs changed: Netlify's ignore
command (tools/netlify-ignore.sh) compares the commit with the site's last build over the paths in the site's list
(energy_inputs.txt, atlas/inputs.txt, ai/inputs.txt). A list that missed a file would leave the site stale after a
change to it, so each build records every file of this repository it reads and fails if one isn't on its list:

    site_inputs.watch()                      # first thing in the build
    site_inputs.check("energy_inputs.txt")   # last: every file read must be on the list

A list holds paths from the repository's root, one per line; a path ending in / covers everything under it, and #
starts a comment. Only files git tracks count (an untracked file can't change between two commits).
Standard library only.
"""
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
_read = set()


def watch():
    """Record every file of the repository the build opens for reading from here on."""
    root = str(REPO) + os.sep

    def hook(event, args):
        if event != "open" or not args or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        mode = args[1] if len(args) > 1 else "r"
        if isinstance(mode, str) and any(c in mode for c in "wax+"):
            return
        path = os.path.realpath(os.fsdecode(args[0]))
        if path.startswith(root):
            _read.add(Path(path).relative_to(REPO).as_posix())

    sys.addaudithook(hook)


def entries(list_name):
    """The paths on a site's list."""
    lines = (REPO / list_name).read_text(encoding="utf-8").splitlines()
    return [line.split("#", 1)[0].strip() for line in lines if line.split("#", 1)[0].strip()]


def check(list_name):
    """Fail the build if it read a tracked file that its list doesn't cover."""
    read = set(_read)  # what the build read, before this reads the list itself
    try:
        tracked = set(subprocess.run(["git", "ls-files", "-z"], cwd=REPO, capture_output=True, check=True)
                      .stdout.decode("utf-8").split("\0"))
    except (OSError, subprocess.CalledProcessError):
        print(f"WARNING: git isn't available, so the build's reads weren't checked against {list_name}")
        return
    listed = entries(list_name)
    missed = sorted(p for p in read & tracked
                    if not any(p == e or (e.endswith("/") and p.startswith(e)) for e in listed))
    if missed:
        sys.exit(f"ERROR: the build read {', '.join(missed)}, which {list_name} doesn't list; add "
                 f"{'them' if len(missed) > 1 else 'it'} there, or Netlify won't rebuild the site when "
                 f"{'they change' if len(missed) > 1 else 'it changes'}")

#!/usr/bin/env bash
# Netlify's ignore command for the sites built from this repository (netlify.toml, atlas/netlify.toml,
# ai/netlify.toml). Every build and deploy costs Netlify credits, so a site is built only when one of its own inputs
# changed since its last build:
#
#     bash tools/netlify-ignore.sh <list>      e.g. energy_inputs.txt, atlas/inputs.txt (paths from the repository's root)
#
# Netlify cancels the build when this exits 0 and builds on any other exit. It builds whenever it can't tell: on a
# project's first build, on a retry or "Clear cache and deploy" of the same commit (Netlify then gives the same commit
# as both refs), or when git can't compare the two. Each build checks that its list covers every file it reads
# (site_inputs.py), so the list can't fall behind the build.
set -u
root=$(git rev-parse --show-toplevel 2>/dev/null) || { echo "netlify-ignore: not in a git checkout; building"; exit 1; }
list="$root/${1:?usage: netlify-ignore.sh <list>}"
[ -f "$list" ] || { echo "netlify-ignore: $1 not found; building"; exit 1; }
from=${CACHED_COMMIT_REF:-}
to=${COMMIT_REF:-}
if [ -z "$from" ] || [ -z "$to" ] || [ "$from" = "$to" ]; then
  echo "netlify-ignore: no earlier build to compare with; building"
  exit 1
fi
paths=()
while IFS= read -r line; do
  line=${line%%#*}
  line=$(printf '%s' "$line" | tr -d '[:space:]')
  [ -n "$line" ] && paths+=("$line")
done < "$list"
git -C "$root" diff --quiet "$from" "$to" -- "${paths[@]}"
case $? in
  0) echo "netlify-ignore: nothing on $1 changed between ${from:0:7} and ${to:0:7}; skipping the build"; exit 0 ;;
  1) echo "netlify-ignore: $1 changed between ${from:0:7} and ${to:0:7}:"
     git -C "$root" diff --name-only "$from" "$to" -- "${paths[@]}" | head -20 | sed 's/^/  /'
     exit 1 ;;
  *) echo "netlify-ignore: couldn't compare ${from:0:7} with ${to:0:7}; building"; exit 1 ;;
esac

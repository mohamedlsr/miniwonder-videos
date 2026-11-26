#!/usr/bin/env bash
# Usage: tools/stage_upload.sh <upload-video|upload-short> <file> [<file> ...]
# Force-pushes ONE orphan commit holding the files to the given branch, then prints raw download URLs.
# The branch is overwritten on every run, so old videos never pile up in the repository.
# (Branch deletion is not allowed from Claude sessions; overwriting is.)
set -euo pipefail
BR="$1"; shift
case "$BR" in upload-video|upload-short) ;; *) echo "branch must be upload-video or upload-short" >&2; exit 1;; esac
TMP="$(mktemp -d)"
git -C "$TMP" init -q
git -C "$TMP" remote add origin https://github.com/mohamedlsr/miniwonder-videos
for f in "$@"; do cp "$f" "$TMP/"; done
git -C "$TMP" add -A
git -C "$TMP" -c user.name="mohamedlsr" -c user.email="mohamedlsr@users.noreply.github.com" commit -qm "Fichiers temporaires pour publication YouTube"
git -C "$TMP" push -q -f origin "HEAD:refs/heads/$BR" 2>&1 | grep -vE "GH001|git-lfs|pull request|^remote: *$" || true
for f in "$@"; do
  url="https://raw.githubusercontent.com/mohamedlsr/miniwonder-videos/$BR/$(basename "$f")"
  # wait until GitHub serves the new file
  for i in $(seq 1 30); do
    code=$(curl -s -o /dev/null -w "%{http_code}" -r 0-0 "$url" || true)
    [ "$code" = "206" ] || [ "$code" = "200" ] && break; sleep 4
  done
  echo "$url"
done
rm -rf "$TMP"

#!/usr/bin/env bash
# Installs (or removes) the ida_zh_cn plugin for IDA Pro 9.x on macOS / Linux.
#
# Copies plugin/ida_zh_cn.py and plugin/zh_cn.json into IDA's *user* plugin
# directory. Nothing inside the IDA install directory is touched.
#
# Default target: $IDAUSR/plugins   if the IDAUSR environment variable is set,
#                  $HOME/.idapro/plugins   otherwise.
#
# Usage:
#   ./install.sh                       # install
#   ./install.sh --uninstall           # remove
#   ./install.sh --target /some/path   # install to a custom user dir's plugins/
#
set -euo pipefail

target=""
uninstall=0

while [ $# -gt 0 ]; do
  case "$1" in
    --target)
      target="$2"
      shift 2
      ;;
    --target=*)
      target="${1#--target=}"
      shift
      ;;
    --uninstall)
      uninstall=1
      shift
      ;;
    -h|--help)
      sed -n '2,17p' "$0"
      exit 0
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

if [ -z "$target" ]; then
  if [ -n "${IDAUSR:-}" ]; then
    first="${IDAUSR%%:*}"
    target="$first/plugins"
  else
    target="$HOME/.idapro/plugins"
  fi
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
src="$script_dir/plugin"
files=(ida_zh_cn.py zh_cn.json)

if [ "$uninstall" -eq 1 ]; then
  for f in "${files[@]}" ida_zh_cn.conf.json ida_zh_cn_missing.txt; do
    p="$target/$f"
    if [ -e "$p" ]; then
      rm -f "$p"
      echo "removed  $p"
    fi
  done
  echo
  echo "Uninstalled. (zh_cn_user.json, if you made one, was left in place.)"
  exit 0
fi

for f in "${files[@]}"; do
  if [ ! -f "$src/$f" ]; then
    echo "missing $src/$f -- run this script from a full checkout" >&2
    exit 1
  fi
done

mkdir -p "$target"
for f in "${files[@]}"; do
  cp -f "$src/$f" "$target/$f"
  echo "copied   $f"
done

cat <<EOF

Installed to: $target

Next step -- pick one:
  1) Restart IDA. The plugin loads by itself.
  2) Without restarting: in IDA press Alt+F7 (File > Script file...) and choose
       $target/ida_zh_cn.py

Switch back to English any time:  Edit > Plugins > "中文界面 开/关"
EOF

#!/usr/bin/env sh
set -e
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ ! -f "$SCRIPT_DIR/bin/gtw" ]; then
  tmpdir="$(mktemp -d)"
  tarball="https://github.com/PeterHdd/Git-Worktree-Visualizer/archive/refs/heads/main.tar.gz"
  /usr/bin/curl -fsSL "$tarball" | /usr/bin/tar -xz -C "$tmpdir"
  repo_dir="$(find "$tmpdir" -maxdepth 1 -type d -name 'Git-Worktree-Visualizer-*' | head -n 1)"
  if [ -z "$repo_dir" ]; then
    echo "failed to download repo" >&2
    exit 1
  fi
  sh "$repo_dir/install.sh"
  rm -rf "$tmpdir"
  exit 0
fi
PREFIX=${PREFIX:-"$HOME/.local"}
LIBDIR=${LIBDIR:-"$PREFIX/lib/git-worktree-visualizer"}
mkdir -p "$PREFIX/bin" "$LIBDIR"
rm -rf "$LIBDIR/gtw"
cp "$SCRIPT_DIR/bin/gtw" "$PREFIX/bin/gtw"
cp "$SCRIPT_DIR/gtw.py" "$LIBDIR/gtw.py"
cp -R "$SCRIPT_DIR/gtw" "$LIBDIR/gtw"
chmod +x "$PREFIX/bin/gtw" "$LIBDIR/gtw.py"

shell=${SHELL##*/}
if [ "$shell" = "zsh" ]; then
  rc="$HOME/.zshrc"
elif [ "$shell" = "bash" ]; then
  rc="$HOME/.bashrc"
else
  rc=""
fi

if [ -n "$rc" ] && ! grep -q "gtw shell-init" "$rc" 2>/dev/null; then
  printf '\n# git worktree visualizer\n' >> "$rc"
  printf 'eval "$(gtw shell-init %s)"\n' "$shell" >> "$rc"
fi

echo "installed to $PREFIX/bin/gtw"
if [ -n "$rc" ]; then
  echo "shell init added to $rc"
fi

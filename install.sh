#!/usr/bin/env sh
set -e
PREFIX=${PREFIX:-"$HOME/.local"}
LIBDIR=${LIBDIR:-"$PREFIX/lib/git-worktree-visualizer"}
mkdir -p "$PREFIX/bin" "$LIBDIR"
rm -rf "$LIBDIR/gtw"
cp "$(dirname "$0")/bin/gtw" "$PREFIX/bin/gtw"
cp "$(dirname "$0")/gtw.py" "$LIBDIR/gtw.py"
cp -R "$(dirname "$0")/gtw" "$LIBDIR/gtw"
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

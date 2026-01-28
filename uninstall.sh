#!/usr/bin/env sh
set -e

PREFIX=${PREFIX:-"$HOME/.local"}
LIBDIR=${LIBDIR:-"$PREFIX/lib/git-worktree-visualizer"}

rm -f "$PREFIX/bin/gtw"
rm -rf "$LIBDIR"
rm -rf "$HOME/.config/gtw"

shell=${SHELL##*/}
if [ "$shell" = "zsh" ]; then
  rc="$HOME/.zshrc"
elif [ "$shell" = "bash" ]; then
  rc="$HOME/.bashrc"
else
  rc=""
fi

if [ -n "$rc" ] && [ -f "$rc" ]; then
  tmp="$(mktemp)"
  awk '
    BEGIN { skip=0 }
    /# git worktree visualizer/ { skip=1; next }
    skip && /gtw shell-init/ { skip=0; next }
    { print }
  ' "$rc" > "$tmp"
  mv "$tmp" "$rc"
fi

echo "gtw removed"

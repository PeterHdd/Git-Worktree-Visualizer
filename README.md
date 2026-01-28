# git-worktree-visualizer

A tiny terminal UI to create, switch, and manage Git worktrees with tmux splits.

Minimal, fast, and shell-friendly. No node, no fzf, no extras.

```
worktrees · my-repo
----------------------------------------------
main                         /repo
feature/auth                 /repo/.worktrees/feature/auth
bugfix/login                 /repo/.worktrees/bugfix/login
----------------------------------------------
↑/↓ move  enter open  c create  t tmux  r refresh  q quit
```

## Install

```bash
cd git-worktree-visualizer
./install.sh
```

### One-line install

```bash
curl -fsSL https://raw.githubusercontent.com/PeterHdd/Git-Worktree-Visualizer/main/install.sh | sh
```

### One-line uninstall

```bash
curl -fsSL https://raw.githubusercontent.com/PeterHdd/Git-Worktree-Visualizer/main/uninstall.sh | sh
```

## Usage

Open the UI:

```bash
gtw
```

Demo: https://www.youtube.com/watch?v=MN7pqxWY-Bc

Pick a worktree and press:
- `enter` to switch
- `c` to create a new worktree
- `t` to open in tmux (split panes, keeps gtw visible)

### Multi-worktree workflow

Use `t` to open a tmux split: gtw stays on the left, the selected worktree opens on the right.

### Auto-run a command in the right pane

Create `~/.config/gtw/config` with a single command to run on each split:

```bash
mkdir -p ~/.config/gtw
echo "codex" > ~/.config/gtw/config
```

You can also set `GTW_CMD` to override the config:

```bash
export GTW_CMD="codex"
```

## Why

Git worktrees are great, but jumping between them is still friction. This gives you a small, focused UI that lives entirely in the terminal and respects your shell.

## Requirements

- Python 3 (curses is in the standard library)
- Git
- tmux

## License

MIT

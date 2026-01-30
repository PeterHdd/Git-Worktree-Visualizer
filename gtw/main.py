import argparse
import os
import sys

from . import __version__
from .gitops import is_git_repo
from .shellops import shell_init
from .ui import select_worktree


def main():
    parser = argparse.ArgumentParser(description="Git worktree visualizer")
    parser.add_argument("--version", action="store_true", help="print version")
    parser.add_argument("--emit", action="store_true", help="emit a shell command")
    parser.add_argument("--out", default=None, help="write emitted command to file")
    parser.add_argument("shell_init", nargs="*", help="print shell init")
    args = parser.parse_args()

    if args.version:
        print(f"git-worktree-visualizer {__version__}")
        return 0

    if args.shell_init and args.shell_init[0] == "shell-init":
        shell = args.shell_init[1] if len(args.shell_init) > 1 else os.environ.get("SHELL", "")
        shell = os.path.basename(shell)
        print(shell_init(shell))
        return 0

    cwd = os.getcwd()
    if not is_git_repo(cwd):
        print("not a git repo", file=sys.stderr)
        return 1

    try:
        cmd = select_worktree(cwd)
    except KeyboardInterrupt:
        return 1
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.emit and args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            if cmd:
                handle.write(cmd)
        return 0

    if not cmd:
        return 0

    print(cmd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

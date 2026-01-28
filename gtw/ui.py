import os
import shlex
import subprocess
import shutil

try:
    import curses
except Exception:
    curses = None

from .config import load_default_cmd
from .gitops import (
    current_branch,
    default_branch,
    list_worktrees,
    repo_name,
    repo_root,
    run_git,
    worktree_for_branch,
)


def sh_escape(path):
    return shlex.quote(path)


def build_cd_command(path):
    return f"cd {sh_escape(path)}"


def build_tmux_command(path, session, cmd):
    if cmd:
        return f"__gtw_tmux__ {sh_escape(path)} {sh_escape(session)} {cmd}"
    return f"__gtw_tmux__ {sh_escape(path)} {sh_escape(session)}"


def close_tmux_panes_for_path(path):
    if "TMUX" not in os.environ:
        return
    tmux_bin = shutil.which("tmux")
    if not tmux_bin:
        return
    current_pane = os.environ.get("TMUX_PANE")
    try:
        output = subprocess.check_output(
            [tmux_bin, "list-panes", "-a", "-F", "#{pane_id} #{pane_current_path}"],
            text=True,
        )
    except subprocess.CalledProcessError:
        return
    target = os.path.normpath(path)
    for line in output.splitlines():
        pane_id, _, pane_path = line.partition(" ")
        if not pane_id or not pane_path:
            continue
        if os.path.normpath(pane_path) == target and pane_id != current_pane:
            subprocess.run([tmux_bin, "kill-pane", "-t", pane_id], check=False)


def prompt_input(screen, prompt, default=""):
    curses.echo()
    screen.addstr(curses.LINES - 2, 2, " " * (curses.COLS - 4))
    screen.addstr(curses.LINES - 2, 2, f"{prompt} ")
    screen.refresh()
    val = screen.getstr(curses.LINES - 2, 2 + len(prompt) + 1, 200).decode("utf-8")
    curses.noecho()
    if not val and default:
        return default
    return val


def draw(screen, title, items, index, footer):
    screen.clear()
    max_y, max_x = screen.getmaxyx()
    screen.addstr(1, 2, title[: max_x - 4], curses.A_BOLD)
    screen.hline(2, 2, "-", max_x - 4)

    list_top = 4
    list_height = max_y - 8
    start = max(0, index - list_height + 1)
    end = min(len(items), start + list_height)

    if not items:
        msg = "No worktrees found. Press c to create or q to quit."
        screen.addstr(list_top, 2, msg[: max_x - 4])
    else:
        for i in range(start, end):
            wt = items[i]
            line = f"{wt.label:<28} {wt.path}"
            attr = curses.A_REVERSE if i == index else curses.A_NORMAL
            screen.addstr(list_top + (i - start), 2, line[: max_x - 4], attr)

    screen.hline(max_y - 4, 2, "-", max_x - 4)
    screen.addstr(max_y - 3, 2, footer[: max_x - 4])
    screen.refresh()


def select_worktree(cwd):
    if curses is None:
        raise RuntimeError("curses is not available")

    worktrees = list_worktrees(cwd)
    git_cwd = None
    if worktrees:
        for wt in worktrees:
            if os.path.normpath(wt.path) != os.path.normpath(cwd):
                git_cwd = wt.path
                break
        if not git_cwd:
            git_cwd = worktrees[0].path
    else:
        git_cwd = repo_root(cwd)

    repo = repo_name(git_cwd)
    default_cmd = load_default_cmd()
    title = f"worktrees · {repo}"
    footer = "↑/↓ move  enter open  c create  t tmux  d delete  r refresh  q quit"

    def refresh():
        return list_worktrees(git_cwd)

    def inner(screen):
        nonlocal git_cwd
        try:
            curses.use_default_colors()
        except Exception:
            pass
        curses.curs_set(0)
        index = 0
        items = worktrees
        while True:
            draw(screen, title, items, index, footer)
            key = screen.getch()
            if key in (3,):  # Ctrl+C
                return None
            if key in (curses.KEY_UP, ord("k")):
                index = max(0, index - 1)
            elif key in (curses.KEY_DOWN, ord("j")):
                index = min(len(items) - 1, index + 1)
            elif key in (ord("q"), 27):
                return None
            elif key in (ord("r"),):
                items = refresh()
                index = min(index, len(items) - 1)
            elif key in (curses.KEY_ENTER, 10, 13):
                if not items:
                    continue
                return ("open", items[index])
            elif key in (ord("t"),):
                if not items:
                    continue
                return ("tmux", items[index])
            elif key in (ord("c"),):
                base = prompt_input(screen, "Base branch", current_branch(git_cwd))
                branch = prompt_input(screen, "New branch name")
                if not branch:
                    continue
                try:
                    run_git(["rev-parse", "--verify", base], git_cwd)
                except subprocess.CalledProcessError:
                    msg = f"base not found: {base}"
                    screen.addstr(curses.LINES - 2, 2, msg[: curses.COLS - 4])
                    screen.refresh()
                    screen.getch()
                    continue
                try:
                    run_git(["rev-parse", "--verify", f"refs/heads/{branch}"], git_cwd)
                    msg = f"branch exists: {branch}"
                    screen.addstr(curses.LINES - 2, 2, msg[: curses.COLS - 4])
                    screen.refresh()
                    screen.getch()
                    continue
                except subprocess.CalledProcessError:
                    pass
                default_path = os.path.join(cwd, branch)
                path = prompt_input(screen, "Path", default_path)
                try:
                    run_git(["worktree", "add", "-b", branch, path, base], git_cwd)
                except subprocess.CalledProcessError as exc:
                    msg = f"failed: {exc}"
                    screen.addstr(curses.LINES - 2, 2, msg[: curses.COLS - 4])
                    screen.refresh()
                    screen.getch()
                items = refresh()
                index = min(index, len(items) - 1)
            elif key in (ord("d"),):
                if not items:
                    continue
                wt = items[index]
                confirm = prompt_input(screen, f"Delete {wt.label}? (y/N)", "N")
                if confirm.lower() != "y":
                    continue
                is_dirty = False
                try:
                    status = run_git(["-C", wt.path, "status", "--porcelain"], git_cwd)
                    is_dirty = bool(status.strip())
                except subprocess.CalledProcessError:
                    is_dirty = False
                force = False
                if is_dirty:
                    confirm_force = prompt_input(
                        screen, "Worktree has changes. Force delete? (y/N)", "N"
                    )
                    if confirm_force.lower() != "y":
                        continue
                    force = True
                delete_current = os.path.commonpath([cwd, wt.path]) == wt.path
                other_paths = [item.path for item in items if item.path != wt.path]
                branch_git_cwd = other_paths[0] if other_paths else None
                fallback = None
                if delete_current:
                    default = default_branch(cwd)
                    fallback_wt = worktree_for_branch(items, default)
                    if fallback_wt and fallback_wt.path != wt.path:
                        fallback = fallback_wt.path
                    else:
                        for other in items:
                            if other.path != wt.path:
                                fallback = other.path
                                break
                    if not fallback:
                        fallback = os.path.dirname(wt.path)
                try:
                    args = ["worktree", "remove"]
                    if force:
                        args.append("-f")
                    args.append(wt.path)
                    run_git(args, git_cwd)
                    close_tmux_panes_for_path(wt.path)
                    if wt.branch:
                        branch_name = wt.branch.replace("refs/heads/", "")
                        if branch_git_cwd:
                            run_git(["branch", "-D", branch_name], branch_git_cwd)
                except subprocess.CalledProcessError as exc:
                    msg = f"failed: {exc}"
                    screen.addstr(curses.LINES - 2, 2, msg[: curses.COLS - 4])
                    screen.refresh()
                    screen.getch()
                if delete_current:
                    return ("open_path", fallback)
                if os.path.normpath(wt.path) == os.path.normpath(git_cwd):
                    if other_paths:
                        git_cwd = other_paths[0]
                    elif os.path.exists(cwd):
                        git_cwd = cwd
                items = refresh()
                index = min(index, len(items) - 1)
        return None

    result = curses.wrapper(inner)
    if not result:
        return None

    action, wt = result
    if action == "open":
        return build_cd_command(wt.path)
    if action == "tmux":
        return build_tmux_command(wt.path, "gtw__hub", default_cmd)
    if action == "open_path":
        return build_cd_command(wt)
    return None

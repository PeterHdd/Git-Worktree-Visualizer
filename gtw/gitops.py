import os
import subprocess


def run_git(args, cwd):
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def is_git_repo(cwd):
    try:
        run_git(["rev-parse", "--show-toplevel"], cwd)
        return True
    except Exception:
        return False


def repo_root(cwd):
    return run_git(["rev-parse", "--show-toplevel"], cwd)


def repo_name(cwd):
    root = repo_root(cwd)
    return os.path.basename(root.rstrip(os.sep))


class Worktree:
    def __init__(self, path, branch, head):
        self.path = path
        self.branch = branch
        self.head = head

    @property
    def label(self):
        if self.branch:
            return self.branch.replace("refs/heads/", "")
        return f"detached@{self.head[:7]}"


def list_worktrees(git_cwd):
    out = run_git(["worktree", "list", "--porcelain"], git_cwd)
    worktrees = []
    current = {}
    for line in out.splitlines():
        if not line.strip():
            continue
        key, _, val = line.partition(" ")
        if key == "worktree":
            if current:
                worktrees.append(Worktree(current.get("worktree"), current.get("branch"), current.get("HEAD")))
                current = {}
            current["worktree"] = val
        else:
            current[key] = val
    if current:
        worktrees.append(Worktree(current.get("worktree"), current.get("branch"), current.get("HEAD")))
    return worktrees


def default_branch(cwd):
    try:
        ref = run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd)
        return ref.rsplit("/", 1)[-1]
    except Exception:
        try:
            return run_git(["config", "--get", "init.defaultBranch"], cwd)
        except Exception:
            return "main"


def current_branch(cwd):
    try:
        return run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    except Exception:
        return default_branch(cwd)


def worktree_for_branch(worktrees, branch_name):
    target = f"refs/heads/{branch_name}"
    for wt in worktrees:
        if wt.branch == target:
            return wt
    return None

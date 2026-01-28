import os
import textwrap


def shell_init(shell):
    if shell == "zsh":
        return textwrap.dedent(
            """
            __gtw_tmux__() {
              local path="$1"
              local session="$2"
              shift 2
              local cmd="$*"
              local tmux_bin=""
              if [ -x "/opt/homebrew/bin/tmux" ]; then
                tmux_bin="/opt/homebrew/bin/tmux"
              elif [ -x "/usr/local/bin/tmux" ]; then
                tmux_bin="/usr/local/bin/tmux"
              elif command -v tmux >/dev/null 2>&1; then
                tmux_bin="tmux"
              fi
              if [ -z "$tmux_bin" ]; then
                echo "tmux not found" >&2
                return 1
              fi
              local shell_bin="/bin/zsh"
              if [ -x "$SHELL" ]; then
                shell_bin="$SHELL"
              fi
              "$tmux_bin" set-environment -g PATH "$PATH" >/dev/null 2>&1
              "$tmux_bin" set-environment -g SHELL "$shell_bin" >/dev/null 2>&1
              if [ -n "$TMUX" ]; then
                local panes dir
                panes="$("$tmux_bin" list-panes -F "#{pane_index}" | wc -l | tr -d ' ')"
                if [ "$panes" -le 1 ]; then
                  dir="h"
                else
                  dir="v"
                fi
                if [ -n "$cmd" ]; then
                  "$tmux_bin" split-window -"$dir" -c "$path" "$shell_bin" -lc "exec $cmd"
                else
                  "$tmux_bin" split-window -"$dir" -c "$path" "$shell_bin" -l
                fi
                if [ "$dir" = "h" ]; then
                  "$tmux_bin" select-pane -L
                else
                  "$tmux_bin" select-pane -U
                fi
              else
                if "$tmux_bin" has-session -t "$session" 2>/dev/null; then
                  local panes dir
                  panes="$("$tmux_bin" list-panes -t "$session:0" -F "#{pane_index}" | wc -l | tr -d ' ')"
                  if [ "$panes" -le 1 ]; then
                    dir="h"
                  else
                    dir="v"
                  fi
                  if [ -n "$cmd" ]; then
                    "$tmux_bin" split-window -"$dir" -t "$session:0" -c "$path" "$shell_bin" -lc "exec $cmd"
                  else
                    "$tmux_bin" split-window -"$dir" -t "$session:0" -c "$path" "$shell_bin" -l
                  fi
                  "$tmux_bin" select-pane -t "$session:0.0"
                  "$tmux_bin" attach -t "$session"
                  return
                fi
                "$tmux_bin" new-session -d -s "$session" -c "$path" "$shell_bin" -lc "command gtw"
                if [ -n "$cmd" ]; then
                  "$tmux_bin" split-window -h -t "$session:0" -c "$path" "$shell_bin" -lc "exec $cmd"
                else
                  "$tmux_bin" split-window -h -t "$session:0" -c "$path" "$shell_bin" -l
                fi
                "$tmux_bin" select-pane -t "$session:0.0"
                "$tmux_bin" attach -t "$session"
              fi
            }
            gtw() {
              local tmp cmd rc
              tmp="$(mktemp -t gtw.XXXXXX)" || return
              command gtw --emit --out "$tmp" "$@" </dev/tty >/dev/tty
              rc=$?
              if [ $rc -ne 0 ]; then
                rm -f "$tmp"
                return $rc
              fi
              cmd="$(cat "$tmp")"
              rm -f "$tmp"
              [ -n "$cmd" ] || return 1
              eval "$cmd"
            }
            """
        ).strip()
    if shell == "bash":
        return textwrap.dedent(
            """
            __gtw_tmux__() {
              local path="$1"
              local session="$2"
              shift 2
              local cmd="$*"
              local tmux_bin=""
              if [ -x "/opt/homebrew/bin/tmux" ]; then
                tmux_bin="/opt/homebrew/bin/tmux"
              elif [ -x "/usr/local/bin/tmux" ]; then
                tmux_bin="/usr/local/bin/tmux"
              elif command -v tmux >/dev/null 2>&1; then
                tmux_bin="tmux"
              fi
              if [ -z "$tmux_bin" ]; then
                echo "tmux not found" >&2
                return 1
              fi
              local shell_bin="/bin/zsh"
              if [ -x "$SHELL" ]; then
                shell_bin="$SHELL"
              fi
              "$tmux_bin" set-environment -g PATH "$PATH" >/dev/null 2>&1
              "$tmux_bin" set-environment -g SHELL "$shell_bin" >/dev/null 2>&1
              if [ -n "$TMUX" ]; then
                local panes dir
                panes="$("$tmux_bin" list-panes -F "#{pane_index}" | wc -l | tr -d ' ')"
                if [ "$panes" -le 1 ]; then
                  dir="h"
                else
                  dir="v"
                fi
                if [ -n "$cmd" ]; then
                  "$tmux_bin" split-window -"$dir" -c "$path" "$shell_bin" -lc "exec $cmd"
                else
                  "$tmux_bin" split-window -"$dir" -c "$path" "$shell_bin" -l
                fi
                if [ "$dir" = "h" ]; then
                  "$tmux_bin" select-pane -L
                else
                  "$tmux_bin" select-pane -U
                fi
              else
                if "$tmux_bin" has-session -t "$session" 2>/dev/null; then
                  local panes dir
                  panes="$("$tmux_bin" list-panes -t "$session:0" -F "#{pane_index}" | wc -l | tr -d ' ')"
                  if [ "$panes" -le 1 ]; then
                    dir="h"
                  else
                    dir="v"
                  fi
                  if [ -n "$cmd" ]; then
                    "$tmux_bin" split-window -"$dir" -t "$session:0" -c "$path" "$shell_bin" -lc "exec $cmd"
                  else
                    "$tmux_bin" split-window -"$dir" -t "$session:0" -c "$path" "$shell_bin" -l
                  fi
                  "$tmux_bin" select-pane -t "$session:0.0"
                  "$tmux_bin" attach -t "$session"
                  return
                fi
                "$tmux_bin" new-session -d -s "$session" -c "$path" "$shell_bin" -lc "command gtw"
                if [ -n "$cmd" ]; then
                  "$tmux_bin" split-window -h -t "$session:0" -c "$path" "$shell_bin" -lc "exec $cmd"
                else
                  "$tmux_bin" split-window -h -t "$session:0" -c "$path" "$shell_bin" -l
                fi
                "$tmux_bin" select-pane -t "$session:0.0"
                "$tmux_bin" attach -t "$session"
              fi
            }
            gtw() {
              local tmp cmd rc
              tmp="$(mktemp -t gtw.XXXXXX)" || return
              command gtw --emit --out "$tmp" "$@" </dev/tty >/dev/tty
              rc=$?
              if [ $rc -ne 0 ]; then
                rm -f "$tmp"
                return $rc
              fi
              cmd="$(cat "$tmp")"
              rm -f "$tmp"
              [ -n "$cmd" ] || return 1
              eval "$cmd"
            }
            """
        ).strip()
    raise SystemExit("unsupported shell")

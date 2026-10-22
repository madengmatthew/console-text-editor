# Mini Terminal Text Editor

A command-driven, multiline text editor written in Python for **CSC1002 Assignment 3**. It runs in a terminal and uses only the Python standard library.

中文简述：一个 Python 课程项目，通过简短命令完成多行文本编辑，练习字符串处理、正则表达式、命令解析和编辑器状态管理。

## Features

- Navigate by character, word, line, or line number.
- Insert and append text at the cursor or at either end of a line.
- Delete characters, words, whitespace spans, or entire lines.
- Swap adjacent words and reorder lines.
- Toggle ANSI character highlighting and an active-line marker.
- Display a built-in command reference with `?`.

The implementation uses functions and command dispatch tables to separate input parsing, editing operations, and display. Words are defined as runs of non-whitespace characters using regular expressions.

## Run

Requirements: Python 3 and a terminal. There are no third-party dependencies. A terminal with ANSI escape-sequence support is recommended for the green character highlight.

```sh
python3 editor.py
```

Enter one command at each `>` prompt, then press Enter. For commands that insert text, put the text directly after the command: `iHello`, for example. Any spaces after the command become part of the inserted text.

## Quick demo

Enter these commands in order:

```text
.
iHello world
sw
o
iSecond line
;
v
q
```

`.` turns off character highlighting so the example is easy to read. `iHello world` inserts the first line, `sw` swaps its two words, `o` opens a new line below, and `;` enables the active-line marker. The editor redraws its content after each editing or navigation command.

After `v`, the displayed document is:

```text
 world Hello
*Second line
```

The leading space on the first line and `*` on the second are display markers, not document text. `q` exits the program.

## Commands

| Command | Action |
| --- | --- |
| `?` | Show help |
| `h`, `l` | Move left, right |
| `^`, `$` | Move to the beginning, end of the line |
| `w`, `b`, `e` | Move to the next word start, current/previous word start, or current/next word end |
| `j`, `k` | Move up, down |
| A positive integer, such as `2` | Jump to a line, starting at its first character |
| `iTEXT`, `aTEXT` | Insert before, append after the cursor |
| `ITEXT`, `ATEXT` | Insert at the beginning, append at the end of the line |
| `x`, `X` | Delete the character at, before the cursor |
| `dw` | Delete from the cursor up to the next word start, or through the line end if there is no next word |
| `de` | Delete from the cursor through the current/next word end |
| `db` | Delete backward through the current/previous word start, including the cursor character |
| `dc` | Delete the entire word or whitespace span containing the cursor |
| `sw`, `sb` | Swap the word at the cursor with the next, previous word |
| `o`, `O` | Insert an empty line below, above |
| `dd` | Delete the current line |
| `J`, `K` | Move the current line up, down |
| `.`, `;` | Toggle character highlighting, active-line marker |
| `v` | Display the current document |
| `q` | Quit |

The coursework mapping is **`j` = up, `k` = down**. Line numbers start at 1; a number beyond the document length selects the last line. Invalid commands are ignored.

## Current limitations

- Text is stored in memory only. File loading/saving and undo/redo are not implemented; quitting discards the document.
- End-of-input, such as Ctrl-D on macOS/Linux, is not handled gracefully and raises `EOFError`. Use `q` to exit normally.
- An extremely long numeric line command can raise `ValueError` on Python versions that enforce an integer-conversion digit limit.

## Coursework and license

Originally developed for CSC1002 Assignment 3: Console-Based Editor. The original assignment attribution is retained in `editor.py`.

No public reuse license is included.

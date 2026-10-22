"""CSC1002 Assignment 3: Console-Based Editor"""

import re

#original state

lines = ['']         # list of strings
cur_line = 0         # index of the active line
cur_col = 0          # cursor column position on the active line
show_cursor = True   # row cursor highlight on/off
show_line = False    # line cursor (*) on/off


#help text

HELP_TEXT = (
    "? - display this help info\n"
    ". - toggle row cursor on and off\n"
    "h - move cursor left\n"
    "l - move cursor right\n"
    "^ - move cursor to beginning of the line\n"
    "$ - move cursor to end of the line\n"
    "w - move cursor to beginning of next word\n"
    "b - move cursor to beginning of current or previous word\n"
    "e - move cursor to end of the word\n"
    "i - insert <text> before cursor\n"
    "a - append <text> after cursor\n"
    "I - insert <text> from beginning\n"
    "A - append <text> at the end\n"
    "x - delete character at cursor\n"
    "X - delete character before cursor\n"
    "dw - delete to start of next word\n"
    "de - delete to end of next word\n"
    "db - delete to start of current or previous word\n"
    "dc - delete whitepaces or entire word at cursor\n"
    "sw - swap word at cursor with next word\n"
    "sb - swap word at cursor with previous word\n"
    "; - toggle line cursor on and off\n"
    "j - move cursor up\n"
    "k - move cursor down\n"
    "o - insert empty line below\n"
    "O - insert empty line above\n"
    "dd - delete line\n"
    "K - move line down\n"
    "J - move line up\n"
    "Line_No. - jump to specific line, first character\n"
    "v - view editor content\n"
    "q - quit program"
)


#display

def highlight_cursor(line, col):
    """return line with green cursor highlight at col"""
    if not show_cursor or not line:
        return line
    highlight = "\033[42m" + line[col] + "\033[0m"
    return line[:col] + highlight + line[col + 1:]

def format_line(idx):
    """return the string for line at the idx with * and highlight"""
    active = (idx == cur_line)
    displayed = highlight_cursor(lines[idx], cur_col) if active else lines[idx]
    if not show_line:
        return displayed
    return ("*" if active else " ") + displayed

def display_content():
    """print the current content to the console"""
    for idx in range(len(lines)):
        print(format_line(idx))


#identify the types of commands
    
single_no_text = set("?.hlwbe^$xXvqj;koOJK")
two_char_no_text = {"dw", "de", "db", "dc", "sw", "sb", "dd"}
all_no_text_commands = single_no_text | two_char_no_text
text_commands = set("iIaA")

def valid_number(userinput):
    """return whether input is a valid positive integer, else None"""
    if re.fullmatch(r'[1-9][0-9]*', userinput):
        return ('Line_No.', int(userinput))
    return None

def identify_command(userinput):
    """to examine whether the user's input is valid"""
    if not userinput:
        return None
    if userinput in all_no_text_commands:
        return (userinput, '')
    command = userinput[0]
    rest = userinput[1:]
    if command in text_commands and len(rest) >= 1:
        return (command, rest)
    return valid_number(userinput)


#find cursor
def clamp(position, low, high):
    """return the position of the cursor limited in [low, high]"""
    return max(low, min(high, position))

def fix_col():
    """ensure the cur_col stays in the proper place after changes"""
    global cur_col
    cur_col = clamp(cur_col, 0, final_col(lines[cur_line]))

def final_col(line):
    """return the index of the last character"""
    return max(0, len(line) - 1)

def reset_col():
    """reset cur_col to 0 if the current line is empty"""
    global cur_col
    if not lines[cur_line]:
        cur_col = 0


#word boundary

def find_words(line):
    """return a list of index tuples (start, end)"""
    return [(match.start(), match.end() - 1) for match in re.finditer(r'\S+', line)]

def next_word_start(line, col):
    """return the start of the next word after the col"""
    starts = [pos for pos, end in find_words(line) if pos > col]
    if starts:
        return starts[0]
    else:
        return final_col(line)

def previous_word_start(line, col):
    """return the start of the current word or the previous word"""
    words = find_words(line)
    in_word = [pos for pos, end in words if pos <= col <= end]
    if in_word and in_word[0] < col:
        return in_word[0]
    previous = [pos for pos, end in words if pos < col]
    if previous:
        return previous[-1]
    else:
        return 0

def current_or_next_word_end(line, col):
    """return word end after col, or final_col"""
    ends = [end for pos, end in find_words(line) if end > col]
    return ends[0] if ends else final_col(line)
    
def find_span_at(line, col):
    """return the start and end of the word or space at col"""
    for pos, end in find_words(line):
        if pos <= col <= end:
            return (pos, end)
    for match in re.finditer(r'\s+', line):
        if match.start() <= col < match.end():
            return (match.start(), match.end() - 1)
    return None

def find_word_index(line, col):
    """return the index of the word containing col, or -1"""
    for idx, (pos, end) in enumerate(find_words(line)):
        if pos <= col <= end:
            return idx
    return -1


#cursor motion commands (h, l, ^, $, w, b, e, j, k)

def command_move_left():
    """move the cursor left by one character"""
    global cur_col
    cur_col = clamp(cur_col - 1, 0, final_col(lines[cur_line]))

def command_move_right():
    """move the cursor right by one character"""
    global cur_col
    cur_col = clamp(cur_col + 1, 0, final_col(lines[cur_line]))

def command_move_beginning():
    """move the cursor to the beginning of the line"""
    global cur_col
    cur_col = 0

def command_move_end():
    """move the cursor to the end of the line"""
    global cur_col
    cur_col = final_col(lines[cur_line])

def command_next_word():
    """move the cursor to the beginning of the next word"""
    global cur_col
    cur_col = next_word_start(lines[cur_line], cur_col)

def command_previous_word():
    """move the cursor to the beginning of the current or previous word"""
    global cur_col
    cur_col = previous_word_start(lines[cur_line], cur_col)

def command_end_word():
    """move the cursor to the end of the current or next word"""
    global cur_col
    cur_col = current_or_next_word_end(lines[cur_line], cur_col)

def command_move_up():
    """move the line cursor up by one line"""
    global cur_line, cur_col
    if cur_line == 0:
        return
    cur_line -= 1
    cur_col = clamp(cur_col, 0, final_col(lines[cur_line]))

def command_move_down():
    """move the line cursor down by one line"""
    global cur_line, cur_col
    if cur_line == len(lines) - 1:
        return
    cur_line += 1
    cur_col = clamp(cur_col, 0, final_col(lines[cur_line]))


#insert and append commands (i, I, a, A)

def command_insert(text):
    """insert text before the cursor"""
    global cur_col
    lines[cur_line] = lines[cur_line][:cur_col] + text + lines[cur_line][cur_col:]

def command_insert_beginning(text):
    """insert text at the beginning of the line"""
    global cur_col
    lines[cur_line] = text + lines[cur_line]
    cur_col = 0

def command_append(text):
    """append text after the cursor"""
    global cur_col
    if not lines[cur_line]:
        insert_position = len(lines[cur_line])
    else:
        insert_position = cur_col + 1
    lines[cur_line] = lines[cur_line][:insert_position] + text + lines[cur_line][insert_position:]
    cur_col = insert_position + len(text) - 1

def command_append_end(text):
    """append text at the end of the line"""
    global cur_col
    lines[cur_line] = lines[cur_line] + text
    cur_col = final_col(lines[cur_line])


#delete commands (x, X)

def command_delete_at():
    """delete the character at the cursor"""
    if not lines[cur_line]:
        return
    lines[cur_line] = lines[cur_line][:cur_col] + lines[cur_line][cur_col + 1:]
    fix_col()
    reset_col()

def command_delete_before():
    """delete the character before the cursor"""
    global cur_col
    if not lines[cur_line] or cur_col == 0:
        return
    lines[cur_line] = lines[cur_line][:cur_col - 1] + lines[cur_line][cur_col:]
    cur_col -= 1
    fix_col()
    reset_col()


#delete word commands (dw, de, db, dc)

def command_delete_next_word():
    """delete from the cursor to the start of the next word"""
    if not lines[cur_line]:
        return
    starts = [pos for pos, end in find_words(lines[cur_line]) if pos > cur_col]
    target = starts[0] if starts else len(lines[cur_line])
    lines[cur_line] = lines[cur_line][:cur_col] + lines[cur_line][target:]
    fix_col()
    reset_col()

def command_delete_end_word():
    """delete from the cursor to the end of the current or next word"""
    if not lines[cur_line]:
        return
    target = current_or_next_word_end(lines[cur_line], cur_col)
    lines[cur_line] = lines[cur_line][:cur_col] + lines[cur_line][target + 1:]
    fix_col()
    reset_col()

def command_delete_prev_word():
    """delete from the cursor to the start of the current or previous word"""
    global cur_col
    if not lines[cur_line]:
        return
    target = previous_word_start(lines[cur_line], cur_col)
    lines[cur_line] = lines[cur_line][:target] + lines[cur_line][cur_col + 1:]
    cur_col = target
    fix_col()
    reset_col()

def command_delete_at_cursor():
    """delete the word or whitespace at the cursor"""
    if not lines[cur_line]:
        return
    span = find_span_at(lines[cur_line], cur_col)
    if span:
        lines[cur_line] = lines[cur_line][:span[0]] + lines[cur_line][span[1] + 1:]
    fix_col()
    reset_col()


#swap word commands (sw, sb)

def compute_swap_base(start_left, end_left, start_right, word_right):
    """compute the base position after swapping two words"""
    return start_left + len(word_right) + (start_right - end_left - 1)       

def swap_words(cur_idx, other_idx):
    """swap the word at cur_idx with the word at other_idx"""
    global cur_col
    words = find_words(lines[cur_line])
    left, right = min(cur_idx, other_idx), max(cur_idx, other_idx)
    word_left, word_right = lines[cur_line][words[left][0]:words[left][1] + 1], \
        lines[cur_line][words[right][0]:words[right][1] + 1]
    offset = cur_col - words[cur_idx][0]
    lines[cur_line] = lines[cur_line][:words[left][0]] + word_right \
        + lines[cur_line][words[left][1] + 1:words[right][0]] + word_left \
        + lines[cur_line][words[right][1] + 1:]
    cur_col = (compute_swap_base(words[left][0], words[left][1], words[right][0], word_right) \
        if cur_idx == left else words[left][0]) + offset

def command_swap_next_word():
    """swap the word at the cursor with the next word"""
    idx = find_word_index(lines[cur_line], cur_col)
    if 0 <= idx < len(find_words(lines[cur_line])) - 1:
        swap_words(idx, idx + 1)

def command_swap_prev_word():
    """swap the word at the cursor with the previous word"""
    idx = find_word_index(lines[cur_line], cur_col)
    if idx > 0:
        swap_words(idx, idx - 1)


#multi-line commands (;, o, O, dd, J, K, Line_No.)

def command_toggle_line():
    """toggle the line cursor"""
    global show_line
    show_line = not show_line

def command_insert_line_below():
    """insert an empty line below the current line"""
    global cur_line, cur_col
    lines.insert(cur_line + 1, '')
    cur_line += 1
    cur_col = 0

def command_insert_line_above():
    """insert an empty line above the current line"""
    global cur_line, cur_col
    lines.insert(cur_line, '')
    cur_col = 0

def command_delete_line():
    """delete the current line"""
    global cur_line
    if len(lines) == 1:
        lines[0] = ''
    else:
        lines.pop(cur_line)
        cur_line = clamp(cur_line, 0, len(lines) - 1)
    fix_col()

def command_move_line_up():
    """swap the current line with the line above"""
    global cur_line
    if cur_line == 0:
        return
    lines[cur_line], lines[cur_line - 1] = lines[cur_line - 1], lines[cur_line]
    cur_line -= 1

def command_move_line_down():
    """swap the current line with the line below"""
    global cur_line
    if cur_line == len(lines) - 1:
        return
    lines[cur_line], lines[cur_line + 1] = lines[cur_line + 1], lines[cur_line]
    cur_line += 1

def command_jump_to_line(line_num):
    """jump to line n"""
    global cur_line, cur_col
    cur_line = clamp(line_num - 1, 0, len(lines) - 1)
    cur_col = 0


#other commands (., ?, v)

def command_toggle_cursor():
    """toggle the visibility of the cursor"""
    global show_cursor
    show_cursor = not show_cursor

def command_help():
    """display the help info"""
    print(HELP_TEXT)

def command_view():
    """for view command"""
    pass


#commands representation table

no_text_representation = {
    "h": command_move_left,
    "l": command_move_right,
    "^": command_move_beginning,
    "$": command_move_end,
    "w": command_next_word,
    "b": command_previous_word,
    "e": command_end_word,
    "x": command_delete_at,
    "X": command_delete_before,
    ".": command_toggle_cursor,
    "v": command_view,
    "j": command_move_up,
    "k": command_move_down,
    ";": command_toggle_line,
    "o": command_insert_line_below,
    "O": command_insert_line_above,
    "dd": command_delete_line,
    "J": command_move_line_up,
    "K": command_move_line_down,
    "dw": command_delete_next_word,
    "de": command_delete_end_word,
    "db": command_delete_prev_word,
    "dc": command_delete_at_cursor,
    "sw": command_swap_next_word,
    "sb": command_swap_prev_word,
}

text_representation = {
    "i": command_insert,
    "a": command_append,
    "I": command_insert_beginning,
    "A": command_append_end,
}


#execution

def run_command(command, text):
    """execute a command and refresh"""
    if command == 'Line_No.':
        command_jump_to_line(text)
    elif command in no_text_representation:
        no_text_representation[command]()
    elif command in text_representation:
        text_representation[command](text)
    display_content()
    return True

def execute_command(command, text):
    """handle quit and help"""
    if command == 'q':
        return False
    if command == '?':
        command_help()
        return True
    return run_command(command, text)


#main function

def run_function():
    """repeatedly execute commands until quit"""
    running_state = True
    while running_state:
        identity = identify_command(input('>'))
        if identity is not None:
            running_state = execute_command(*identity)

def main():
    """initialize editor state and start the command loop"""
    global lines, cur_line, cur_col, show_cursor, show_line
    lines, cur_line, cur_col = [''], 0, 0
    show_cursor, show_line = True, False
    run_function()

if __name__ == '__main__':
    main()



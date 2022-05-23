from .Table import getTexTable

count = 1000

def save_text(text):
    filename = 'result.txt'
    try:
        f = open(filename, "w")
        f.write(text)
    finally:
        f.close()

def contains_character(string, character):
    for ch in string:
        if ch == character:
            return True
    return False

def valid_filename(filename):
    MAX_LENGTH = 255
    restricted_characters = ['/', '\'', '\"']
    non_recommended_characters = ['$', '%', '\\', '(', ')', '{', '}', '[', ']', '<', '>', '|', ':', '&']

    if filename == None or len(filename) < 1 or len(filename) > MAX_LENGTH:
        return False

    for character in restricted_characters:
        if contains_character(filename, character):
            return False

    # for character in non_recommended_characters:
    #     if contains_character(filename, character):
    #         return False

    return True

def save_table(rows, columns, title, filename=""):
    tex_source = getTexTable(rows, columns, title)

    global count
    if filename == "":
        filename = 'table' + str(count) + ".tex"
        count += 1
    elif not(filename.endswith(".tex")):
        filename += ".tex"

    if not(valid_filename(filename)):
        print("Invalid filename")
        return
    
    try:
        f = open(filename, "w")
        f.write(tex_source)
    finally:
        f.close()

def save_figure(fig, filename = "", **kwargs):
    global count
    if filename == "":
        filename = 'figure' + str(count) + ".png"
        count += 1
    if not(valid_filename(filename)):
        print("Invalid Filename")
        return

    fig.savefig(filename, **kwargs)
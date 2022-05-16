import os

def save_text(text, filename=None):
    filename = "result.txt"
    try:
        f = open(filename, "w")
        f.write(text)
    finally:
        f.close()
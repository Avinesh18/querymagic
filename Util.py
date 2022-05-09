import os

from matplotlib.pyplot import figure

figures_created = 0

def save_figure(fig, filename=None, chain_files=False):
    if fig == None:
        return
    if filename == None:
        filename = os.getenv("QUERYMAGIC_FILENAME")
        filename = filename if filename != None else "querymagic-figure"
        filename += ".png"    
    
    if chain_files:
        global figures_created
        figures_created += 1
        index_dot = filename.find('.')
        if index_dot != -1:
            filename = filename[:index_dot] + "_" + str(figures_created) + filename[index_dot:]
    fig.savefig(filename, bbox_inches = "tight")

def save_text(text, filename=None):
    if filename == None:
        filename = os.getenv("QUERYMAGIC_FILENAME")
        filename = filename if filename != None else "querymagic-output"
    try:
        f = open(filename, "w")
        f.write(text)
    finally:
        f.close()
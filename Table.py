import matplotlib.pyplot as plt
from pandas.plotting import table

MAX_CHARACTERS_IN_ONE_LINE = 30

def break_text_into_lines(text):
    return '\n'.join(text[i:i+MAX_CHARACTERS_IN_ONE_LINE] for i in range(0, len(text), MAX_CHARACTERS_IN_ONE_LINE))

def generateTable(df, options):
    fig, ax = plt.subplots()
    ax.set(frame_on = False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)

    df_table = table(ax, df, loc='center')
    df_table.scale(3.5, 1.5)
    df_table.set(fontsize = 'medium')

    cells = df_table.get_celld()

    # Calculating and setting correct height for column labels
    height_multiplier = 1
    for j in range(0, len(df.columns)):
        cell = cells[(0, j)]
        cell_text = cell.get_text().get_text()
        cell_height = cell.get_height()
        height_multiplier = max(height_multiplier, len(cell_text) / MAX_CHARACTERS_IN_ONE_LINE + cell_text.count('\n'))
        cell.set_text_props(verticalalignment = 'center', horizontalalignment = 'center')

        if len(cell_text) > MAX_CHARACTERS_IN_ONE_LINE:
            cell_text = break_text_into_lines(cell_text)
            cell.set_text_props(text = cell_text)

    for j in range(0, len(df.columns)):
        cell = cells[(0, j)]
        cell_height = cell.get_height()
        cell.set(height = cell_height * height_multiplier)

    #Calcuating and setting correct height for other rows
    for i in range(1, len(df.index) + 1):
        height_multiplier = 1
        for j in range(-1, len(df.columns)):
            cell = cells[(i, j)]
            cell_text = cell.get_text().get_text()
            cell_height = cell.get_height()
            height_multiplier = max(height_multiplier, len(cell_text) / MAX_CHARACTERS_IN_ONE_LINE + cell_text.count('\n'))
            cell.set_text_props(verticalalignment = 'center', horizontalalignment = 'center')

            if len(cell_text) > MAX_CHARACTERS_IN_ONE_LINE:
                cell_text = break_text_into_lines(cell_text)
                cell.set_text_props(text = cell_text)
        
        for j in range(-1, len(df.columns)):
            cell = cells[(i, j)]
            cell_height = cell.get_height()
            cell.set(height = cell_height * height_multiplier)

    return fig
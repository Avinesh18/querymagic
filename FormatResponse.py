import pandas
from IPython.display import display
from .Table import generateTable
from .Chart import plotChart

def formatResponse(result, options):
    print(options)
    fig = None
    
    if not('out' in options):
        print("Displaying dataframe")
        display(pandas.DataFrame(result['rows'], columns = result['columns']))

    elif options['out'] == 'table':
        print("Saving dataframe to image")
        fig = generateTable(result, options)

    elif options['out'] == "raw":
        print("Displaying raw result")
        display(result)

    elif options['out'] == 'chart':
        print("Saving chart")
        fig = plotChart(result, options)

    else:
        print("Invalid out parameter. Saving dataframe as png")
        fig = generateTable(result, options)

    return fig

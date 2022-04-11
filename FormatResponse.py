import pandas
import matplotlib.pyplot as plt
from pandas.plotting import table

def formatResponse(result, options):
    if ~('out' in options) or options['out'] == 'df':
        return pandas.DataFrame(result['rows'], columns = result['columns'])
        # dataframeToImage(pandas.DataFrame(result['rows'], columns = result['columns']), options)
    elif options['out'] == "raw":
        return result
    elif options['out'] == "table":
        return generateTable()
    else:
        return pandas.DataFrame(result['rows'], columns = result['columns'])

def generateTable():
    # TODO
    pass

def dataframeToImage(df, options):
    ax = plt.subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table(ax, df, loc='center')
    plt.savefig(options['filename'] + ".png")

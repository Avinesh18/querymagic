import pandas
import matplotlib.pyplot as plt
from matplotlib.dates import datestr2num
from pandas.plotting import table
from IPython.display import display
import numpy as np
from dateutil.parser import parse
import re

VALID_DATA_TYPES = ["bool", "boolean", "datetime", "date", "int", "long", "real", "double", "string", "timespan", "time", "decimal"]

def dataframeToImage(df, options):
    plt.figure(figsize = (10, 5), dpi = 80)
    ax = plt.subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    table(ax, df, loc='center')
    plt.savefig(options['filename'] + ".png")

def validDateString(string):
    try:
        parse(string)
    except ValueError:
        return False
    return True

def isBool(data):
    for e in data:
        if e != True and e != False:
            return False
    return True

def isNumber(data):
    num_regex = re.compile("^\d+([.]\d+)?$")
    for e in data:
        if re.match(num_regex, e) == None:
            return False
    return True

def isDateTime(data):
    for e in data:
        if not(validDateString(e)):
            return False
    return True

def findType(data):
    if isBool(data):
        return 'bool'
    elif isNumber(data):
        return 'real'
    elif isDateTime(data):
        return 'datetime'
    else:
        return 'string'
        
def formatRealDataSeries(data):
    data = np.vectorize(lambda x: float(x))(data)
    return data

def formatBoolDataSeries(data):
    data = np.vectorize(lambda x: int(x))(data)
    return data

def formatDateTimeDataSeries(data):
    data = np.vectorize(lambda x: parse(x))(data)
    return data

def formatDataSeries(data, type, allow_string):
    if type == None:
        type = findType(data)
    
    if type == 'boolean':
        type = 'bool'
    elif type == 'date' or type == 'timespan' or type == 'time':
        type = 'datetime'
    elif type == 'int' or type == 'long' or type == 'double':
        type = 'real'

    print("Series Type:", type)
    
    if type == 'string' and not(allow_string):
        raise Exception('cannot plot this type of data')

    if type == 'real':
        data = formatRealDataSeries(data)
    elif type == 'bool':
        data = formatBoolDataSeries(data)
    elif type == 'datetime':
        data = formatDateTimeDataSeries(data)
    
    return data

def formatRowsAndColumnsForPlotting(result, x_field, y_field):
    x_field_index = np.where(result['columns'] == x_field)[0][0]
    y_field_index = np.where(result['columns'] == y_field)[0][0]
    x_series = result['rows'][:, x_field_index]
    y_series = result['rows'][:, y_field_index]
    x_series = formatDataSeries(x_series, None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][x_field_index], True)
    y_series = formatDataSeries(y_series, None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][y_field_index], False)
    return (x_series, y_series)

def plotChartAndSaveToFile(result, options):
    chart_type = options['chart'] if 'chart' in options else 'linechart'
    x_field = None if not('x' in options) else options['x']
    y_field = None if not('y' in options) else options['y']

    result_has_x_field = x_field != None and x_field in result['columns']
    result_has_y_field = y_field != None and y_field in result['columns']
    if chart_type == '' or not(result_has_x_field) or not(result_has_y_field):
        print("Can't plot chart, saving a table instead")
        print(chart_type)
        print(x_field, result_has_x_field)
        print(y_field, result_has_y_field)
        return dataframeToImage(pandas.DataFrame(result['rows'], columns = result['columns']), options)

    (x_series, y_series) = formatRowsAndColumnsForPlotting(result, x_field, y_field)
    
    plt.figure(figsize = (10, 5), dpi = 80)
    plt.xticks(rotation=70)
    plt.plot(x_series, y_series)
    plt.savefig(options['filename'] + ".png")

def formatResponse(result, options):
    print(options)
    
    if not('out' in options) or options['out'] == 'table':
        print("Saving dataframe to image")
        dataframeToImage(pandas.DataFrame(result['rows'], columns = result['columns']), options)

    elif options['out'] == "raw":
        print("Displaying raw result")
        display(result)

    elif options['out'] == 'chart':
        print("Saving chart")
        plotChartAndSaveToFile(result, options)

    elif options['out'] == "df":
        print("Displaying dataframe")
        display(pandas.DataFrame(result['rows'], columns = result['columns']))

    else:
        print("Invalid out parameter. Saving dataframe as png")
        dataframeToImage(pandas.DataFrame(result['rows'], columns = result['columns']), options)

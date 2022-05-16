import numpy as np
import matplotlib.pyplot as plt
from dateutil.parser import parse
import pandas
import re
from .Table import generateTable

count = 1

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

# def formatRowsAndColumnsForPlotting(result, x_field, y_field):
#     x_field_index = np.where(result['columns'] == x_field)[0][0]
#     y_field_index = np.where(result['columns'] == y_field)[0][0]

#     x_series = np.array(result['rows'])[:, x_field_index]
#     y_series = np.array(result['rows'])[:, y_field_index]

#     x_series = formatDataSeries(x_series, None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][x_field_index], True)
#     y_series = formatDataSeries(y_series, None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][y_field_index], False)

#     return (x_series, y_series)

def getSeries(result, name, allow_string):
    index = np.where(result['columns'] == name)[0][0]
    series = np.array(result['rows'])[:, index]
    return formatDataSeries(series, None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][index], allow_string)

def validateInputParameters(result, options):
    x_name = None if not('x' in options) else options['x']
    if not(x_name in result['columns']):
        return False, "Invalid x parameter"

    if 'y1' in options:
        i = 1
        while ('y' + str(i)) in options:
            y_name = options['y' + str(i)]
            if not(y_name in result['columns']):
                return False, "Invalid y" + str(i) + " parameter"
            i += 1
    else:
        y_name = None if not('y' in options) else options['y']
        if y_name != None and not(x_name in result['columns']):
            return False, "Invalid y paramter"
    return True, ""

def plotChart(result, options):
    chart_type = options['chart'] if 'chart' in options else 'linechart'
    valid, comment = validateInputParameters(result, options)
    if not(valid):
        print(comment)
        return generateTable(result, options)

    # (x_series, y_series) = formatRowsAndColumnsForPlotting(result, column_x, column_y)
    x_series = getSeries(result, options['x'], True)

    no_y_series = 0
    labels = []
    y_series = []
    if not('y' in options):
        while 'y' + str(no_y_series+1) in options:
            y_series.append(getSeries(result, options['y' + str(no_y_series + 1)], False))
            labels.append(options['y' + str(no_y_series + 1)])
            no_y_series+=1
    else:
        no_y_series = 1
        y_series.append(getSeries(result, options['y'], False))
        labels.append(options['y'])
    
    fig, ax = plt.subplots(figsize = (10, 5), dpi = 80)

    if chart_type == 'barchart':
        for i in range(no_y_series):
            ax.bar(x_series, y_series[i])

    elif chart_type == 'piechart':
        ax.pie(y_series, labels=x_series, startangle=90, autopct='%.1f%%')

    elif chart_type == 'scatterplot':
        for i in range(no_y_series):
            ax.scatter(x_series, y_series[i], label = labels[i])

    else:
        for i in range(no_y_series):
            ax.plot(x_series, y_series[i], label = labels[i])
    
    ax.tick_params(axis = 'x', labelrotation = 70)
    ax.grid(axis='y')
    ax.legend(loc = 'upper right')

    global count
    filename = options['title'] if 'title' in options else 'chart' + str(count) + '.png'
    count += 1 

    fig.suptitle(options['title'] if 'title' in options else '')
    fig.savefig(filename, bbox_inches = 'tight')
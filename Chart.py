import numpy as np
import matplotlib.pyplot as plt
from dateutil.parser import parse
import re
from .Util import valid_filename

count = 1

class ChartProperties:
    pass

def getProperties(options):
    chart_properties = ChartProperties()
    chart_properties.x = options['x'] if 'x' in options else None
    chart_properties.type = options['type'] if 'type' in options else 'linechart'
    chart_properties.group = options['groupBy'] if 'groupBy' in options else None
    chart_properties.title = options['title'] if 'title' in options else ''


    if 'y1' in options:
        count = 1
        chart_properties.y = []
        while 'y' + str(count) in options:
            chart_properties.y.append(options['y' + str(count)])
            count += 1
    else:
        chart_properties.y = [options['y']] if 'y' in options else []

    if chart_properties.x == None or len(chart_properties.y) == 0:
        return None, "Need x and y parameters"
    if chart_properties.group != None and len(chart_properties.y) > 1:
        return None, "Grouping possible only with single y series"
    return chart_properties, None

def columnExists(result, name):
    return name in result['columns']

def isBool(series):
    for e in series:
        if e != True and e != False:
            return False
    return True

def isNumber(series):
    num_regex = re.compile("^\d+([.]\d+)?$")
    for e in series:
        if re.match(num_regex, e) == None:
            return False
    return True

def validDateString(string):
    try:
        parse(string)
    except ValueError:
        return False
    return True

def isDateTime(series):
    for e in series:
        if not(validDateString(e)):
            return False
    return True

def findType(series):
    if isBool(series):
        return 'bool'
    elif isNumber(series):
        return 'real'
    elif isDateTime(series):
        return 'datetime'
    else:
        return 'string'

def formatRealSeries(series):
    series = np.vectorize(lambda x: float(x))(series)
    return series

def formatBoolSeries(series):
    series = np.vectorize(lambda x: int(x))(series)
    return series

def formatDateTimeSeries(series):
    series = np.vectorize(lambda x: parse(x))(series)
    return series

def formatSeries(series, type):
    if type == None:
        type = findType(series)
    
    if type == 'boolean':
        type = 'bool'
    elif type == 'date' or type == 'timespan' or type == 'time':
        type = 'datetime'
    elif type == 'int' or type == 'long' or type == 'double':
        type = 'real'

    if type == 'real':
        series = formatRealSeries(series)
    elif type == 'bool':
        series = formatBoolSeries(series)
    elif type == 'datetime':
        series = formatDateTimeSeries(series)
    
    return series, type

def getSeries(result, name):
    index = np.where(result['columns'] == name)[0][0]
    series = np.array(result['rows'])[:, index]
    series_type = None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][index]
    return formatSeries(series, series_type)

def matrixColumn(array, index):
    return [array[i][index] for i in range(len(array))]

def getGroupedSeries(result, properties):
    if not(columnExists(result, properties.x)):
        return None, "Invlaid x parameter"
    if not(columnExists(result, properties.y[0])):
        return None, "Invalid y parameter"
    if not(columnExists(result, properties.group)):
        return None, "Invalid groupBy parameter"

    x_series, x_type = getSeries(result, properties.x)

    y_index = np.where(result['columns'] == properties.y[0])[0][0]
    y_type = None if type(result['column_types']).__name__ == 'NoneType' else result['column_types'][y_index]
    if y_type == 'string':
        return None, "y series cannot be string"

    group_column_index = np.where(result['columns'] == properties.group)[0][0]
    groups = {}
    for i in range(len(x_series)):
        group = result['rows'][i][group_column_index]
        if group in groups:
            groups[group].append([x_series[i], result['rows'][i][y_index]])
        else:
            groups[group] = [[x_series[i], result['rows'][i][y_index]]]

    series = []
    for group in groups.keys():
        group_series = groups[group]
        if x_type != 'real' and x_type != 'datetime':
            formatted_y, _ = formatSeries(matrixColumn(group_series, 1), y_type)
            series.append((matrixColumn(group_series, 0), formatted_y, group))

        elif x_type == 'real':
            group_series.sort(key = lambda x: x[0])
            formatted_y, _ = formatSeries(matrixColumn(group_series, 1), y_type)
            series.append((matrixColumn(group_series, 0), formatted_y, group))

        elif x_type == 'datetime':
            group_series.sort(key = lambda x: x[0].timestamp())
            formatted_y, _ = formatSeries(matrixColumn(group_series, 1), y_type)
            series.append((matrixColumn(group_series, 0), formatted_y, group))

    return series, None

def getAllSeries(result, properties):
    series = []

    if not(columnExists(result, properties.x)):
        return None, "Invalid x parameter"
    for y_name in properties.y:
        if not(columnExists(result, y_name)):
            return None, "Invalid y parameter"

    x_series, x_type = getSeries(result, properties.x)

    if x_type != 'real' and x_type != 'datetime':
        for y_name in properties.y:
            y_series, y_type = getSeries(result, y_name)
            if y_type == 'string':
                return None, "y series cannot be string"

            series.append((x_series.copy(), y_series, y_name))
        return series, None
    else:
        y_index = []
        y_types = []
        for y_name in properties.y:
            y_index.append(np.where(result['columns'] == y_name)[0][0])
            y_types.append(result['column_types'][y_index[-1]] if type(result['column_types']).__name__ != 'NoneType' else None)
        
        aggregate_series = []
        for i in range(len(x_series)):
            row = [x_series[i]]
            for index in y_index:
                row.append(result['rows'][i][index])
            aggregate_series.append(row)

        if x_type == 'real':
            aggregate_series.sort(key = lambda x: x[0])
        elif x_type == 'datetime':
            aggregate_series.sort(key = lambda x: x[0].timestamp())

        x_series = matrixColumn(aggregate_series, 0)
        for i in range(1, len(aggregate_series[0])):
            y_series, y_type = formatSeries(matrixColumn(aggregate_series, i), y_types[i-1])
            if y_type == 'string':
                return None, "y series cannot be string"
            series.append((x_series.copy(), y_series, properties.y[i-1]))

        return series, None



def plotChart(result, options):
    properties, error = getProperties(options)
    if error != None:
        print(error)
        return

    series = None
    error = None
    if properties.group != None:
        series, error = getGroupedSeries(result, properties)
    else:
        series, error = getAllSeries(result, properties)
    
    if error != None:
        print(error)
        return

    fig, ax = plt.subplots(figsize = (10, 5), dpi = 80)
    if properties.type == 'barchart':
        for element in series:
            ax.bar(element[0], element[1], label = element[2])

    elif properties.type == 'piechart':
        ax.pie(series[0][1], labels = series[0][0], startangle = 90, autopct = '%.1f%%')

    elif properties.type == 'scatterplot':
        for element in series:
            ax.scatter(element[0], element[1], label = element[2])

    else:
        for element in series:
            ax.plot(element[0], element[1], label = element[2])

    ax.tick_params(axis = 'x', labelrotation = 70)
    ax.grid(axis = 'y')
    if properties.type != 'piechart':
        ax.legend(loc = 'upper right')

    fig.suptitle(properties.title)

    global count
    if properties.title != '' and valid_filename(properties.title):
        filename = properties.title + '.png'
    else:
        filename = 'chart' + str(count) + '.png'
        count += 1
    fig.savefig(filename, bbox_inches = 'tight')
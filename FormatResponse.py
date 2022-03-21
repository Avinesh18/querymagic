import pandas

def formatSplunkResponse(result, format):
    if format == "df":
        return pandas.DataFrame(result['rows'], columns = result['fields'])
    elif format == "json":
        return result
    elif format == "table":
        return generateTable()

def generateTable():
    return 'PRETEND THIS IS A TABLE!'
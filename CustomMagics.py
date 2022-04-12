import os
from IPython.core.magic import register_cell_magic, Magics, magics_class, cell_magic, needs_local_scope
from IPython.display import display
from .Splunk import execute as splunk_execute
from .Kusto import execute as kusto_execute
from .FormatResponse import formatResponse
import threading
import pandas
import re

threadLock = threading.Lock()

print("USING LOCAL QUERYMAGIC")

class QueryResult:
    def __init__(self, type=None, query=None, result=None):
        self.__type = type
        self.__query = query
        self.__result = result

    @property
    def type(self):
        return self.__type

    @property
    def query(self):
        return self.__query

    @property
    def result(self):
        return self.__result
    
    def _set(self, type, query, result):
        self.__type = type
        self.__query = query
        self.__result = result

_last_query_result = QueryResult()

def parse_parameters(parameters):
    valid_parameters_regex = re.compile("^(-(\w+)([ ]+(\w+))?[ ]*)*$")
    if valid_parameters_regex.match(parameters) == None:
        raise Exception("invalid paramter string")

    paramter_regex = re.compile("-(\w+)[ ]+(\w*)")
    options = re.findall(paramter_regex, parameters)
    paramter_map = {}
    for option in options:
        paramter_map[option[0]] = option[1]

    return paramter_map

# Any \val present in the query string is replaced by the value of identifier val
# Any \\val present in the query string is replaced to \val
def add_substitutions(query, local_ns):
    open_braces_replaced = re.compile(r"{").sub("{{", query)
    closed_braces_replaced = re.compile(r"}").sub("}}", open_braces_replaced)
    
    escaped_value_rgx = re.compile(r"(?:\s)\\(\w+)")
    format_string = escaped_value_rgx.sub(" {}", closed_braces_replaced)
    
    substitution_values = []
    for field in re.findall(escaped_value_rgx, query):
        substitution_values.append(local_ns[field])
        
    substituted_string = format_string.format(*tuple(substitution_values))
    
    restored_escaped_backslash = re.compile(r"\\\\").sub(r"\\", substituted_string)
    return restored_escaped_backslash

@magics_class
class QueryMagic(Magics):

    def __init__(self, shell):
        super(QueryMagic, self).__init__(shell)

    @needs_local_scope
    @cell_magic
    def splunk(self, line, cell, local_ns = None):
        parameters = parse_parameters(line)
        parameters['filename'] = os.getenv('QUERYMAGIC_FILENAME')
        parameters['filename'] = parameters['filename'] if parameters['filename'] != None else 'querymagic-image'
        substituted_string = add_substitutions(cell, local_ns)
        try:
            threadLock.acquire()
            try:
                result = splunk_execute(substituted_string)
            except Exception as e:
                print(e)
                return

            global _last_query_result
            _last_query_result._set("splunk", substituted_string, result)

            formatResponse(result, parameters)
        finally:
            threadLock.release()

    @needs_local_scope
    @cell_magic
    def kusto(self, line, cell, local_ns = None):
        parameters = parse_parameters(line)
        parameters['filename'] = os.getenv('QUERYMAGIC_FILENAME')
        parameters['filename'] = parameters['filename'] if parameters['filename'] != None else 'querymagic-image'
        substituted_string = add_substitutions(cell, local_ns)
        try:
            threadLock.acquire()
            try:
                result = kusto_execute(substituted_string)
            except Exception as e:
                print(e)
                return

            global _last_query_result
            _last_query_result._set("kusto", substituted_string, result)

            for i in range(len(result)):
                formatResponse(result[i], parameters)
        finally:
            threadLock.release()

ip = get_ipython()
ip.register_magics(QueryMagic)
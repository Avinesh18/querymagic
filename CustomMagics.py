from IPython.core.magic import register_cell_magic, Magics, magics_class, cell_magic, needs_local_scope
from IPython.display import display
from .FetchResult import fetch_kusto, fetch_splunk
from .FormatResponse import formatSplunkResponse
from .Util import add_substitutions
import threading
import pandas
import re as regex

threadLock = threading.Lock()
_last_query_result = ""
SPLUNK_VALID_OUTPUT_MODES = ["df", "json", "table"]

class QueryResult:
    def __init__(self, type=None, query=None, result=None):
        self._type = type
        self._query = query
        self._result = result

    @property
    def type(self):
        return self._type

    @property
    def query(self):
        return self._query

    @property
    def result(self):
        return self._result
    
    def set(self, type, query, result):
        self._type = type
        self._query = query
        self._result = result

_last_query_result = QueryResult()

@magics_class
class QueryMagic(Magics):

    def __init__(self, shell):
        super(QueryMagic, self).__init__(shell)

    @needs_local_scope
    @cell_magic
    def splunk(self, line, cell, local_ns=None):
        output_mode = "df"
        options = regex.findall("-(\w+)[ ]+(\w*)", line)
        for option in options:
            if option[0] == 'out':
                if option[1] in SPLUNK_VALID_OUTPUT_MODES:
                    output_mode = option[1]

        substituted_string = add_substitutions(cell, local_ns)
        try:
            threadLock.acquire()
            result = fetch_splunk(substituted_string)
            global _last_query_result
            _last_query_result.set("splunk", substituted_string, result)
            display(formatSplunkResponse(result, output_mode))
            # return formatSplunkResponse(result, output_mode)
        finally:
            threadLock.release()

ip = get_ipython()
ip.register_magics(QueryMagic)
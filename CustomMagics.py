from IPython.core.magic import register_cell_magic
from IPython.display import display
from .FetchResult import fetch_kusto, fetch_splunk
import threading
import pandas

threadLock = threading.Lock()
_last_query_result = ""

@register_cell_magic
def splunk(line, cell):
    try:
        threadLock.acquire()
        result = fetch_splunk(cell)
        display(pandas.DataFrame(result['rows'], columns = result['fields']))
        _last_query_result = result
    finally:
        threadLock.release()

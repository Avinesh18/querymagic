import time
from .Splunk import *

_SPLUNK_SLEEP_SECONDS = 2

def fetch_kusto(query):
    return "MOCK KUSTO RESULT!"

def fetch_splunk(query):
    search_id = send_request(query)

    # time.sleep(1)
    done_progress = 0
    while done_progress != 1:
        (done_progress, dispatch_state) = get_status(search_id)
        print(dispatch_state)

        if done_progress != 1:
            time.sleep(_SPLUNK_SLEEP_SECONDS)
    
    print("Fetching Result")
    json_response = fetch_result(search_id)
    return json_response
from datetime import timedelta
import os
from dotenv import load_dotenv
from azure.kusto.data import KustoClient, KustoConnectionStringBuilder, ClientRequestProperties
from azure.kusto.data.exceptions import KustoServiceError
from azure.kusto.data.helpers import dataframe_from_result_table

load_dotenv()
_CLIENT_ID = os.getenv("KUSTO_CLIENT_ID")
_CLIENT_SECRET = os.getenv("KUSTO_CLIENT_SECRET")
_TENANT_ID = os.getenv("KUSTO_TENANT_ID")
_CLUSTER = "https://ghinsights.eastus2.kusto.windows.net"
_DATABASE = "Insights"
_TIMEOUT_MINUTES = 10

if _CLIENT_ID == None:
    raise Exception("Kusto Client ID not found")
if _CLIENT_SECRET == None:
    raise Exception("Kusto Client Secret not found")
if _TENANT_ID == None:
    raise Exception("Kusto Tenant ID not found")

print(_CLIENT_ID)
print(_CLIENT_SECRET)
print(_TENANT_ID)


def execute(query):
    kcsb = KustoConnectionStringBuilder.with_aad_application_key_authentication(_CLUSTER, _CLIENT_ID, _CLIENT_SECRET, _TENANT_ID)
    client = KustoClient(kcsb)
    properties = ClientRequestProperties()
    properties.set_option(properties.request_timeout_option_name, timedelta(seconds = _TIMEOUT_MINUTES * 60))

    try:
        response = client.execute(_DATABASE, query, properties)
        formatted_response = []
        for i in range(len(response.primary_results)):
            formatted_response.append(format_kusto_response(response.primary_results[i]))
        return formatted_response
    except KustoServiceError as error:
        print("Error:", error)

def format_kusto_response(response):
    formatted_response = {}
    formatted_response['columns'] = list(map((lambda x: x['ColumnName']), response.raw_columns))
    formatted_response['rows'] = response.raw_rows
    return formatted_response
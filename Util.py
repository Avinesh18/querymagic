import re as regex

# Any \val present in the query string is replaced by the value of identifier val
# Any \\val present in the query string is replaced to \val
def add_substitutions(query, local_ns):
    open_braces_replaced = regex.compile(r"{").sub("{{", query)
    closed_braces_replaced = regex.compile(r"}").sub("}}", open_braces_replaced)
    
    escaped_value_rgx = regex.compile(r"(?:\s)\\(\w+)")
    format_string = escaped_value_rgx.sub(" {}", closed_braces_replaced)
    
    substitution_values = []
    for field in regex.findall(escaped_value_rgx, query):
        substitution_values.append(local_ns[field])
        
    substituted_string = format_string.format(*tuple(substitution_values))
    
    restored_escaped_backslash = regex.compile(r"\\\\").sub(r"\\", substituted_string)
    return restored_escaped_backslash
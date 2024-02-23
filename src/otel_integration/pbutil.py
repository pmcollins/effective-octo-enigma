import time


def save_proto(pbobj, kind):
    filename = f"{time.time_ns()}_{kind}.pbstr"
    with open(filename, "wb") as file:
        file.write(pbobj.SerializeToString(deterministic=True))


def get_trace_attr_str(tr, attr_name) -> [str]:
    out = []
    for span in tr.resource_spans:
        for attr in span.resource.attributes:
            if attr.key == attr_name:
                out.append(attr.value.string_value)
    return out

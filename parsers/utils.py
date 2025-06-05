from .fit_parser import parse_fit
from .tcx_parser import parse_tcx
from .gpx_parser import parse_gpx
import io

def parse_file(uploaded_file):
    name = uploaded_file.name.lower()
    content = io.BytesIO(uploaded_file.read())
    content.seek(0)

    if name.endswith(".fit"):
        return parse_fit(content)
    elif name.endswith(".tcx"):
        return parse_tcx(content)
    elif name.endswith(".gpx"):
        return parse_gpx(content)
    else:
        return None

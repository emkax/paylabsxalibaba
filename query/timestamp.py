from imports import *

def generate_timestamp(tz_offset=7):
    tz = timezone(timedelta(hours=tz_offset))
    now = datetime.now(tz)
    # Format with milliseconds (.XXX)
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}" + now.strftime("%z")
    return timestamp[:-2] + ":" + timestamp[-2:]

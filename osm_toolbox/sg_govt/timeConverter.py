from datetime import datetime, timedelta


class DATETIME_FORMATS():
    ISO_8601_TZ = "%Y/%m/%d %H:%M:%S%z"
    # YYYY/MM/DD HH:MM:SS+TZTZ
    CONCAT_DATETIME = "%Y%m%d%H%M%S%z"
    # YYYYMMDDHHMMSSTZTZ used in ref data


def datetime_to_timestamp(dt: datetime) -> str:
    # convert timestamps from datetime object to YYYY/mm/dd HH:MM:ss+zone
    return dt.strftime(DATETIME_FORMATS.ISO_8601_TZ)


def timestamp_to_datetime(st: str) -> datetime:
    # convert timestamps from YYYY/mm/dd HH:MM:ss+zone to datetime object
    return datetime.strptime(st, DATETIME_FORMATS.ISO_8601_TZ)


def ref_to_datetime(st: str) -> datetime:
    # convert ref_data timestamps to UTC datetime object
    return datetime.strptime(f"{st}+0000", DATETIME_FORMATS.CONCAT_DATETIME) - timedelta(hours=8)


def ref_to_timestamp(st: str) -> str:
    # convert ref data to standard timestamp
    return datetime_to_timestamp(ref_to_datetime(st))

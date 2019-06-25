# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import chardet
import time


def _read_binary_file(file):
    if not file:
        return []
    data = base64.b64decode(file)
    separador = ''
    if data.find(b'\r') > -1:
        separador = b'\r'
    data_lines = data.split(separador)
    return data_lines


def _format_info(info):
    encoding_dict = chardet.detect(info)
    return info.decode(encoding_dict.get('encoding') or 'windows-1252').strip()


def _convert_time_str_to_float(time_str):
    if not time_str or time_str.find(':') == -1:
        return 0.0
    try:
        hour = time.strptime(time_str, '%H:%M')
        return (
            float(time.strftime('%H', hour)) +
            (float(time.strftime('%M', hour)) / 60.0))
    except Exception:
        hour = time_str.split(':')
        return float(hour[0]) + (float(hour[1]) / 60.0)

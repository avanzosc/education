# Copyright 2019 Oihane Crucelaegui - AvanzOSC
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import chardet


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

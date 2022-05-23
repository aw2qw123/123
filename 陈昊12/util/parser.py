import re


def mobile(mobile_str):
    if re.match(r'^1[3-9]\d{9}$', mobile_str):
        return mobile_str
    else:
        raise ValueError(f'{mobile_str} mobile is not valid')


def code(code_str):
    if re.match(r'^\d{6}$', code_str):
        return code_str
    else:
        raise ValueError(f'{code_str} code is not valid')




from typing import Dict

from metaprogramming.create_new_step import get_api_function_params
from metaprogramming.utils.code_utils import CLOSE_BRACKET, OPEN_BRACKET
from metaprogramming.utils.path_utils import (get_api_folder, get_src_folder,
                                              write_python_code_file)
from metaprogramming.utils.user_input_utils import read_params

API_PY_IMPORT_MARKER = '# AUTOGENERATED LINE: API.PY IMPORT (DO NOT DELETE)'
API_PY_CALL_MARKER = '# AUTOGENERATED LINE: API.PY CALL (DO NOT DELETE)'
API_TSX_GET_MARKER = '// AUTOGENERATED LINE: API GET (DO NOT DELETE)'



def get_api_call_python_code_params(params: Dict[str, str]) -> str:
    params_code = ""

    for name, type in params.items():
        params_code += f'    {name}: {type} = params[\'{name}\']'

    return params_code

def get_api_call_python_code_result_params(result_params: Dict[str, str]) -> str:
    result_params_code = ""

    for name in result_params:
        result_params_code += f'    \'{name}\': None,'

    return result_params_code

def get_api_call_python_code(name: str, params: Dict[str, str], result_params: Dict[str, str]) -> str:
    return f"""#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.

import json
from typing import Any, Dict
from mitosheet.types import StepsManagerType


def {name}(params: Dict[str, Any], steps_manager: StepsManagerType) -> str:
    {get_api_call_python_code_params(params)}

    # TODO: Implement the call

    return json.dumps({OPEN_BRACKET}
        {get_api_call_python_code_result_params(result_params)}
    {CLOSE_BRACKET})
"""

def write_to_api_py_file(name: str) -> None:
    path_to_api_py = get_api_folder() / 'api.py'

    with open(path_to_api_py, 'r') as f:
        code = f.read()
        code = code.replace(API_PY_IMPORT_MARKER, f"from mitosheet.api.{name} import {name}\n{API_PY_IMPORT_MARKER}")
        code = code.replace(API_PY_CALL_MARKER, f"""elif event["type"] == "{name}":
            result = {name}(params, steps_manager)\n    {API_PY_CALL_MARKER}""")

    with open(path_to_api_py, 'w') as f:
        f.write(code)

def get_typescript_api_code(name: str, params: Dict[str, str], result_params: Dict[str, str]) -> str:
    ts_function_name = "get" + "".join([s.title() for (idx, s) in enumerate(name.split('_')) if idx != 0])
    params_type = F"{OPEN_BRACKET}{get_api_function_params(params)}{CLOSE_BRACKET}"
    result_params_type = F"{OPEN_BRACKET}{get_api_function_params(result_params)}{CLOSE_BRACKET}"

    return f"""
    async {ts_function_name}(params: {params_type}): Promise<{result_params_type} | undefined> {OPEN_BRACKET}

        const resultString = await this.send<string>({OPEN_BRACKET}
            'event': 'api_call',
            'type': '{name}',
            'params': params
        {CLOSE_BRACKET}, {OPEN_BRACKET}{CLOSE_BRACKET})

        if (resultString !== undefined && resultString !== '') {OPEN_BRACKET}
            return JSON.parse(resultString);
        {CLOSE_BRACKET}
        return undefined;
    {CLOSE_BRACKET}"""

def write_to_typscript_api(name: str, params: Dict[str, str], result_params: Dict[str, str]) -> None:
    path_to_api_tsx = get_src_folder() / 'jupyter' / 'api.tsx'

    with open(path_to_api_tsx, 'r') as f:
        code = f.read()
        code = code.replace(API_TSX_GET_MARKER, get_typescript_api_code(name, params, result_params) + f'\n\n    {API_TSX_GET_MARKER}')

    with open(path_to_api_tsx, 'w') as f:
        f.write(code)



def create_new_api_call(name: str) -> None:
    params = read_params()
    result_params = read_params('result param names')

    api_call_path = get_api_folder() / f"{name}.py"
    api_code = get_api_call_python_code(name, params, result_params)

    # Create the file
    write_python_code_file(api_call_path, api_code)

    # Write it to the API list
    write_to_api_py_file(name)

    # Write the typescript to the API
    write_to_typscript_api(name, params, result_params)
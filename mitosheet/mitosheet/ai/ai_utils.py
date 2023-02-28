

import ast
import os
from typing import List, Optional

def is_open_ai_credentials_available() -> bool:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    return OPENAI_API_KEY is not None

def get_import_lines_to_add(code: str) -> List[str]:
    lines = []
    if 'np.' in code and 'import numpy as np' not in code:
        lines.append('import numpy as np')
    if 'pd.' in code and 'import pandas as pd' not in code:
        lines.append('import pandas as pd')
    return lines


def fix_up_missing_imports(code: str) -> str:
    import_lines = get_import_lines_to_add(code)

    for import_line in import_lines:
        code = f'{import_line}\n' + code
        
    return code

def get_code_string_from_last_expression(code: str, last_expression: ast.stmt) -> str:
    code_lines = code.splitlines()
    # NOTE; these are 1-indexed, and we need make sure we add one if they are the same, so that 
    # we can actually get the line with our slice. Also, on earlier versions of Python, the end_lineno is
    # not defined; thus, we must access it through the attribute getter
    lineno = last_expression.lineno - 1
    end_lineno = last_expression.__dict__.get('end_lineno', None)
    if end_lineno is not None:
        end_lineno -= 1
        if end_lineno == lineno:
            end_lineno += 1
    relevant_lines = code_lines[lineno:end_lineno] 
    return "\n".join(relevant_lines)

def fix_final_dataframe_name(code: str, new_df_name: str, is_series: bool) -> str:
    ast_before = ast.parse(code)
    last_expression = ast_before.body[-1]

    last_expression_string = get_code_string_from_last_expression(code, last_expression)

    if not is_series:
        # If it's a dataframe, just add the name
        code = code.replace(last_expression_string, f'{new_df_name} = {last_expression_string}')
    else:
        # If it's a series, create a dataframe
        code = code.replace(last_expression_string, f'series = {last_expression_string}\n{new_df_name} = pd.DataFrame(series, index=series.index)')

    return code

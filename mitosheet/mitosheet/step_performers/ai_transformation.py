
#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.

import pandas as pd
from time import perf_counter
from typing import Any, Dict, List, Optional, Set, Tuple
from mitosheet.ai.ai_utils import fix_final_dataframe_name, fix_up_missing_imports
from mitosheet.code_chunks.code_chunk import CodeChunk
from mitosheet.code_chunks.ai_transformation_code_chunk import AITransformationCodeChunk

from mitosheet.state import State
from mitosheet.step_performers.step_performer import StepPerformer
from mitosheet.step_performers.utils import get_param
from mitosheet.ai.recon import exec_and_get_new_state_and_result

class AITransformationStepPerformer(StepPerformer):
    """
    Allows you to execute an arbitrary chunk of code, generated by an AI.
    """

    @classmethod
    def step_version(cls) -> int:
        return 1

    @classmethod
    def step_type(cls) -> str:
        return 'ai_transformation'

    @classmethod
    def execute(cls, prev_state: State, params: Dict[str, Any]) -> Tuple[State, Optional[Dict[str, Any]]]:
        # We don't use any of these parameters, but we keep them for clarity, and we don't want to remove them accidently
        user_input: str = get_param(params, 'user_input')
        prompt_version: str = get_param(params, 'prompt_version')
        prompt: str = get_param(params, 'prompt')
        completion: str = get_param(params, 'completion')
        edited_completion: str = get_param(params, 'edited_completion')

        pandas_start_time = perf_counter()
        post_state, last_line_value, frontend_result = exec_and_get_new_state_and_result(prev_state, edited_completion)
        pandas_processing_time = perf_counter() - pandas_start_time

        if isinstance(last_line_value, pd.DataFrame) or isinstance(last_line_value, pd.Series):
            final_code = fix_final_dataframe_name(edited_completion, post_state.df_names[-1], isinstance(last_line_value, pd.Series))
        else:
            final_code = edited_completion

        return post_state, {
            'pandas_processing_time': pandas_processing_time,
            'result': frontend_result,
            'final_code': final_code
        }

    @classmethod
    def transpile(
        cls,
        prev_state: State,
        params: Dict[str, Any],
        execution_data: Optional[Dict[str, Any]],
    ) -> List[CodeChunk]:
        return [
            AITransformationCodeChunk(
                prev_state, 
                get_param(params, 'user_input'),
                get_param(execution_data if execution_data is not None else {}, 'final_code')
            )
        ]

    @classmethod
    def get_modified_dataframe_indexes(cls, params: Dict[str, Any]) -> Set[int]:
        return set() # NOTE: We act as though we modify all sheet indexes, as we can't easily figure out what we do modify

    @classmethod
    def get_created_dataframe_indexes(cls, params: Dict[str, Any]) -> Set[int]:
        return {-1} # NOTE: We act as though we create all sheet indexes, as we can't easily figure out what we do modify
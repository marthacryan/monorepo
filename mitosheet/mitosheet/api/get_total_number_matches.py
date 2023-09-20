#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
import re
import pandas as pd
from typing import Any, Dict
from mitosheet.types import StepsManagerType


def get_total_number_matches(params: Dict[str, Any], steps_manager: StepsManagerType) -> str:
    """
    Finds the number of matches to a given search value in the dataframe.
    """
    sheet_index = params['sheet_index']
    search_value = params['search_value']
    df = steps_manager.dfs[sheet_index]

    # First, generate a count for each value in the dataframe:
    unique_value_counts = df.value_counts()

    # Then, filter for the search value:
    matches = unique_value_counts.filter(regex=re.compile(search_value, re.IGNORECASE), axis=0)

    # Then, sum the matches:
    total_number_matches = matches.sum()

    # Find the indices of cells containing the search value
    indices = [{'row': i, 'col': j} for i in range(min(1500,len(df.index))) for j in range(len(df.columns)) if (re.search(re.compile(search_value, re.IGNORECASE),str(df.iloc[i, j])) is not None)]
    return {'total_number_matches': total_number_matches, 'matches': indices }
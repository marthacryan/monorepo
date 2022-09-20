#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
"""
Contains tests for Melt
"""

import pandas as pd
import pytest
from mitosheet.tests.test_utils import create_mito_wrapper_dfs

MELT_TESTS = [
    (
        [
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]})
        ],
        0, 
        ['product_id', 'description'], 
        [pd.to_datetime('1-1-2020'), pd.to_datetime('1-2-2020')],
        [
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]}),
            pd.DataFrame({'product_id': [1, 2, 1, 2], 'description': ["a cat", "a bat", "a cat", "a bat"], 'variable': pd.to_datetime(['1-1-2020', '1-1-2020', '1-2-2020', '1-2-2020']), 'value': [0, 1, 0, 2]})
        ]
    ),
    (
        [
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]})
        ],
        0, 
        ['product_id', 'description'], 
        [pd.to_datetime('1-1-2020')],
        [
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]}),
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], 'variable': pd.to_datetime(['1-1-2020', '1-1-2020']), 'value': [0, 1]})
        ]
    ),
    (
        [
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]})
        ],
        0, 
        ['product_id', 'description'], 
        ['product_id', pd.to_datetime('1-1-2020')],
        [
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]}),
            pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], 'variable': pd.to_datetime(['1-1-2020', '1-1-2020']), 'value': [0, 1]})
        ]
    ),
    (
        [
            pd.DataFrame({'product_id': [1, None], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]})
        ],
        0, 
        ['product_id', 'description'], 
        ['product_id', pd.to_datetime('1-1-2020')],
        [
            pd.DataFrame({'product_id': [1, None], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]}),
            pd.DataFrame({'product_id': [1, None], 'description': ["a cat", "a bat"], 'variable': pd.to_datetime(['1-1-2020', '1-1-2020']), 'value': [0, 1]})
        ]
    ),
]
@pytest.mark.parametrize("input_dfs, sheet_index, id_vars, value_vars, output_dfs", MELT_TESTS)
def test_melt(input_dfs, sheet_index, id_vars, value_vars, output_dfs):
    mito = create_mito_wrapper_dfs(*input_dfs)

    mito.melt(sheet_index, id_vars, value_vars)

    assert len(mito.dfs) == len(output_dfs)
    for actual, expected in zip(mito.dfs, output_dfs):
        assert actual.equals(expected)

def test_melt_with_empty_values_is_empty():
    mito = create_mito_wrapper_dfs(pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]}))

    mito.melt(0, ['product_id', 'description'], [])

    assert len(mito.dfs) == 2
    assert mito.dfs[1].empty

def test_melt_overwritten_by_delete():
    mito = create_mito_wrapper_dfs(pd.DataFrame({'product_id': [1, 2], 'description': ["a cat", "a bat"], pd.to_datetime('1-1-2020'): [0, 1], pd.to_datetime('1-2-2020'): [0, 2]}))
    mito.melt(
        0, 
        ['product_id', 'description'], 
        [pd.to_datetime('1-1-2020'), pd.to_datetime('1-2-2020')]
    )
    mito.delete_dataframe(1)
    assert len(mito.transpiled_code) == 0 
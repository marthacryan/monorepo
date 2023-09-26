#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
import os
import pandas as pd
from mitosheet.code_chunks.step_performers.import_steps.simple_import_code_chunk import DEFAULT_DECIMAL

from mitosheet.tests.test_utils import create_mito_wrapper
from mitosheet.tests.decorators import pandas_post_1_only, pandas_post_1_4_only, python_post_3_6_only

TEST_FILE = 'file.xlsx'
TEST_FILE_XLSM = 'file.xlsm'


@pandas_post_1_only
@python_post_3_6_only
def test_can_import_a_single_excel():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    df.to_excel(TEST_FILE, index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE, ['Sheet1'], True, 0, DEFAULT_DECIMAL)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert mito.curr_step.step_type == 'excel_import'
    assert len(mito.dfs) == 1
    assert mito.dfs[0].equals(df)
    assert mito.df_names == ['Sheet1']

    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_with_no_headers_and_skiprows():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    df.to_excel(TEST_FILE, index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE, ['Sheet1'], False, 2, DEFAULT_DECIMAL)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert mito.curr_step.step_type == 'excel_import'
    assert len(mito.dfs) == 1
    assert mito.dfs[0].equals(pd.DataFrame({
        0: [2, 3], 1: [3, 4]
    }))
    assert mito.df_names == ['Sheet1']

    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_multiple_sheets():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE, ['Sheet1', 'Sheet2'], True, 0)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert mito.curr_step.step_type == 'excel_import'
    assert len(mito.dfs) == 2
    assert mito.dfs[0].equals(df)
    assert mito.dfs[1].equals(df)
    assert mito.df_names == ['Sheet1', 'Sheet2']
    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_multiple_sheets_xlsm():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE_XLSM) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE_XLSM, ['Sheet1', 'Sheet2'], True, 0)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert mito.curr_step.step_type == 'excel_import'
    assert len(mito.dfs) == 2
    assert mito.dfs[0].equals(df)
    assert mito.dfs[1].equals(df)
    assert mito.df_names == ['Sheet1', 'Sheet2']
    # Remove the test file
    os.remove(TEST_FILE_XLSM)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_multiple_sheets_then_delete_no_optimize():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE, ['Sheet1', 'Sheet2'], True, 0)
    mito.delete_dataframe(0)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert len(mito.dfs) == 1
    assert mito.dfs[0].equals(df)
    assert mito.df_names == ['Sheet2']
    assert len(mito.transpiled_code) != 0
    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_multiple_sheets_then_delete_last_no_optimize():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE, ['Sheet1', 'Sheet2'], True, 0)
    mito.delete_dataframe(1)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert len(mito.dfs) == 1
    assert mito.dfs[0].equals(df)
    assert mito.df_names == ['Sheet1']
    assert len(mito.transpiled_code) != 0
    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_multiple_sheets_then_multiple_deletes():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    # Create with no dataframes
    mito = create_mito_wrapper()
    # And then import just a test file
    mito.excel_import(TEST_FILE, ['Sheet1', 'Sheet2'], True, 0)
    mito.delete_dataframe(0)
    mito.delete_dataframe(0)

    # Make sure a step has been created, and that the dataframe is the correct dataframe
    assert len(mito.dfs) == 0
    assert mito.transpiled_code == []
    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_can_import_multiple_sheets_then_multiple_deletes_later_in_analysis():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    mito = create_mito_wrapper(df)

    mito.excel_import(TEST_FILE, ['Sheet1', 'Sheet2'], True, 0)
    mito.delete_dataframe(2)
    mito.delete_dataframe(1)

    assert len(mito.dfs) == 1
    assert mito.transpiled_code == []

    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_only
@python_post_3_6_only
def test_remove_multiple_one_by_one_does_not_optimize_till_all_gone():
    df = pd.DataFrame(data={'A': [1, 2, 3], 'B': [2, 3, 4]})
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='Sheet1', index=False)
        df.to_excel(writer, sheet_name='Sheet2', index=False)

    mito = create_mito_wrapper(df)

    mito.excel_import(TEST_FILE, ['Sheet1', 'Sheet2'], True, 0)
    mito.delete_dataframe(2)

    assert len(mito.dfs) == 2

    mito.delete_dataframe(1)

    assert mito.transpiled_code == []

    # Remove the test file
    os.remove(TEST_FILE)


@pandas_post_1_4_only
@python_post_3_6_only
def test_comma_decimal_excel_import():
    df_comma = pd.DataFrame({'KG': ['267,88', '458,99', '125,89', '1,55', '1']}) 
    df_result = pd.DataFrame({'KG': [267.88, 458.99, 125.89, 1.55, 1]}) 
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df_comma.to_excel(writer, sheet_name='Sheet1', index=False)

    mito = create_mito_wrapper()
    mito.excel_import(TEST_FILE, ['Sheet1'], True, 0, ',')
    
    assert mito.dfs[0].equals(df_result)

    # Remove the test file
    os.remove(TEST_FILE)

@pandas_post_1_4_only
@python_post_3_6_only
def test_only_creates_valid_python_variables():
    df = pd.DataFrame({'KG': [267.88, 458.99, 125.89, 1.55, 1]}) 
    with pd.ExcelWriter(TEST_FILE) as writer:  
        df.to_excel(writer, sheet_name='print', index=False)
        df.to_excel(writer, sheet_name='return', index=False)
        df.to_excel(writer, sheet_name='as', index=False)
        df.to_excel(writer, sheet_name='or', index=False)
        df.to_excel(writer, sheet_name='and', index=False)
        df.to_excel(writer, sheet_name='if', index=False)
        df.to_excel(writer, sheet_name='else', index=False)
        df.to_excel(writer, sheet_name='elif', index=False)
        df.to_excel(writer, sheet_name='for', index=False)
        df.to_excel(writer, sheet_name='while', index=False)
        df.to_excel(writer, sheet_name='in', index=False)
        df.to_excel(writer, sheet_name='is', index=False)
        df.to_excel(writer, sheet_name='not', index=False)
        df.to_excel(writer, sheet_name='None', index=False)
        df.to_excel(writer, sheet_name='True', index=False)
        df.to_excel(writer, sheet_name='False', index=False)
        df.to_excel(writer, sheet_name='break', index=False)
        df.to_excel(writer, sheet_name='continue', index=False)

    mito = create_mito_wrapper()
    mito.excel_import(TEST_FILE, [
        'print', 'return', 'as', 'or', 'and', 'if', 'else', 'elif', 'for', 'while', 'in', 'is', 'not', 'None', 'True', 'False', 'break', 'continue'
    ], True, 0, ',')
    
    assert mito.df_names == ['print_df', 'return_df', 'as_df', 'or_df', 'and_df', 'if_df', 'else_df', 'elif_df', 'for_df', 'while_df', 'in_df', 'is_df', 'not_df', 'None_df', 'True_df', 'False_df', 'break_df', 'continue_df']

    # Remove the test file
    os.remove(TEST_FILE)
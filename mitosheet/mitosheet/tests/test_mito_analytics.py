#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the GPL License.
"""
Contains tests to make sure that the mito analytics test is
performing correctly
"""

import pprint
import sys
import time
import pandas as pd
from mitosheet.column_headers import get_column_header_id
from mitosheet.enterprise.mito_config import MITO_CONFIG_LOG_SERVER_BATCH_INTERVAL, MITO_CONFIG_LOG_SERVER_URL, MITO_CONFIG_VERSION
from mitosheet.errors import MitoError
from mitosheet.telemetry.telemetry_utils import PRINT_LOGS
import pytest
from unittest.mock import patch
import os
import json
from mitosheet.tests.test_mito_config import delete_all_mito_config_environment_variables
from mitosheet.tests.test_utils import create_mito_wrapper, create_mito_wrapper_with_data
from mitosheet.types import FORMULA_ENTIRE_COLUMN_TYPE
from mitosheet.utils import get_new_id

try:
    from pandas import __version__ as pandas_version
except:
    pandas_version = 'no pandas'
try:
    # Format version_python as "3.8.5"
    version_python = '.'.join([str(x) for x in sys.version_info[:3]])
except:
    version_python = 'no python'

URL = "https://url?" 

def test_not_printing_logs():
    assert PRINT_LOGS is False

def test_log_uploader_single_edit_event():
    
    os.environ[MITO_CONFIG_VERSION] = "2"
    os.environ[MITO_CONFIG_LOG_SERVER_URL] =  f"{URL}"
    os.environ[MITO_CONFIG_LOG_SERVER_BATCH_INTERVAL] = "0"
    
    mito = create_mito_wrapper_with_data([123])

    with patch('requests.post') as mock_post:
        mito.add_column(0, 'B')

        print(mock_post.call_args_list)
        log_call = mock_post.call_args_list[0]

        # Get the URL from the log call
        actual_url = log_call[0][0]
        assert actual_url == URL

        # From the call object, get the payload 
        # that was passed to requests.post
        data = log_call[1]['data']
        log_payload = json.loads(data)[0]

        assert len(log_payload) == 9
        assert log_payload["params_sheet_index"] == 0
        assert log_payload["params_column_header"] is not None
        assert log_payload["params_column_header_index"] == -1
        assert log_payload["params_public_interface_version"] == 3
        assert log_payload["version_python"] == version_python
        assert log_payload["version_pandas"] == pandas_version
        assert log_payload["version_mito"] is not None
        assert log_payload["timestamp_gmt"] is not None
        assert log_payload["event"] == "add_column_edit"

    delete_all_mito_config_environment_variables()

def test_log_uploader_multiple_edit_events():
    
    os.environ[MITO_CONFIG_VERSION] = "2"
    os.environ[MITO_CONFIG_LOG_SERVER_URL] =  f"{URL}"
    os.environ[MITO_CONFIG_LOG_SERVER_BATCH_INTERVAL] = "1"
    
    mito = create_mito_wrapper_with_data([123])

    mito.add_column(0, 'B')
    mito.delete_columns(0, ['B'])

    # wait 1 second
    time.sleep(1)

    with patch('requests.post') as mock_post:

        mito.add_column(0, 'C')

        # Even though multiple events occured, there should be only one upload
        assert len(mock_post.call_args_list) == 1

        log_call = mock_post.call_args_list[0]

        # Get the URL from the log call
        actual_url = log_call[0][0]
        assert actual_url == URL

        # From the call object, get the payload 
        # that was passed to requests.post
        data = log_call[1]['data']
        add_column_log_event = json.loads(data)[0]

        assert len(add_column_log_event) == 9
        assert add_column_log_event["params_sheet_index"] == 0
        assert add_column_log_event["params_column_header"] is not None
        assert add_column_log_event["params_column_header_index"] == -1
        assert add_column_log_event["params_public_interface_version"] == 3
        assert add_column_log_event["version_python"] == version_python
        assert add_column_log_event["version_pandas"] == pandas_version
        assert add_column_log_event["version_mito"] is not None
        assert add_column_log_event["timestamp_gmt"] is not None
        assert add_column_log_event["event"] == "add_column_edit"

        delete_columns_log_event = json.loads(data)[1]
        print(delete_columns_log_event)
        assert len(delete_columns_log_event) == 8
        assert delete_columns_log_event["params_sheet_index"] == 0
        assert len(delete_columns_log_event["params_column_ids"]) == 1
        assert delete_columns_log_event["params_public_interface_version"] == 3
        assert delete_columns_log_event["version_python"] == version_python
        assert delete_columns_log_event["version_pandas"] == pandas_version
        assert delete_columns_log_event["version_mito"] is not None
        assert delete_columns_log_event["timestamp_gmt"] is not None
        assert delete_columns_log_event["event"] == "delete_column_edit"

    delete_all_mito_config_environment_variables()

def test_log_uploader_error_events():
    
    os.environ[MITO_CONFIG_VERSION] = "2"
    os.environ[MITO_CONFIG_LOG_SERVER_URL] =  f"{URL}"
    os.environ[MITO_CONFIG_LOG_SERVER_BATCH_INTERVAL] = "0"
    
    mito = create_mito_wrapper(pd.DataFrame({'A': [1, 2, 3]}))

    with patch('requests.post') as mock_post:

        mito.set_formula('=INVALID_FUNCTION()', 0, 'A')

        assert len(mock_post.call_args_list) == 1

        log_call = mock_post.call_args_list[0]

        # Get the URL from the log call
        actual_url = log_call[0][0]
        assert actual_url == URL

        # From the call object, get the payload 
        # that was passed to requests.post
        data = log_call[1]['data']
        log_event = json.loads(data)[0]

        assert len(log_event) == 13
        assert log_event["error_traceback"] is not None
        assert log_event["error_traceback_last_line"] is not None
        assert log_event["params_sheet_index"] == 0
        assert log_event["params_column_id"] is not None
        assert log_event["params_formula_label"] is not None
        assert log_event["params_index_labels_formula_is_applied_to"] is not None
        assert log_event["params_public_interface_version"] == 3
        assert log_event["params_new_formula"] == '=INVALID_FUNCTION()'
        assert log_event["version_python"] == version_python
        assert log_event["version_pandas"] == pandas_version
        assert log_event["version_mito"] is not None
        assert log_event["timestamp_gmt"] is not None
        assert log_event["event"] == "error"

    delete_all_mito_config_environment_variables()
    

def test_log_uploader_mitosheet_rendered():
    
    os.environ[MITO_CONFIG_VERSION] = "2"
    os.environ[MITO_CONFIG_LOG_SERVER_URL] = f"{URL}"
    os.environ[MITO_CONFIG_LOG_SERVER_BATCH_INTERVAL] = "0"
    
    mito = create_mito_wrapper(pd.DataFrame({'A': [1, 2, 3]}))

    with patch('requests.post') as mock_post:
        mito.mito_backend.receive_message({
            'params': {'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15'}, 
            'event': 'log_event', 
            'type': 'mitosheet_rendered', 
            'id': '_pt4wgfw0z'
        })

        assert len(mock_post.call_args_list) == 1

        log_call = mock_post.call_args_list[0]

        # Get the URL from the log call
        actual_url = log_call[0][0]
        assert actual_url == URL

        # From the call object, get the payload 
        # that was passed to requests.post
        data = log_call[1]['data']
        log_event = json.loads(data)[0]

        assert len(log_event) == 6
        assert log_event["params_user_agent"] == "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15"
        assert log_event["version_python"] == version_python
        assert log_event["version_pandas"] == pandas_version
        assert log_event["version_mito"] is not None
        assert log_event["timestamp_gmt"] is not None
        assert log_event["event"] == "mitosheet_rendered"

    delete_all_mito_config_environment_variables()



def test_log_uploader_long_interval_does_not_trigger_upload():
    
    os.environ[MITO_CONFIG_VERSION] = "2"
    os.environ[MITO_CONFIG_LOG_SERVER_URL] =  f"{URL}"
    os.environ[MITO_CONFIG_LOG_SERVER_BATCH_INTERVAL] = "100"
    
    mito = create_mito_wrapper(pd.DataFrame({'A': [1, 2, 3]}))

    with patch('requests.post') as mock_post:

        mito.add_column(0, 'B')
        mito.add_column(0, 'C')
        mito.add_column(0, 'D')

        assert len(mock_post.call_args_list) == 0

    delete_all_mito_config_environment_variables()

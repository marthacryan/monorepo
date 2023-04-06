

import os
import json
from mitosheet.tests.test_utils import create_mito_wrapper_dfs
import mitosheet.api.get_ai_completion as ai
from mitosheet.tests.decorators import requires_open_ai_credentials
from mitosheet.user.db import get_user_field, set_user_field
from mitosheet.user.schemas import UJ_AI_MITO_API_NUM_USAGES

@requires_open_ai_credentials
def test_get_ai_completion():
    mito = create_mito_wrapper_dfs()

    completion = ai.get_ai_completion({
        'user_input': 'test',
        'selection': None
    }, mito.mito_backend.steps_manager)

    try:
        assert json.loads(completion)['user_input'] == 'test'
        assert len(json.loads(completion)['prompt_version']) > 0
        assert len(json.loads(completion)['prompt']) > 0
        assert len(json.loads(completion)['completion']) > 0
    except:
        # This integrates with an external API, so if this doesn't work, we should get an error
        # We add this since this test is flakey
        assert len(json.loads(completion)['error']) > 0

def test_get_ai_completion_with_no_api_key_works():
    mito = create_mito_wrapper_dfs()

    if 'OPENAI_API_KEY' in os.environ:
        key = os.environ['OPENAI_API_KEY']
        del os.environ['OPENAI_API_KEY']
        num_usages = get_user_field(UJ_AI_MITO_API_NUM_USAGES)
    else:
        key = None
        num_usages = 0

    set_user_field(UJ_AI_MITO_API_NUM_USAGES, 0)

    completion = ai.get_ai_completion({
        'user_input': 'test',
        'selection': None
    }, mito.mito_backend.steps_manager)

    assert json.loads(completion)['user_input'] == 'test'
    assert len(json.loads(completion)['prompt_version']) > 0
    assert len(json.loads(completion)['prompt']) > 0
    assert len(json.loads(completion)['completion']) > 0

    if key is not None:
        os.environ['OPENAI_API_KEY'] = key
    set_user_field(UJ_AI_MITO_API_NUM_USAGES, num_usages)

def test_get_ai_completion_with_no_api_key_errors_if_above_rate_limit():
    set_user_field(UJ_AI_MITO_API_NUM_USAGES, 20)

    mito = create_mito_wrapper_dfs()

    if 'OPENAI_API_KEY' in os.environ:
        key = os.environ['OPENAI_API_KEY']
        del os.environ['OPENAI_API_KEY']
        num_usages = get_user_field(UJ_AI_MITO_API_NUM_USAGES)
    else:
        key = None
        num_usages = 0

    # Reload it to refresh variables stored
    import importlib
    importlib.reload(ai)

    completion = ai.get_ai_completion({
        'user_input': 'test',
        'selection': None
    }, mito.mito_backend.steps_manager)

    assert 'You have used Mito AI 20 times.' in json.loads(completion)['error']


    if key is not None:
        os.environ['OPENAI_API_KEY'] = key
    set_user_field(UJ_AI_MITO_API_NUM_USAGES, num_usages)
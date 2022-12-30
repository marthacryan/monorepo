#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Saga Inc.
# Distributed under the terms of the The Mito Enterprise license.

from typing import Any, Dict, Optional
import os
from mitosheet.telemetry.telemetry_utils import log

# Note: Do not change these keys, we need them for looking up 
# the environment variables from previous mito_config_versions.
MITO_CONFIG_KEY_VERSION = 'MITO_CONFIG_VERSION'
MITO_CONFIG_KEY_SUPPORT_EMAIL = 'MITO_CONFIG_SUPPORT_EMAIL'
MITO_CONFIG_KEY_CODE_SNIPPETS_SUPPORT_EMAIL = 'MITO_CONFIG_CODE_SNIPPETS_SUPPORT_EMAIL'
MITO_CONFIG_KEY_CODE_SNIPPETS_VERSION = 'MITO_CONFIG_CODE_SNIPPETS_VERSION'
MITO_CONFIG_KEY_CODE_SNIPPETS_URL = 'MITO_CONFIG_CODE_SNIPPETS_URL'

# Note: The below keys can change since they are not set by the user.
MITO_CONFIG_KEY_CODE_SNIPPETS = 'MITO_CONFIG_CODE_SNIPPETS'

# The default values to use if the mec does not define them
DEFAULT_MITO_CONFIG_SUPPORT_EMAIL = 'founders@sagacollab.com'
DEFAULT_MITO_CONFIG_CODE_SNIPPETS_SUPPORT_EMAIL = 'founders@sagacollab.com'

def upgrade_mec_1_to_2(mec: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts mec of shape:
    {
        'MITO_CONFIG_VERSION': '1',
        'MITO_CONFIG_SUPPORT_EMAIL': 'support@mito.com'
    }
    
    into: 

    {
        'MITO_CONFIG_VERSION': '2',
        'MITO_CONFIG_SUPPORT_EMAIL': 'support@mito.com',
        'MITO_CONFIG_CODE_SNIPPETS_SUPPORT_EMAIL': None,
        'MITO_CONFIG_CODE_SNIPPETS_VERSION': None,
        'MITO_CONFIG_CODE_SNIPPETS_URL': None
    }
    """
    return {
        MITO_CONFIG_KEY_VERSION: '2',
        MITO_CONFIG_KEY_SUPPORT_EMAIL: mec[MITO_CONFIG_KEY_SUPPORT_EMAIL],
        MITO_CONFIG_KEY_CODE_SNIPPETS_SUPPORT_EMAIL: None,
        MITO_CONFIG_KEY_CODE_SNIPPETS_VERSION: None,
        MITO_CONFIG_KEY_CODE_SNIPPETS_URL: None
    }

"""
When updating the MEC_VERSION, add a function here to update the previous mec to the new version. For example, 
if mec_version='3', mec_upgrade_functions should look like:
{
   '1': upgrade_mec_1_to_2,
   '2': upgrade_mec_2_to_3
}
To keep things simple for now, these upgrade functions just make sure that all of the keys are defined so 
that the functions below can set the correct default values and format the mec properly.
"""

mec_upgrade_functions: Dict[str, Any] = {
    '1': upgrade_mec_1_to_2
}

def upgrade_mito_enterprise_configuration(mec: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if mec is None:
        return None

    # So mypy tests recognize that mec is not None
    _mec = mec
    while _mec[MITO_CONFIG_KEY_VERSION] in mec_upgrade_functions:
        _mec = mec_upgrade_functions[_mec[MITO_CONFIG_KEY_VERSION]](_mec)

    return _mec

# Since Mito needs to look up individual environment variables, we need to 
# know the names of the variables associated with each mito config version. 
# To do so we store them as a list here. 
MEC_VERSION_KEYS = {
    '1': [MITO_CONFIG_KEY_VERSION, MITO_CONFIG_KEY_SUPPORT_EMAIL],
    '2': [
        MITO_CONFIG_KEY_VERSION, 
        MITO_CONFIG_KEY_SUPPORT_EMAIL, 
        MITO_CONFIG_KEY_CODE_SNIPPETS_SUPPORT_EMAIL, 
        MITO_CONFIG_KEY_CODE_SNIPPETS_VERSION,
        MITO_CONFIG_KEY_CODE_SNIPPETS_URL
    ]
}

def create_mec_from_environment_variables() -> Optional[Dict[str, Any]]:
    """
    Creates a Mito Enterprise Config object from the environment variables
    """
    config_version = os.environ.get(MITO_CONFIG_KEY_VERSION)

    if config_version is None:
        return None

    mec: Dict[str, Any] = {}
    for key in MEC_VERSION_KEYS[config_version]:
        mec[key] = os.environ.get(key)

    return mec

class MitoConfig:
    """
    The MitoConfig class is repsonsible for reading the settings from the 
    environment variables and returning them as the most updated version of the 
    mito_enterprise_configuration object that is used by the rest of the app. 

    If the environment variables does not exist or does not set every configuration option, 
    the MitoConfig class sets defaults. 
    """
    def __init__(self):
        mec_potentially_outdated = create_mec_from_environment_variables()
        self.mec = upgrade_mito_enterprise_configuration(mec_potentially_outdated)

        if self.mec is not None:
            log('loaded_mito_enterprise_config')

    def get_version(self) -> str:
        if self.mec is None or self.mec[MITO_CONFIG_KEY_VERSION] is None:
            return '2' # NOTE: update this to be the most recent version, when we bump the version
        return self.mec[MITO_CONFIG_KEY_VERSION]

    def get_support_email(self) -> str:
        if self.mec is None or self.mec[MITO_CONFIG_KEY_SUPPORT_EMAIL] is None:
            return DEFAULT_MITO_CONFIG_SUPPORT_EMAIL
        return self.mec[MITO_CONFIG_KEY_SUPPORT_EMAIL]

    def get_code_snippets_version(self) -> str:
        if self.mec is None or self.mec[MITO_CONFIG_KEY_CODE_SNIPPETS_VERSION] is None:
            return None
        return self.mec[MITO_CONFIG_KEY_CODE_SNIPPETS_VERSION]

    def get_code_snippets_url(self) -> Optional[str]:
        if self.mec is None or self.mec[MITO_CONFIG_KEY_CODE_SNIPPETS_URL] is None:
            return None
        return self.mec[MITO_CONFIG_KEY_CODE_SNIPPETS_URL]

    def get_code_snippets_support_email(self) -> str:
        if self.mec is None or self.mec[MITO_CONFIG_KEY_CODE_SNIPPETS_SUPPORT_EMAIL] is None:
            return DEFAULT_MITO_CONFIG_CODE_SNIPPETS_SUPPORT_EMAIL
        return self.mec[MITO_CONFIG_KEY_CODE_SNIPPETS_SUPPORT_EMAIL]

    def get_code_snippets(self) -> Dict[str, Optional[str]]:
        return {
            MITO_CONFIG_KEY_CODE_SNIPPETS_VERSION: self.get_code_snippets_version(),
            MITO_CONFIG_KEY_CODE_SNIPPETS_URL: self.get_code_snippets_url(),
            MITO_CONFIG_KEY_CODE_SNIPPETS_SUPPORT_EMAIL: self.get_code_snippets_support_email(),
        }

    # Add new mito configuration options here ...

    def get_mito_config(self) -> Dict[str, Any]:
        return {
            MITO_CONFIG_KEY_VERSION: self.get_version(),
            MITO_CONFIG_KEY_SUPPORT_EMAIL: self.get_support_email(),
            MITO_CONFIG_KEY_CODE_SNIPPETS: self.get_code_snippets()
        }


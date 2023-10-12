from mitosheet.tests.decorators import requires_streamlit
from mitosheet.streamlit.v1.spreadsheet import MitoAnalysis
import pytest
import pandas as pd

sample_code = f"""from mitosheet.public.v3 import *
import pandas as pd

def function(file_name_import_csv_0, file_name_import_excel_0, file_name_export_csv_0, file_name_export_excel_0):
    txt = pd.read_csv(file_name_import_csv_0)
    
    sheet_df_dictonary = pd.read_excel(file_name_import_excel_0, engine='openpyxl', sheet_name=[
        'Sheet1'
    ], skiprows=0)
    Sheet1 = sheet_df_dictonary['Sheet1']
    
    txt.to_csv(file_name_export_csv_0, index=False)
    
    with pd.ExcelWriter(file_name_export_excel_0, engine="openpyxl") as writer:
        Sheet1.to_excel(writer, sheet_name="Sheet1", index=False)
    
    return txt, Sheet1
"""

ANALYSIS_TESTS = [
    (
        sample_code,
        None,
        sample_code
    )
]

@requires_streamlit
@pytest.mark.parametrize('code, code_options, fully_parameterized_function', ANALYSIS_TESTS)
def test_mito_analysis(tmp_path, code, code_options, fully_parameterized_function):
    tmp_file1 = str(tmp_path / 'txt.csv')
    tmp_file2 = str(tmp_path / 'file.xlsx')
    tmp_exportfile1 = str(tmp_path / 'export.csv')
    tmp_exportfile2 = str(tmp_path / 'export.xlsx')
    df1 = pd.DataFrame({'A': [1], 'B': [2]})
    df1.to_csv(tmp_file1, index=False)
    df1.to_excel(tmp_file2, index=False)
    param_metadata = [
        {
            'initial_value': f"r'{tmp_file1}'",
            'type': 'file_name',
            'subtype': 'file_name_import_csv',
            'name': 'file_name_import_csv_0',
            'required': False
        },
        {
            'initial_value': f"r'{tmp_file2}'",
            'type': 'file_name',
            'subtype': 'file_name_import_excel',
            'name': 'file_name_import_excel_0',
            'required': False
        },
        {
            'initial_value': f"r'{tmp_exportfile1}'",
            'type': 'file_name',
            'subtype': 'file_name_export_csv',
            'name': 'file_name_export_csv_0',
            'required': False
        },
        {
            'initial_value': f"r'{tmp_exportfile2}'",
            'type': 'file_name',
            'subtype': 'file_name_export_excel',
            'name': 'file_name_export_excel_0',
            'required': False
        }
    ]
    
    analysis = MitoAnalysis(code, code_options, fully_parameterized_function, param_metadata)
    result = analysis.run()
    assert result is not None
    pd.testing.assert_frame_equal(result[0], df1)
    pd.testing.assert_frame_equal(result[1], df1)

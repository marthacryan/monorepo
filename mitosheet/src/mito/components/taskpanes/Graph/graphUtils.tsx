// Helper function for creating default graph params. Defaults to a Bar chart, 
import React from "react"
import { ColumnID, ColumnIDsMap, EditorState, GraphDataArray, GraphDataBackend, GraphDataFrontend, GraphID, GraphParamsBackend, GraphParamsFrontend, SheetData, UIState } from "../../../types"
import { getDisplayColumnHeader } from "../../../utils/columnHeaders"
import { isDatetimeDtype, isNumberDtype } from "../../../utils/dtypes"
import { convertStringToFloatOrUndefined } from "../../../utils/numbers"
import { convertToStringOrUndefined } from "../../../utils/strings"
import DropdownItem from "../../elements/DropdownItem"
import { GRAPHS_THAT_HAVE_BARMODE, GRAPHS_THAT_HAVE_HISTFUNC, GRAPHS_THAT_HAVE_LINE_SHAPE, GRAPHS_THAT_HAVE_POINTS, GraphType, GRAPH_SAFETY_FILTER_CUTOFF } from "./GraphSetupTab"
import { MitoAPI, getRandomId } from "../../../api/api"
import { TaskpaneType } from "../taskpanes"
import { ModalEnum } from "../../modals/modals"

// Note: these should match the constants in Python as well
const DO_NOT_CHANGE_PAPER_BGCOLOR_DEFAULT = '#FFFFFF'
const DO_NOT_CHANGE_PLOT_BGCOLOR_DEFAULT = '#E6EBF5'
const DO_NOT_CHANGE_TITLE_FONT_COLOR_DEFAULT = '#2F3E5D'

/**
 * Returns the default axis column ids for a given graph type and selected column ids.
 * Used to set the default axis column ids based on the current selection when creating a new graph.
 */
const getAxisColumnIDs = (sheetData: SheetData, graphType?: GraphType, selectedColumnIds?: ColumnID[]): {
    x_axis_column_ids: ColumnID[],
    y_axis_column_ids: ColumnID[]
} => {
    if (selectedColumnIds === undefined || selectedColumnIds.length === 0) {
        return {
            x_axis_column_ids: [],
            y_axis_column_ids: []
        }
    }
    if (selectedColumnIds.length === 1) {
        return {
            x_axis_column_ids: [],
            y_axis_column_ids: selectedColumnIds
        }
    }
    if (graphType === GraphType.SCATTER) {
        return {
            x_axis_column_ids: [selectedColumnIds[0]],
            y_axis_column_ids: selectedColumnIds.slice(1)
        }
    } else {
        if (!isNumberDtype(sheetData.columnDtypeMap[selectedColumnIds[0]])) {
            return {
                x_axis_column_ids: [selectedColumnIds[0]],
                y_axis_column_ids: selectedColumnIds.slice(1)
            }
        } else {
            return {
                x_axis_column_ids: [],
                y_axis_column_ids: selectedColumnIds
            }
        }
    }
}


// unless a graph type is provided
export const getDefaultGraphParams = (sheetDataArray: SheetData[], sheetIndex: number, graphID: GraphID, graphType?: GraphType, selectedColumnIds?: ColumnID[]): GraphParamsFrontend => {
    graphType = graphType || GraphType.BAR
    const axis_column_ids = getAxisColumnIDs(sheetDataArray[sheetIndex], graphType, selectedColumnIds)
    return {
        graphID: graphID ?? getRandomId(),
        graphPreprocessing: {
            safety_filter_turned_on_by_user: true
        },
        graphCreation: {
            graph_type: graphType,
            sheet_index: sheetIndex,
            color: undefined,
            facet_col_column_id: undefined,
            facet_row_column_id: undefined,
            facet_col_wrap: undefined,
            facet_col_spacing: undefined,
            facet_row_spacing: undefined,
            ...axis_column_ids,
            // Params that are only available to some graph types
            points: GRAPHS_THAT_HAVE_POINTS.includes(graphType) ? 'outliers' : undefined,
            line_shape: GRAPHS_THAT_HAVE_LINE_SHAPE.includes(graphType) ? 'linear' : undefined,
            nbins: undefined,
            histnorm: undefined,
            histfunc: GRAPHS_THAT_HAVE_HISTFUNC.includes(graphType) ? 'count' : undefined
        },
        graphStyling: {
            title: {
                title: undefined,
                visible: true,
                title_font_color: DO_NOT_CHANGE_TITLE_FONT_COLOR_DEFAULT
            },
            xaxis: {
                title: undefined,
                visible: true,
                title_font_color: DO_NOT_CHANGE_TITLE_FONT_COLOR_DEFAULT,
                type: undefined,
                showgrid: true,
                gridwidth: undefined,
                rangeslider: {
                    visible: true,
                },
            },
            yaxis: {
                title: undefined,
                visible: true,
                title_font_color: DO_NOT_CHANGE_TITLE_FONT_COLOR_DEFAULT,
                type: undefined,
                showgrid: true,
                gridwidth: undefined,
            },
            showlegend: true,
            legend: {
                title: {
                    text: undefined
                },
                orientation: 'v',
                x: undefined, 
                y: undefined,
            },
            paper_bgcolor: DO_NOT_CHANGE_PAPER_BGCOLOR_DEFAULT,
            plot_bgcolor: DO_NOT_CHANGE_PLOT_BGCOLOR_DEFAULT,

            // Params that are only available to some graph types
            barmode: GRAPHS_THAT_HAVE_BARMODE.includes(graphType) ? 'group' : undefined,
            barnorm: undefined,
        }
    }
}



// Helper function for getting the default safety filter status
export const getDefaultSafetyFilter = (sheetDataArray: SheetData[], sheetIndex: number): boolean => {
    return sheetDataArray[sheetIndex] === undefined || sheetDataArray[sheetIndex].numRows > GRAPH_SAFETY_FILTER_CUTOFF
}

// Returns a list of dropdown items. Selecting them sets the color attribute of the graph.
// Option 'None' always comes first.
export const getColorDropdownItems = (
    graphSheetIndex: number,
    columnIDsMapArray: ColumnIDsMap[],
    columnDtypesMap: Record<string, string>,
    setColor: (columnID: ColumnID | undefined) => void,
): JSX.Element[] => {
    const NoneOption = [(
        <DropdownItem
            key='None'
            title='None'
            onClick={() => setColor(undefined)}
        />
    )]
    
    const columnDropdownItems = Object.keys(columnIDsMapArray[graphSheetIndex] || {}).map(columnID => {
        const columnHeader = columnIDsMapArray[graphSheetIndex][columnID];

        // Plotly doesn't support setting the color as a date series, so we disable date series dropdown items
        const disabled = isDatetimeDtype(columnDtypesMap[columnID])
        return (
            <DropdownItem
                key={columnID}
                title={getDisplayColumnHeader(columnHeader)}
                onClick={() => setColor(columnID)}
                disabled={disabled}
                subtext={disabled ? 'Dates cannot be used as the color breakdown property' : ''}
                hideSubtext
                displaySubtextOnHover
            />
        )
    })

    return NoneOption.concat(columnDropdownItems)
}

export const getGraphTypeFullName = (graphType: GraphType): string => {
    switch(graphType) {
        case GraphType.BAR: return 'Bar chart'
        case GraphType.BOX: return 'Box plot'
        case GraphType.DENSITY_CONTOUR: return 'Density contour'
        case GraphType.DENSITY_HEATMAP: return 'Density heatmap'
        case GraphType.ECDF: return 'ECDF'
        case GraphType.HISTOGRAM: return 'Histogram'
        case GraphType.LINE: return 'Line chart'
        case GraphType.SCATTER: return 'Scatter plot'
        case GraphType.STRIP: return 'Strip plot'
        case GraphType.VIOLIN: return 'Violin plot'
    }
}

export const convertBackendtoFrontendGraphData = (graphDataBackend: GraphDataBackend): GraphDataFrontend => {
    return {
        graphID: graphDataBackend.graph_id,
        graphOutput: graphDataBackend.graph_output,
        graphTabName: graphDataBackend.graph_tab_name,
    }
}

export const convertFrontendtoBackendGraphData = (graphDataFrontend: GraphDataFrontend): GraphDataBackend => {
    return {
        graph_id: graphDataFrontend.graphID,
        graph_output: graphDataFrontend.graphOutput,
        graph_tab_name: graphDataFrontend.graphTabName,
    }
}

export const convertFrontendtoBackendGraphParams = (graphParamsFrontend: GraphParamsFrontend): GraphParamsBackend => {
    const graphCreationParams = graphParamsFrontend.graphCreation
    const graphStylingParams = graphParamsFrontend.graphStyling

    return {
        graph_id: graphParamsFrontend.graphID,
        graph_creation: {
            ...graphParamsFrontend.graphCreation,
            facet_col_wrap: convertStringToFloatOrUndefined(graphCreationParams.facet_col_wrap),
            facet_col_spacing: convertStringToFloatOrUndefined(graphCreationParams.facet_col_spacing),
            facet_row_spacing: convertStringToFloatOrUndefined(graphCreationParams.facet_row_spacing),
            nbins: convertStringToFloatOrUndefined(graphCreationParams.nbins),
        },
        graph_styling: {
            ...graphParamsFrontend.graphStyling,
            xaxis: {
                ...graphParamsFrontend.graphStyling.xaxis,
                gridwidth: convertStringToFloatOrUndefined(graphStylingParams.xaxis.gridwidth)
            },
            yaxis: {
                ...graphParamsFrontend.graphStyling.yaxis,
                gridwidth: convertStringToFloatOrUndefined(graphStylingParams.yaxis.gridwidth)
            },
            legend: {
                ...graphParamsFrontend.graphStyling.legend,
                x: convertStringToFloatOrUndefined(graphStylingParams.legend.x),
                y: convertStringToFloatOrUndefined(graphStylingParams.legend.y)
            }
        },
        graph_preprocessing: graphParamsFrontend.graphPreprocessing
    }
}

export const convertBackendtoFrontendGraphParams = (graphParamsBackend: GraphParamsBackend): GraphParamsFrontend => {
    const graphCreationParams = graphParamsBackend.graph_creation
    const graphStylingParams = graphParamsBackend.graph_styling

    return {
        graphID: graphParamsBackend.graph_id,
        graphCreation: {
            ...graphCreationParams,
            facet_col_wrap: convertToStringOrUndefined(graphCreationParams.facet_col_wrap),
            facet_col_spacing: convertToStringOrUndefined(graphCreationParams.facet_col_spacing),
            facet_row_spacing: convertToStringOrUndefined(graphCreationParams.facet_row_spacing),
            nbins: convertToStringOrUndefined(graphCreationParams.nbins)
        },
        graphStyling: {
            ...graphStylingParams,
            xaxis: {
                ...graphStylingParams.xaxis,
                gridwidth: convertToStringOrUndefined(graphStylingParams.xaxis.gridwidth)
            },
            yaxis: {
                ...graphStylingParams.yaxis,
                gridwidth: convertToStringOrUndefined(graphStylingParams.yaxis.gridwidth)
            },
            legend: {
                ...graphStylingParams.legend,
                x: convertToStringOrUndefined(graphStylingParams.legend.x),
                y: convertToStringOrUndefined(graphStylingParams.legend.y)
            }
        },
        graphPreprocessing: graphParamsBackend.graph_preprocessing
    }
}

export const openGraphEditor = 
    async (
        setEditorState: React.Dispatch<React.SetStateAction<EditorState | undefined>>,
        sheetDataArray: SheetData[],
        uiState: UIState,
        setUIState: React.Dispatch<React.SetStateAction<UIState>>,
        mitoAPI: MitoAPI,
        graphDataArray: GraphDataArray,
        graphID?: GraphID,
        graphType?: GraphType,
        duplicateGraph?: boolean
    ) => {
    // We turn off editing mode, if it is on
        setEditorState(undefined);

        // If there is no data, prompt the user to import and nothing else
        if (sheetDataArray.length === 0) {
            setUIState((prevUIState) => {
                return {
                    ...prevUIState,
                    currOpenTaskpane: {
                        type: TaskpaneType.IMPORT_FIRST,
                        message: 'Before graphing data, you need to import some!'
                    }
                }
            })
            return;
        }

        // If there is a graphID, we are editing an existing graph.
        let existingParams = undefined;
        if (graphID !== undefined) {
            const response = await mitoAPI.getGraphParams(graphID);
            const existingParamsBackend = 'error' in response ? undefined : response.result;
            if (existingParamsBackend !== undefined) {
                existingParams = convertBackendtoFrontendGraphParams(existingParamsBackend);
                if (duplicateGraph) {
                    graphID = getRandomId();
                    existingParams = {
                        ...existingParams,
                        graphID: graphID,
                    }
                }
            }
        } else {
            graphID = getRandomId();
        }
        setUIState({
            ...uiState,
            selectedTabType: 'graph',
            selectedGraphID: graphID,
            currOpenModal: {type: ModalEnum.None},
            currOpenTaskpane: {
                type: TaskpaneType.GRAPH,
                graphType: graphType,
                existingParams: existingParams,
                graphID: graphID,
            }
        })
    }
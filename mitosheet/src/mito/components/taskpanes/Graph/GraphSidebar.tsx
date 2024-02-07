import React, { useEffect } from 'react';
import '../../../../../css/taskpanes/Graph/GraphSidebar.css';
import '../../../../../css/taskpanes/Graph/LoadingSpinner.css';
import { MitoAPI } from '../../../api/api';
import { useEffectOnResizeElement } from '../../../hooks/useEffectOnElementResize';
import useLiveUpdatingParams from '../../../hooks/useLiveUpdatingParams';
import { AnalysisData, GraphDataArray, GraphParamsBackend, GraphParamsFrontend, OpenGraphType, RecursivePartial, SheetData, StepType, UIState } from '../../../types';
import XIcon from '../../icons/XIcon';
import Col from '../../layout/Col';
import Row from '../../layout/Row';
import DefaultEmptyTaskpane from '../DefaultTaskpane/DefaultEmptyTaskpane';
import { TaskpaneType } from '../taskpanes';
import GraphSetupTab from './GraphSetupTab';
import LoadingSpinner from './LoadingSpinner';
import { GraphElementType, convertBackendtoFrontendGraphParams, convertFrontendtoBackendGraphParams, getDefaultGraphParams, getGraphElementObjects, getGraphRenderingParams, registerClickEventsForGraphElements } from './graphUtils';
import { updateObjectWithPartialObject } from '../../../utils/objects';
import { classNames } from '../../../utils/classNames';
import Input from '../../elements/Input';
import { getInputWidth } from '../../elements/Input';

export const Popup = (props: {
    value: string;
    position?: {
        left?: number;
        right?: number;
        top?: number;
        bottom?: number;
    };
    containerRef?: React.RefObject<HTMLDivElement>;
    setValue: (value: string) => void;
    onClose: () => void;
    caretPosition?: 'above' | 'below-left' | 'below-centered';
}) => {
    /**
     * If position is undefined, we don't display the popup. 
     */
    if (!props.position) {
        return <></>
    }

    /**
     * We use a temporary value to store the value of the popup input. This is because
     * we don't want to update the graphParams until the user presses enter.
     */
    const [ temporaryValue, setTemporaryValue ] = React.useState(props.value);
    
    React.useEffect(() => {
        setTemporaryValue(props.value);
    }, [props.value]);

    /**
     * The popup input is autofocusing, but when the popup is already open and we switch
     * to a new graph element, we lose focus. This effect re-focuses the input when the
     * graph element changes.
     */
    React.useEffect(() => {
        const input = document.getElementsByClassName('popup-input')[0] as HTMLInputElement;
        input.focus();
    }, [props.position])

    return (
        <div
            className={`graph-element-popup-div ${props.caretPosition === 'above' ? 'graph-element-popup-div-caret-above' : props.caretPosition === 'below-left' ? 'graph-element-popup-div-caret-below-left' : 'graph-element-popup-div-caret-below-centered'}`}
            style={{
                position: 'absolute',
                height: '32px',
                left: props.position.left,
                right: props.position.right,
                top: props.position.top,
                bottom: props.position.bottom,
            }}
        >
            <div className='graph-element-popup-div-caret'/>
            <Input
                className='popup-input'
                value={temporaryValue}
                style={{
                    zIndex: 1,
                    position: 'relative',
                    width: getInputWidth(temporaryValue, 150),
                }}
                onKeyDown={(e) => {
                    /**
                     * Normally, when the user has a graph element selected, pressing backspace
                     * should delete the element. However, we don't want to delete the element
                     * when the user is typing in the popup input.
                     */
                    if (e.key === 'Backspace') {
                        e.stopPropagation();
                    }
                    if (e.key === 'Enter') {
                        props.setValue(temporaryValue);
                    }
                }}
                autoFocus
                onChange={(e) => {
                    setTemporaryValue(e.target.value);
                }}
            />
        </div>
    )
}

/*
    This is the main component that displays all graphing
    functionality, allowing the user to build and view graphs.
*/
const GraphSidebar = (props: {
    setUIState: React.Dispatch<React.SetStateAction<UIState>>;
    uiState: UIState;
    sheetDataArray: SheetData[];
    mitoAPI: MitoAPI;
    graphDataArray: GraphDataArray
    mitoContainerRef: React.RefObject<HTMLDivElement>,
    analysisData: AnalysisData,
    openGraph: OpenGraphType
}): JSX.Element => {

    const {params: graphParams, setParams: setGraphParams, startNewStep, loading } = useLiveUpdatingParams<GraphParamsFrontend, GraphParamsBackend>(
        () => getDefaultGraphParams(props.mitoContainerRef, props.sheetDataArray, props.uiState.selectedSheetIndex, props.openGraph),
        StepType.Graph,
        props.mitoAPI,
        props.analysisData,
        1000, // Relatively long debounce delay, so we don't send too many graphing messages
        {
            getBackendFromFrontend: convertFrontendtoBackendGraphParams,
            getFrontendFromBackend: convertBackendtoFrontendGraphParams,
        },
    )

    /*
        The graphID is the keystone of the graphSidebar. Each graph tab has one graphID that does not switch even if the user changes source data sheets. 
        
        In order to properly open a graph in Mito, there are a few things that need to occur:
            1. We need to update the uiState's `selectedTabType` to "graph" so that the footer selects the correct tab
            2. We need to set the uiState's `currTaskpaneOpen` to "graph" so that we actually display the graph
            3. We need to pass the current taskpane the graphID so that we know which graph to display.
        Everything else is handled by the graphSidebar.  

        To create a graph, we always pass a graphID. That means that if we're creating a new graph, the opener of the taskpane is required
        to create a new graphID. 
    */
    const dataSourceSheetIndex = graphParams?.graphCreation.sheet_index
    const graphData = props.graphDataArray.find(graphData => graphData.graph_id === props.openGraph.graphID)
    const graphOutput = graphData?.graph_output;

    const currOpenTaskpane = props.uiState.currOpenTaskpane;
    if (currOpenTaskpane.type !== TaskpaneType.GRAPH) {
        return <></>
    }

    /*
         If the openGraph changes, which happens when opening a graph:
         1. reset the stepID so we don't overwrite the previous edits.
         2. refresh the graphParams so the UI is up to date with the new graphID's configuration.
     */
    useEffect(() => {
        startNewStep();
        const newParams = getDefaultGraphParams(props.mitoContainerRef, props.sheetDataArray, props.uiState.selectedSheetIndex, props.openGraph);
        setGraphParams(newParams);
    }, [props.openGraph])

    // We log if plotly is not defined
    useEffect(() => {
        if (!(window as any).Plotly) {
            void props.mitoAPI.log('plotly_define_failed');
        }
    }, [])

    // Handle graph resizing
    useEffectOnResizeElement(() => {
        setGraphParams(prevGraphParams => {
            return {
                ...prevGraphParams,
                graphRendering: getGraphRenderingParams(props.mitoContainerRef)
            }
        })
    }, [currOpenTaskpane.graphSidebarOpen], props.mitoContainerRef, '#mito-center-content-container')

    const selectedGraphElement = props.uiState.currOpenTaskpane.type === TaskpaneType.GRAPH ? props.uiState.currOpenTaskpane.currentGraphElement : undefined;
    const setSelectedGraphElement = (graphElement: GraphElementType | null) => {
        props.setUIState(prevUIState => {
            return {
                ...prevUIState,
                currOpenTaskpane: {
                    ...prevUIState.currOpenTaskpane,
                    currentGraphElement: graphElement === null ? undefined : graphElement,
                }
            }
        });
    };

    // When we get a new graph ouput, we execute the graph script here. This is a workaround
    // that is required because we need to make sure this code runs, which it does
    // not when it is a script tag inside innerHtml (which react does not execute
    // for safety reasons).
    useEffect(() => {
        try {
            if (graphOutput === undefined) {
                return;
            }
            const executeScript = new Function(graphOutput.graphScript);
            executeScript()

            const graphObjects = getGraphElementObjects(graphOutput);
            graphObjects?.div.on('plotly_afterplot', () => {
                registerClickEventsForGraphElements(graphOutput, setSelectedGraphElement);
            });
        } catch (e) {
            console.error("Failed to execute graph function", e)
        }

    }, [graphOutput])

    // Since the UI for the graphing takes up the whole screen, we don't even let the user keep it open
    // If there is no data to graph
    if (props.sheetDataArray.length === 0 || graphParams === undefined || dataSourceSheetIndex === undefined) {
        props.setUIState(prevUIState => {
            return {
                ...prevUIState,
                currOpenTaskpane: { type: TaskpaneType.NONE }
            }
        })
        return <DefaultEmptyTaskpane setUIState={props.setUIState} />
    } 

    const selectedGraphElementClass = selectedGraphElement !== undefined ? `${selectedGraphElement.element}-highlighted` : undefined;
    const containerRef = React.useRef<HTMLDivElement>(null);

    return (
        <div
            className={classNames('graph-sidebar-div', selectedGraphElementClass)}
            tabIndex={0}
            ref={containerRef}
            onKeyDown={(e) => {
                if (e.key === 'Backspace') {
                    const newGraphParams: RecursivePartial<GraphParamsFrontend> = {};
                    if (selectedGraphElement?.element === 'gtitle') {
                        newGraphParams.graphStyling = { title: { visible: false } };
                    } else if (selectedGraphElement?.element === 'xtitle') {
                        newGraphParams.graphStyling = { xaxis: { visible: false } };
                    } else if (selectedGraphElement?.element === 'ytitle') {
                        newGraphParams.graphStyling = { yaxis: { visible: false } };
                    }
                    setGraphParams(updateObjectWithPartialObject(graphParams, newGraphParams));
                }
                if ((e.key === 'Escape' || e.key === 'Enter') && (selectedGraphElement !== null)) {
                    setSelectedGraphElement(null);
                }
            }}
        >
            <div 
                className='graph-sidebar-graph-div' 
                id='graph-div'
                // Because we have padding on this div, but we want the graph to appear
                // to take up the whole screen, we also style it with the background color
                // NOTE: there's a minor visual bug where this updates quicker than the graph
                // but we choose to view it as a nice preview rather than something to fix :-)
                style={{
                    backgroundColor: graphParams?.graphStyling.paper_bgcolor,
                    color: graphParams?.graphStyling.title.title_font_color,
                }}
            >
                {graphOutput === undefined &&
                    <p className='graph-sidebar-welcome-text text-align-center-important' >To generate a graph, select an axis.</p>
                }
                {graphOutput !== undefined &&
                    <div dangerouslySetInnerHTML={{ __html: graphOutput.graphHTML }} />
                }
                <Popup
                    value={(selectedGraphElement?.element === 'gtitle' ? graphParams?.graphStyling.title.title : selectedGraphElement?.element === 'xtitle' ? graphParams?.graphStyling.xaxis?.title : selectedGraphElement?.element === 'ytitle' ? graphParams?.graphStyling.yaxis?.title : '') ?? selectedGraphElement?.defaultValue ?? ''}
                    setValue={(value) => {
                        const update = {
                            graphStyling: {
                                title: selectedGraphElement?.element === 'gtitle' ? { title: value } : graphParams?.graphStyling.title,
                                xaxis: selectedGraphElement?.element === 'xtitle' ? { title: value } : graphParams?.graphStyling.xaxis,
                                yaxis: selectedGraphElement?.element === 'ytitle' ? { title: value } : graphParams?.graphStyling.yaxis,
                            }
                        };
                        const currOpenTaskpane = props.uiState.currOpenTaskpane;
                        const stepSummaryList = props.analysisData.stepSummaryList;
                        const currGraphStep = stepSummaryList[stepSummaryList.length - 1];
                        const params = currGraphStep.params as GraphParamsBackend | undefined;
                        if (currOpenTaskpane.type !== TaskpaneType.GRAPH || params === undefined) {
                            return;
                        }
                        void props.mitoAPI.editGraph(
                            currOpenTaskpane.openGraph.graphID,
                            updateObjectWithPartialObject(graphParams, update),
                            graphParams.graphRendering.height ?? '100%',
                            graphParams.graphRendering.width ?? '100%',
                            currGraphStep.step_id,
                            true
                        );
                    }}
                    caretPosition={selectedGraphElement?.element === 'gtitle' ? 'above' : selectedGraphElement?.element === 'ytitle' ? 'below-left' : 'below-centered'}
                    position={selectedGraphElement?.popupPosition}
                    onClose={() => setSelectedGraphElement(null)}
                    containerRef={containerRef}
                />
            </div>
            {currOpenTaskpane.graphSidebarOpen && <div className='graph-sidebar-toolbar-container'>
                <div className='graph-sidebar-toolbar-content-container'>
                    <Row justify='space-between' align='center'>
                        <Col>
                            <p className='text-header-2'>
                                Select Data
                            </p>
                        </Col>
                        <Col>
                            <XIcon
                                onClick={() => {
                                    props.setUIState((prevUIState) => {
                                        return {
                                            ...prevUIState,
                                            currOpenTaskpane: {
                                                ...prevUIState.currOpenTaskpane,
                                                graphSidebarOpen: false,
                                            }
                                        }
                                    })
                                }}
                            />
                        </Col>
                    </Row>
                    <GraphSetupTab 
                        graphParams={graphParams}
                        setGraphParams={setGraphParams}
                        uiState={props.uiState}
                        mitoAPI={props.mitoAPI}
                        graphID={props.openGraph.graphID}
                        sheetDataArray={props.sheetDataArray}
                        columnDtypesMap={props.sheetDataArray[dataSourceSheetIndex]?.columnDtypeMap || {}}
                        setUIState={props.setUIState}
                        mitoContainerRef={props.mitoContainerRef}
                        openGraph={props.openGraph}
                    />
                </div>
            </div>}
            {loading &&
                <div className='popup-div'>
                    <LoadingSpinner />
                    <p className='popup-text-div'>
                        loading
                    </p>
                </div>
            }
        </div>
        
    )
};

export default GraphSidebar;

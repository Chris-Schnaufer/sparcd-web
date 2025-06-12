/** @module Queries */

import * as React from 'react';
import Box from '@mui/material/Box';
import { DataGrid, useGridApiRef } from '@mui/x-data-grid';
import DownloadForOfflineOutlinedIcon from '@mui/icons-material/DownloadForOfflineOutlined';
import Grid from '@mui/material/Grid';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import PropTypes from 'prop-types';

import QueryFilters from './queries/QueryFilters'
import { FilterCollectionsFormData } from './queries/FilterCollections';
import { FilterDateFormData } from './queries/FilterDate';
import { FilterDayOfWeekFormData } from './queries/FilterDayOfWeek';
import { FilterElevationsFormData } from './queries/FilterElevation';
import { FilterHourFormData } from './queries/FilterHour';
import { FilterLocationsFormData } from './queries/FilterLocations';
import { FilterMonthFormData } from './queries/FilterMonth';
import { FilterSpeciesFormData } from './queries/FilterSpecies';
import { FilterYearFormData } from './queries/FilterYear';
import * as utils from './utils'

import { resp } from './queryresult'; //TODO: remove when obtaining real data
import { LocationsInfoContext, SpeciesInfoContext, TokenContext } from './serverInfo'

/**
 * Provides the UI for queries
 * @function
 * @returns {object} The UI for generating queries
 */
export default function Queries() {
  const theme = useTheme();
  const apiRef = useGridApiRef(); // TODO: Auto size columns of grids using this api
  const filterRef = React.useRef();   // Used for sizeing
  const locationItems = React.useContext(LocationsInfoContext);
  const queryToken = React.useContext(TokenContext);
  const speciesItems = React.useContext(SpeciesInfoContext);
  const [activeTab, setActiveTab] = React.useState(0);
  const [filters, setFilters] = React.useState([]); // Stores filter information
  const [filterRedraw, setFilterRedraw] = React.useState(null); // Used to force redraw when new filter added
  const [filterHeight, setFilterHeight] = React.useState(240); // Used to force redraw when new filter added
  const [queryResults, setQueryResults] = React.useState(null); // Used to store query results
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [totalHeight, setTotalHeight] = React.useState(null);  // Default value is recalculated at display time
  const [windowSize, setWindowSize] = React.useState({width: 640, height: 480});  // Default values are recalculated at display time
  const [workingTop, setWorkingTop] = React.useState(null);    // Default value is recalculated at display time
  const [workspaceWidth, setWorkspaceWidth] = React.useState(640);  // Default value is recalculated at display time

  handleFilterChange = handleFilterChange.bind(Queries);
  removeFilter = removeFilter.bind(Queries);
  handleFilterAccepted = handleFilterAccepted.bind(Queries);
  handleQuery = handleQuery.bind(Queries);

  /**
   * Updates fields when a new tab is selected for display
   * @function
   * @param {object} event The triggering event object
   * @param {object} newValue The new tab value
   */
  function handleTabChange(event, newValue) {
    setActiveTab(newValue);
  }

  // Recalcuate available space in the window
  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWindowSize(newSize);
    calcTotalSize(newSize);
    setWorkspaceWidth(newSize.width);
  }, [totalHeight]);

  // Adds a handler for when the window is resized, and automatically removes the handler
  React.useLayoutEffect(() => {
      function onResize () {
        const newSize = {'width':window.innerWidth,'height':window.innerHeight};

        setWindowSize(newSize);

        calcTotalSize(newSize);

        const newWorkspaceWidth = newSize.width;
        setWorkspaceWidth(newWorkspaceWidth);

        // Calculate the filter panel size
        if (filterRef && filterRef.current) {
          filterHeight = filterRef.current.offsetHeight;
          setFilterHeight(filterHeight);
        }
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [totalHeight]);

  /**
   * Calculates the total UI size available for the workarea
   * @function
   * @param {object} curSize The total width and height of the window
   */
  function calcTotalSize(curSize) {
    const elWorkspace = document.getElementById('queries-workspace-wrapper');
    if (elWorkspace) {
      const elWorkspaceSize = elWorkspace.getBoundingClientRect();
      let workingHeight = elWorkspaceSize.height;
      const elFooter = document.getElementById('sparcd-footer');
      if (elFooter) {
        const elFooterSize = elFooter.getBoundingClientRect();
        workingHeight -= elFooterSize.height;
      }
      setTotalHeight(workingHeight);
      setWorkingTop(0);
    }

    setWorkspaceWidth(curSize.width);
  }

  /**
   * Adds a new filter to the list of filters
   * @function
   */
  function addFilter(filterChoice) {
    // Get the filter elements we need to access
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    if (!elFilter) {
      return;
    }
    // Show the spinner until the new filter is added
    let elFilterWait = document.getElementById("query-filter-selection-waiting");
    if (elFilterWait) {
      if (elFilter.style.visibility === 'visible') {
        elFilterWait.style.visibility = 'visible';
      }
    }

    // Add the new filter to the array of filters
    const newFilter = {type:filterChoice, id:crypto.randomUUID(), data:null}
    const allFilters = filters;
    allFilters.push(newFilter);

    // Set the timeout to remove the spinner and update the UI
    window.setTimeout(() => {
                  elFilter.style.visibility = 'hidden';
                  if (elFilterWait) {
                    elFilterWait.style.visibility = 'hidden';
                  }

                  setFilters(allFilters);
                  setFilterRedraw(newFilter.id);
                });
  }

  /**
   * Removes a filter from the list
   * @function
   * @param {string} filterId The unique ID of the filter to remove
   */
  function removeFilter(filterId) {
    const remainingFilters = filters.filter((item) => item.id != filterId);
    setFilters(remainingFilters);

    setFilterRedraw(crypto.randomUUID());
  }

  /**
   * Called when the data for a filter is changed
   * @function
   * @param {string} filterId The ID of the filter to update
   * @param {object} filterData The new filter data to save
   */
  function handleFilterChange(filterId, filterData) {
    const filterIdx = filters.findIndex((item) => item.id === filterId);
    if (filterIdx > -1) {
      const curFilters = filters;
      curFilters[filterIdx].data = filterData;
      setFilters(curFilters);
    }
  }

  /**
   * Handles adding a new filter when a filter is double-clicked
   * @function
   * @param {string} filterChoice The filter name that is to be added
   */
  function handleFilterAccepted(filterChoice) {
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    // Show the wait spinner
    let elFilterWait = document.getElementById("query-filter-selection-waiting");
    if (elFilter && elFilterWait) {
      if (elFilter.style.visibility === 'visible') {
        elFilterWait.style.visibility = 'visible';
      }
    }
    // Set the timeout to add the filter and update the UI
    window.setTimeout(() => { addFilter(filterChoice);
                              if (elFilterWait) {
                                elFilterWait.style.visibility = 'hidden';
                              }
                            }, 100);
  }

  /**
   * Fills in the form data for all of the user's filters
   * @function
   * @param {array} queryFilters The array of filter information to use to fill in the FormData
   * @returns {object} Returns a new FormData with the filters added
   */
  function getQueryFormData(queryFilters) {
    let formData = new FormData();

    for (const filterIdx in queryFilters) {
      const filter = queryFilters[filterIdx];
      switch(filter.type) {
        case 'Species Filter':
          FilterSpeciesFormData(filter.data, formData, speciesItems);
          break;
        case 'Location Filter':
          FilterLocationsFormData(filter.data, formData, locationItems);
          break;
        case 'Elevation Filter':
          FilterElevationsFormData(filter.data, formData);
          break;
        case 'Year Filter':
          FilterYearFormData(filter.data, formData);
          break;
        case 'Month Filter':
          FilterMonthFormData(filter.data, formData);
          break;
        case 'Hour Filter':
          FilterHourFormData(filter.data, formData);
          break;
        case 'Day of Week Filter':
          FilterDayOfWeekFormData(filter.data, formData);
          break;
        case 'Start Date Filter':
          FilterDateFormData('startDate', filter.data, formData);
          break;
        case 'End Date Filter':
          FilterDateFormData('endDate', filter.data, formData);
          break;
        case 'Collection Filter':
          FilterCollectionsFormData(filter.data, formData);
        break;
      }
    }

    return formData;
  }

  /**
   * Makes the call to get the query data and saves the results
   * @function
   */
  function handleQuery() {
    const queryUrl = serverURL + '/query';
    const formData = getQueryFormData(filters);

    formData.append('token', queryToken);

    console.log('QUERY');
    for (const i of formData.keys()) console.log(i);
    for (const i of formData.values()) console.log(i);

    // Make the query
    try {
      const resp = fetch(queryUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
          if (resp.ok) {
            return resp.json();
          } else {
            throw new Error(`Failed to complete query: ${resp.status}`, {cause:resp});
          }
        })
        .then((respData) => {
          // TODO: handle no results
          console.log('QUERY:',respData);
          setQueryResults(respData);
        })
        .catch(function(err) {
          console.log('Error: ',err);
        });
    } catch (error) {
      console.log('Error: ',error);
    }
  }

  /**
   * Internal TabPanel element type
   * @function
   * @param {object} props The properties of the TabPanel element
   * @returns {object} Returns the UI for the TabPanel
   */
  function TabPanel(props) {
    const { children, value, index, ...other } = props;

    return (
      <div
        role="tabpanel"
        hidden={value !== index}
        id={`query-results-tabpanel-${index}`}
        aria-labelledby={`query-results-${index}`}
        {...other}
      >
      {value === index && (
        <Box id='tabpanel-box' sx={{ height:'395px' }}>
          {children}
        </Box>
      )}
      </div>
    );
  }

  // Define the types of the properties accepted by the TabPanel
  TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
  };

  /**
   * Returns the a11y properties for a tab control
   * @function
   * @param {integer} index The index of the tab
   * @returns {object} The properties to use for the tab
   */
  function a11yPropsTabPanel(index) {
    return {
      id: `query-results-${index}`,
      'aria-controls': `query-results-${index}`,
    };
  }

  /**
   * Generates a panel for displaying the query results based upon different tabs
   * @function
   * @param {object} queryResults The results of the performed query
   * @param {string} tabName The unique identifier of the tab to generate the panel for
   * @param {integer} tabIndex The relative index of the tab
   * @returns {object} The panel UI to render
   */ 
  function generateResultPanel(queryResults, tabName, tabIndex) {

      // Generate a textarea to display the results if we aren't generating a data grid
    if (queryResults.columns[tabName] == undefined) {
      return (
          <textarea id={'query-results-'+tabName} readOnly wrap="off"
            style={{resize:"none", fontFamily:'monospace', fontSize:'small', fontWeight:'lighter', 
                    position:'absolute', left:0, top:0, right:0, bottom:0, padding:'5px'}}
            value={queryResults[tabName]}
          />
      );
    }

    // Generate a DataGrid to display the results
    let colTitles = queryResults.columns[tabName];
    let colData = queryResults[tabName];
    let keys = Object.keys(colTitles);
    let curData = colData;
    let columnGroupings = undefined;

    let curTitles = keys.map((name, idx) => {return {field:name, headerName:colTitles[name]}});

    if (keys.find((item) => item === 'id') == undefined) {
      curData = colData.map((row, rowIdx) => {return {id:rowIdx, ...row}});
    }

    // Check if we have column groupings and regenerate/update variables if we do
    if (keys.find((item) => typeof(colTitles[item]) === 'object' && !Array.isArray(colTitles[item])) != undefined) {
      let newKeys = [];
      let newTitles = [];
      columnGroupings = [];
      for (const curKey in colTitles) {
        if (typeof(colTitles[curKey]) === 'object' && !Array.isArray(colTitles[curKey])) {
          const curGroup = colTitles[curKey];
          const curKeys = Object.keys(curGroup);
          columnGroupings.push({groupId:curGroup['title'],
                                children:curKeys.map((curKey) => curKey !== 'title' && {field:curKey})
                                          .filter((child) => child !== false)
                               });
          newKeys = [...newKeys, ...(curKeys.map((curKey) => curKey !== 'title' && curGroup[curKey])
                                            .filter((item) => item !== false))
                    ];
          newTitles = [...newTitles, ...(curKeys.map((curKey) => curKey !== 'title' && {field:curKey, headerName:curGroup[curKey]})
                                                .filter((item) => item !== false))
                      ];
        } else {
          // Don't add to groupings
          //columnGroupings.push({groupId:colTitles[curKey],children:[{field:curKey}]});
          newKeys.push(curKey);
          newTitles.push({field:curKey, headerName:colTitles[curKey]});
        }
      }

      keys = newKeys;
      curTitles = newTitles;
    }

    return (
      <DataGrid columns={curTitles} rows={curData} disableRowSelectionOnClick 
                autosizeOptions={{
                    columns: keys,
                    includeOutliers: true,
                    includeHeaders: true,
                    outliersFactor: 1,
                    expand: true,
                  }}
                columnGroupingModel={columnGroupings}
      />
    );
  }

  /**
   * Generates the UI for displaying query results
   * @param {object} queryResults The results of a query to display
   * @returns {object} The UI of the query results
   */
  function generateQueryResults(queryResults) {
    return (
      <Grid container size="grow" alignItems="start" justifyContent="start">
        <Grid size={2}  sx={{backgroundColor:"#EAEAEA"}}>
          <Tabs id='testing' value={activeTab} onChange={handleTabChange} aria-label="Query results" orientation="vertical" variant="scrollable"
                scrollButtons={false} style={{overflow:'scroll', maxHeight:'100%'}}>
          { queryResults.tabs.order.map((item, idx) => 
              <Tab label={
                          <Grid container direction="row" alignItems="center" justifyContent="center">
                            <Grid>
                              <Typography gutterBottom variant="body2">
                                {queryResults.tabs[item]}
                              </Typography>
                            </Grid>
                            <Tooltip title={'Download CSV of '+queryResults.tabs[item]}>
                              <a href={serverURL + '/querydownload?tab' + item} download={item + '.csv'}  style={{marginLeft:'auto'}}>
                                <Grid sx={{borderRadius:'5px','&:hover':{backgroundColor:'rgba(0,0,255,0.05)'} }}>
                                  <DownloadForOfflineOutlinedIcon sx={{padding:'5px'}} />
                                </Grid>
                              </a>
                            </Tooltip>
                          </Grid>
                         }
                   key={item} {...a11yPropsTabPanel(idx)} sx={{'&:hover':{backgroundColor:'rgba(0,0,0,0.05)'} }} />
            )
          }
          </Tabs>
        </Grid>
        <Grid size={10} sx={{minHeight:'395px',maxHeight:'395px',overflowX:'scroll',display:'flex'}}>
          { queryResults.tabs.order.map((item, idx) => {
              return (
                <TabPanel id={'query-result-panel-'+item} value={activeTab} index={idx} key={item+'-'+idx} 
                          style={{overflow:'scroll', width:'100%', position:'relative',margin:'0 16px auto 8px'}}>
                  {generateResultPanel(queryResults, item, idx)}
                </TabPanel>
              )}
            )
          }
        </Grid>
      </Grid>
    );
  }

  // Set a time to have new panels scroll into view
  const elActions = document.getElementById('queries-actions');
  if (elActions && filters) {
    window.setTimeout(() => elActions.scrollIntoView({ behavior:'smooth', inline:'nearest'}), 10);
  }

  // Return the UI
  const curHeight = 350;//((totalHeight || 480) / 2.0) + 'px';
  return (
    <Box id='queries-workspace-wrapper' sx={{ flexGrow: 1, 'width': '100vw', position:'relative'}} >
      <QueryFilters ref={filterRef} workingWidth={workspaceWidth} workingHeight={curHeight} filters={filters}
                    filterChanged={handleFilterChange} filterRemove={removeFilter} filterAdd={handleFilterAccepted}
                    onQuery={handleQuery} />
      <Grid container id="query-results-wrapper" direction="row" alignItems="start" justifyContent="start" wrap="nowrap"
            spacing={2}
            sx={{minHeight:(totalHeight-curHeight)+"px", maxHeight:(totalHeight-curHeight)+"px", backgroundColor:'white',
                 margin:0, overflow:'clip', padding:'5px', borderTop:'1px solid grey'}}
      >
      { queryResults ? generateQueryResults(queryResults)  : null }
      </Grid>
    </Box>
  );
}
/** @module CollectionsManage */

import * as React from 'react';
import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import CircularProgress from '@mui/material/CircularProgress';
import Container from '@mui/material/Container';
import { DataGrid, useGridApiRef } from '@mui/x-data-grid';
import DownloadForOfflineOutlinedIcon from '@mui/icons-material/DownloadForOfflineOutlined';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Tab from '@mui/material/Tab';
import Tabs from '@mui/material/Tabs';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import PropTypes from 'prop-types';

import FilterCollections, { FilterCollectionsFormData } from './components/FilterCollections';
import FilterDate, { FilterDateFormData } from './components/FilterDate';
import FilterDayOfWeek, { FilterDayOfWeekFormData } from './components/FilterDayOfWeek';
import FilterElevation, { FilterElevationsFormData } from './components/FilterElevation';
import FilterHour, { FilterHourFormData } from './components/FilterHour';
import FilterLocations, { FilterLocationsFormData } from './components/FilterLocations';
import FilterMonth, { FilterMonthFormData } from './components/FilterMonth';
import FilterSpecies, { FilterSpeciesFormData } from './components/FilterSpecies';
import FilterYear, { FilterYearFormData } from './components/FilterYear';
import * as utils from './utils'

import { resp } from './queryresult';

export default function Queries() {
  const theme = useTheme();
  const apiRef = useGridApiRef(); // TODO: Auto size columns
  const [activeTab, setActiveTab] = React.useState(0);
  const [filters, setFilters] = React.useState([]); // Stores filter information
  const [filterSelected, setFilterSelected] = React.useState(false); // Indicates a new filter is selected
  const [filterRedraw, setFilterRedraw] = React.useState(null); // Used to force redraw when new filter added
  const [queryResults, setQueryResults] = React.useState(null); // Used to store query results
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [totalHeight, setTotalHeight] = React.useState(null);  // Default value is recalculated at display time
  const [windowSize, setWindowSize] = React.useState({width: 640, height: 480});  // Default values are recalculated at display time
  const [workingTop, setWorkingTop] = React.useState(null);    // Default value is recalculated at display time
  const [workspaceWidth, setWorkspaceWidth] = React.useState(640);  // Default value is recalculated at display time

  const handleChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const filterNames = [
    'Species Filter',
    'Location Filter',
    'Elevation Filter',
    'Year Filter',
    'Month Filter',
    'Hour Filter',
    'Day of Week Filter',
    'Start Date Filter',
    'End Date Filter',
    'Collection Filter'
  ];

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
      setTotalHeight(elWorkspaceSize.height);
      setWorkingTop(0);
    }

    setWorkspaceWidth(curSize.width);
  }

  function handleNewFilter() {
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    if (!elFilter) {
      return;
    }
    elFilter.style.visibility = 'visible';
  }

  function addFilter() {
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    if (!elFilter) {
      return;
    }
    let elFilterWait = document.getElementById("query-filter-selection-waiting");
    if (elFilterWait) {
      if (elFilter.style.visibility === 'visible') {
        elFilterWait.style.visibility = 'visible';
      }
    }

    const newFilter = {type:filterSelected, id:crypto.randomUUID(), data:null}
    const allFilters = filters;
    allFilters.push(newFilter);

    window.setTimeout(() => {
                  elFilter.style.visibility = 'hidden';
                  if (elFilterWait) {
                    elFilterWait.style.visibility = 'hidden';
                  }

                  setFilters(allFilters);
                  setFilterRedraw(newFilter.id);
                });
  }

  function cancelAddFilter() {
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    if (!elFilter) {
      return;
    }
    elFilter.style.visibility = 'hidden';
  }

  function removeFilter(filterId) {
    const remainingFilters = filters.filter((item) => item.id != filterId);
    setFilters(remainingFilters);

    setFilterRedraw(crypto.randomUUID());
  }

  function handleFilterChange(filterId, filterData) {
    const filterIdx = filters.findIndex((item) => item.id === filterId);
    if (filterIdx > -1) {
      const curFilters = filters;
      curFilters[filterIdx].data = filterData;
      setFilters(curFilters);
    }
  }

  function handleFilterAccepted(filterChoice) {
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    let elFilterWait = document.getElementById("query-filter-selection-waiting");
    if (elFilter && elFilterWait) {
      if (elFilter.style.visibility === 'visible') {
        elFilterWait.style.visibility = 'visible';
      }
    }
    window.setTimeout(() => { setFilterSelected(filterChoice);
                              addFilter();
                              if (elFilterWait) {
                                elFilterWait.style.visibility = 'hidden';
                              }
                            }, 100);
  }

  function getQueryFormData(queryFilters) {
    let formData = new FormData();

    for (const filterIdx in queryFilters) {
      const filter = queryFilters[filterIdx];
      switch(filter.type) {
        case 'Species Filter':
          FilterSpeciesFormData(filter.data, formData);
          break;
        case 'Location Filter':
          FilterLocationsFormData(filter.data, formData);
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

  function handleQuery() {
    const uploadUrl = serverURL + '/query';
    const formData = getQueryFormData(filters);

    // Get the information on the upload
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(loginUrl, {
      'method': 'POST',
      'data': formData
    });
    console.log(resp);
    */
    setQueryResults(resp);
  }

  function generateFilterTile(filterInfo) {
    switch(filterInfo.type) {
      case 'Collection Filter':
        return (
          <FilterCollections data={filterInfo.data}
                             onClose={() => removeFilter(filterInfo.id)} 
                             onChange={(data) => handleFilterChange(filterInfo.id, data)}/>

        );
      case 'Day of Week Filter':
        return (
          <FilterDayOfWeek data={filterInfo.data}
                           onClose={() => removeFilter(filterInfo.id)} 
                           onChange={(data) => handleFilterChange(filterInfo.id, data)}/>

        );
      case 'Elevation Filter':
        return (
          <FilterElevation data={filterInfo.data}
                           onClose={() => removeFilter(filterInfo.id)} 
                           onChange={(data) => handleFilterChange(filterInfo.id, data)}/>

        );
      case 'End Date Filter':
        return (
            <FilterDate data={filterInfo.data}
                        title='End Date Filter'
                        onClose={() => removeFilter(filterInfo.id)} 
                        onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
      case 'Hour Filter':
        return (
            <FilterHour data={filterInfo.data}
                        onClose={() => removeFilter(filterInfo.id)} 
                        onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
      case 'Location Filter':
        return (
            <FilterLocations data={filterInfo.data}
                           onClose={() => removeFilter(filterInfo.id)} 
                           onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
      case 'Month Filter':
        return (
            <FilterMonth data={filterInfo.data}
                         onClose={() => removeFilter(filterInfo.id)} 
                         onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
      case 'Species Filter':
        return (
            <FilterSpecies data={filterInfo.data}
                           onClose={() => removeFilter(filterInfo.id)} 
                           onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
      case 'Start Date Filter':
        return (
            <FilterDate data={filterInfo.data}
                        title='Start Date Filter'
                        onClose={() => removeFilter(filterInfo.id)} 
                        onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
      case 'Year Filter':
        return (
            <FilterYear data={filterInfo.data}
                        onClose={() => removeFilter(filterInfo.id)} 
                        onChange={(data) => handleFilterChange(filterInfo.id, data)}/>
        );
    }
  }

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

  TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
  };

  function a11yPropsTabPanel(index) {
    return {
      id: `query-results-${index}`,
      'aria-controls': `query-results-${index}`,
    };
  }

  function generateResultPanel(queryResults, tabName, tabIndex) {
    if (queryResults.columns[tabName] == undefined) {
      return (
          <textarea id={'query-results-'+tabName} readOnly wrap="off"
            style={{resize:"none", fontFamily:'monospace', fontSize:'small', fontWeight:'lighter', 
                    position:'absolute', left:0, top:0, right:0, bottom:0, padding:'5px'}}
            value={queryResults[tabName]}
          />
      );
    }

    let colTitles = queryResults.columns[tabName];
    let colData = queryResults[tabName];
    let keys = Object.keys(colTitles);
    let curData = colData;
    let columnGroupings = undefined;

    let curTitles = keys.map((name, idx) => {return {field:name, headerName:colTitles[name]}});

    if (keys.find((item) => item === 'id') == undefined) {
      curData = colData.map((row, rowIdx) => {return {id:rowIdx, ...row}});
    }

    // Check if we have column groupings and update fields when we do
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

  function generateQueryResults(queryResults) {
    return (
      <Grid container alignItems="start" justifyContent="start" >
        <Grid item  xs={2}  sx={{backgroundColor:"#EAEAEA"}}>
          <Tabs value={activeTab} onChange={handleChange} aria-label="Query results" orientation="vertical" variant="scrollable">
          { queryResults.tabs.order.map((item, idx) => 
              <Tab label={
                          <Grid container direction="row" alignItems="center" justifyContent="center">
                            <Grid item>
                              <Typography gutterBottom variant="body2">
                                {queryResults.tabs[item]}
                              </Typography>
                            </Grid>
                            <Tooltip title={'Download CSV of '+queryResults.tabs[item]}>
                              <a href={serverURL + '/querydownload?tab' + item} download={item + '.csv'}  style={{marginLeft:'auto'}}>
                                <Grid item sx={{borderRadius:'5px','&:hover':{backgroundColor:'rgba(0,0,255,0.05)'} }}>
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
        <Grid item xs={10} sx={{minHeight:'395px',maxHeight:'395px',overflowX:'scroll',display:'flex'}}>
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

  const elActions = document.getElementById('queries-actions');
  if (elActions && filters) {
    window.setTimeout(() => elActions.scrollIntoView({ behavior:'smooth', inline:'nearest'}), 10);
  }

  const curHeight = 350;//((totalHeight || 480) / 2.0) + 'px';
  return (
    <Box id='queries-workspace-wrapper' sx={{ flexGrow: 1, 'width': '100vw', position:'relative'}} >
      <div style={{overflow:'scroll'}}>
        <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap"
              spacing={2}
              sx={{minHeight:curHeight+"px", maxHeight:curHeight+"px", backgroundColor:'white',
                   margin:0, overflowY:'scroll', padding:'5px'}}
        >
          { filters.map((item, idx) => 
              <Grid item key={"filter-" + item + "-" + idx} >
                <Grid container direction="column" alignItems="center" justifyContent="center"
                      sx={{ minHeight:'310px', maxHeight:'310px', minWidth:'310px', maxWidth:'310px', padding:'5px',
                            border:'solid 1px grey', borderRadius:'10px', backgroundColor:'seashell' }}>
                  <Grid item>
                    {generateFilterTile(item)}
                  </Grid>
                </Grid>
              </Grid>
              ) 
          }
          <Grid item>
            <Grid id="queries-actions" container direction="column" alignItems="center" justifyContent="center"
                  sx={{ position:'relative', minHeight:'310px',minWidth:'250px', border:'solid 1px grey', borderRadius:'10px',
                        backgroundColor:'seashell' }}>
              <Grid item>
                <Tooltip title="Click to add a new filter">
                  <IconButton onClick={handleNewFilter}>
                    <AddCircleOutlineOutlinedIcon sx={{fontSize: 55, color:'grey'}} />
                  </IconButton>
                </Tooltip>
              </Grid>
              <Grid item>
                <Button disabled={filters.length > 0 ? false:true} onClick={handleQuery}>Perform Query</Button>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </div>
      <Grid id="query-filter-selection-wrapper" container direction="column"  alignItems="center" justifyContent="center"
            sx={{position:'absolute', top:'0px', width:workspaceWidth, minHeight:curHeight, maxHeight:curHeight,
                 background:'rgb(0,0,0,0.75)', overflow:'clip', visibility:'hidden'}}
      >
        <Card variant="outlined" >
          <React.Fragment>
            <CardHeader sx={{ textAlign:'center', paddingBottom:'0' }} title={
                <Typography gutterBottom variant="h6" component="h4">
                  Choose Filter
                </Typography>
               }
             />
            <CardContent sx={{position:'relative'}}>
              <List sx={{backgroundColor:'silver', border:'1px solid grey', borderRadius:'7px', maxHeight:'200px', overflow:'scroll'}} >
                { filterNames.map((item) => 
                    <ListItem disablePadding key={"query-filter-sel-" + item}>
                        <ListItemText primary={item} 
                                      sx={{padding:'0 8px', cursor:'pointer', ...(item === filterSelected && {backgroundColor:'#B0B0B0'}),
                                           '&:hover':{backgroundColor:'lightgrey'} }}
                                      onClick={() => setFilterSelected(item)}
                                      onDoubleClick={() => handleFilterAccepted(item)}/>
                    </ListItem>
                )}
              </List>
              <Grid id="query-filter-selection-waiting" container direction="column"  alignItems="center" justifyContent="center"
                    sx={{position:'absolute', top:'0px', width:'100%', height:'100%', visibility:'hidden'}}
              >
                <CircularProgress id="query-filter-selection-waiting" />
              </Grid>
            </CardContent>
            <CardActions>
              <Button id="add-filter" sx={{'flex':'1'}} size="small" onClick={addFilter}
                      disabled={filterSelected ? false : true}>Add</Button>
              <Button id="add-filter-cancel" sx={{'flex':'1'}} size="small" onClick={cancelAddFilter}>Cancel</Button>
            </CardActions>
          </React.Fragment>
        </Card>
      </Grid>
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
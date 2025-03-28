/** @module CollectionsManage */

import * as React from 'react';
import AddCircleOutlineOutlinedIcon from '@mui/icons-material/AddCircleOutlineOutlined';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Container from '@mui/material/Container';
import Grid from '@mui/material/Grid';
import IconButton from '@mui/material/IconButton';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import FilterCollections from './components/FilterCollections';
import FilterDate from './components/FilterDate';
import FilterDayOfWeek from './components/FilterDayOfWeek';
import FilterElevation from './components/FilterElevation';
import FilterHour from './components/FilterHour';
import FilterLocations from './components/FilterLocations';
import FilterMonth from './components/FilterMonth';
import FilterSpecies from './components/FilterSpecies';
import FilterYear from './components/FilterYear';

export default function Queries() {
  const theme = useTheme();
  const [filters, setFilters] = React.useState([]); // Stores filter information
  const [filterSelected, setFilterSelected] = React.useState(false); // Indicates a new filter is selected
  const [filterRedraw, setFilterRedraw] = React.useState(null); // Used to force redraw when new filter added
  const [totalHeight, setTotalHeight] = React.useState(null);  // Default value is recalculated at display time
  const [windowSize, setWindowSize] = React.useState({width: 640, height: 480});  // Default values are recalculated at display time
  const [workingTop, setWorkingTop] = React.useState(null);    // Default value is recalculated at display time
  const [workspaceWidth, setWorkspaceWidth] = React.useState(640);  // Default value is recalculated at display time

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
    console.log('ADD FILTER');
    let elFilter = document.getElementById('query-filter-selection-wrapper');
    if (!elFilter) {
      return;
    }
    elFilter.style.visibility = 'hidden';

    const newFilter = {type:filterSelected, id:crypto.randomUUID(), data:null}
    const allFilters = filters;
    allFilters.push(newFilter);
    setFilters(allFilters);

    setFilterRedraw(newFilter.id);
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
      console.log('F',filterId, filterData);
      const curFilters = filters;
      curFilters[filterIdx].data = filterData;
      setFilters(curFilters);
    }
  }

  function handleFilterAccepted(filterChoice) {
    setFilterSelected(filterChoice);
    addFilter();
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

  const curHeight = (totalHeight || 480) + 'px';
  return (
    <Box id='queries-workspace-wrapper' sx={{ flexGrow: 1, 'width': '100vw', position:'relative' }} >
      <Grid container direction="row" alignItems="start" justifyContent="start"
            spacing={2}
            sx={{position:'absolute', top:'0px', width:workspaceWidth, minHeight:curHeight, maxHeight:curHeight, backgroundColor:'white',
                 overflow:'scroll', padding:'5px'}}
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
          <Grid container direction="column" alignItems="center" justifyContent="center"
                sx={{ minHeight:'310px',minWidth:'250px', border:'solid 1px grey', borderRadius:'10px', backgroundColor:'seashell' }}>
            <Grid item>
              <Tooltip title="Click to add a new filter">
                <IconButton onClick={handleNewFilter}>
                  <AddCircleOutlineOutlinedIcon sx={{fontSize: 55, color:'grey'}} />
                </IconButton>
              </Tooltip>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
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
              <CardContent>
                <List sx={{backgroundColor:'silver', border:'1px solid grey', borderRadius:'7px'}} >
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
              </CardContent>
              <CardActions>
                <Button id="add-filter" sx={{'flex':'1'}} size="small" onClick={addFilter}
                        disabled={filterSelected ? false : true}>Add</Button>
                <Button id="add-filter-cancel" sx={{'flex':'1'}} size="small" onClick={cancelAddFilter}>Cancel</Button>
              </CardActions>
            </React.Fragment>
          </Card>
      </Grid>
    </Box>
  );
}
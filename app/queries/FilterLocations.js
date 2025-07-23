/** @module components/FilterLocations */

import * as React from 'react';
import BackspaceOutlined from '@mui/icons-material/BackspaceOutlined';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import Grid from '@mui/material/Grid';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { LocationsInfoContext } from '../serverInfo';
import FilterCard from './FilterCard';

/**
 * Adds location information to form data
 * @function
 * @param {object} data The saved data to add to the form
 * @param {object} formData The FormData to add the fields to
 * @param {array} locationsItems The complete list of locations used for mapping
 */
export function FilterLocationsFormData(data, formData, locationItems) {
  const id_data = locationItems.filter((item) => data.includes(item['nameProperty']))
  formData.append('locations', JSON.stringify(id_data.map((item) => item['idProperty'])));
}

/**
 * Returns the UI for filtering by location
 * @param {object} {data} Saved location data
 * @param {string} parentId The ID of the parent of this filter
 * @param {function} onClose The handler for closing this filter
 * @param {function} onChange The handler for when the filter data changes
 * @returns {object} The UI specific for filtering by location range
 */
export default function FilterLocations({data, parentId, onClose, onChange}) {
  const theme = useTheme();
  const cardRef = React.useRef();   // Used for sizeing
  const locationItems = React.useContext(LocationsInfoContext);
  const [displayedLocations, setDisplayedLocations] = React.useState(locationItems); // The visible locations
  const [listHeight, setListHeight] = React.useState(200);
  const [selectedLocations, setSelectedLocations] = React.useState(data ? data : locationItems.map((item)=>item.nameProperty)); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  // Set the default data if it's not set yet
  React.useEffect(() => {
    if (!data) {
      onChange(selectedLocations);
    }
  }, [data, onChange, selectedLocations]);

  // Calculate how large the list can be
  React.useLayoutEffect(() => {
    if (parentId && cardRef && cardRef.current) {
      const parentEl = document.getElementById(parentId);
      if (parentEl) {
        const parentRect = parentEl.getBoundingClientRect();
        let usedHeight = 0;
        const childrenQueryIds = ['#filter-conent-header', '#filter-content-actions', '#filter-location-search-wrapper'];
        for (let curId of childrenQueryIds) {
          let childEl = cardRef.current.querySelector(curId);
          if (childEl) {
            let childRect = childEl.getBoundingClientRect();
            usedHeight += childRect.height;
          }
        }
        setListHeight(parentRect.height - usedHeight);
      }
    }
  }, [parentId, cardRef]);

  /**
   * Handles selecting all the location choices
   * @function
   */
  function handleSelectAll() {
    const curLocations = displayedLocations.map((item) => item.nameProperty);
    const newLocations = curLocations.filter((item) => selectedLocations.findIndex((selItem) => selItem === item) < 0);
    const updateSelections = [...selectedLocations, ...newLocations]
    setSelectedLocations(updateSelections);
    onChange(updateSelections);
    handleClearSearch();
  }

  /**
   * Handles clearing all selected location choices
   * @function
   */
  function handleSelectNone() {
    setSelectedLocations([]);
    onChange([]);
    handleClearSearch();
  }

  /**
   * Handles the user selecting or deselecting a location
   * @function
   * @param {object} event The triggering event data
   * @param {object} location The location to add or remove from the filter
   */
  function handleCheckboxChange(event, location) {

    if (event.target.checked) {
      const curIdx = selectedLocations.findIndex((item) => location.nameProperty === item.nameProperty && 
                                                           location.idProperty === item.idProperty &&
                                                           location.latProperty === item.latProperty &&
                                                           location.lngProperty === item.lngProperty &&
                                                           lcoation.elevationProperty === item.elevationProperty);
      // Add the location in if we don't have it already
      if (curIdx < 0) {
        const curlocations = selectedLocations;
        curlocations.push(location.nameProperty);
        setSelectedLocations(curlocations);
        onChange(curlocations);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the location if we have it
      const curlocations = selectedLocations.filter((item) => item !== location.nameProperty);
      if (curlocations.length < selectedLocations.length) {
        setSelectedLocations(curlocations);
        onChange(curlocations);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  /**
   * Handles a change in the locations search
   * @function
   * @param {object} event The triggering event data
   */
  function handleSearchChange(event) {
    if (event.target.value) {
      const ucSearch = event.target.value.toUpperCase();
      const filtered = locationItems.filter((item) => item.nameProperty.toUpperCase().includes(ucSearch) || 
                                                      item.idProperty.toUpperCase().includes(ucSearch));
      setDisplayedLocations(filtered);
    } else {
      setDisplayedLocations(locationItems);
    }
  }

  /**
   * Handles clearing the locations search
   */
  function handleClearSearch() {
    const searchEl = document.getElementById('file-location-search');
    if (searchEl) {
      searchEl.value = '';
      setDisplayedLocations(locationItems);
    }
  }

  // Return the UI for filtering on locations
  return (
    <FilterCard cardRef={cardRef} title="Locations Filter" onClose={onClose}
                actions={
                <React.Fragment>  
                  <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
                  <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
                </React.Fragment>  
                }
    >
      <Grid sx={{minHeight:listHeight+'px', maxHeight:listHeight+'px', height:listHeight+'px', minWidth:'250px', overflow:'scroll',
                      border:'1px solid black', borderRadius:'5px', paddingLeft:'5px',
                      backgroundColor:'rgb(255,255,255,0.3)'
                    }}>
        <FormGroup>
          { displayedLocations.map((item, idx) => 
              <FormControlLabel key={'filter-locations-' + item.nameProperty + item.latProperty + item.lngProperty + '-' + idx}
                                control={<Checkbox size="small" 
                                                   checked={selectedLocations.findIndex((curLocation) => curLocation===item.nameProperty) > -1 ? true : false}
                                                   onChange={(event) => handleCheckboxChange(event,item)}
                                          />} 
                                label={
                                  <Grid container direction="row" alignItems="center" justifyContent="start" wrap="nowrap" sx={{width:"220px"}}>
                                    <Grid wrap="nowrap">
                                      <Typography variant="body2" sx={{fontWeight:'bold'}}>
                                        {item.idProperty}
                                      </Typography>
                                    </Grid>
                                    <Grid sx={{marginLeft:"auto"}}>
                                      <Typography variant="body2" align="center" sx={{color:'darkgrey'}}>
                                        {item.nameProperty}
                                      </Typography>
                                    </Grid>
                                  </Grid>
                                }
              />
            )
          }
        </FormGroup>
      </Grid>
      <FormControl id='filter-location-search-wrapper' fullWidth variant="standard">
        <TextField
          variant="standard"
          id="file-location-search"
          label="Search"
          slotProps={{
            input: {
              endAdornment:(
                <InputAdornment position="end">
                  <IconButton onClick={handleClearSearch}>
                    <BackspaceOutlined/>
                  </IconButton>
                </InputAdornment>
              )
            },
          }}
          onChange={handleSearchChange}
        />
      </FormControl>
    </FilterCard>
  );
}

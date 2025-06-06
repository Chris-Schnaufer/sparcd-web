/** @module components/FilterCollections */

import * as React from 'react';
import BackspaceOutlinedIcon from '@mui/icons-material/BackspaceOutlined';
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

import { CollectionsInfoContext } from '../serverInfo'
import FilterCard from './FilterCard'

/**
 * Adds collection information to form data
 * @function
 * @param {object} data The saved data to add to the form
 * @param {object} formData The FormData to add the fields to
 */
export function FilterCollectionsFormData(data, formData) {
  formData.append('collections', JSON.stringify(data));
}

/**
 * Returns the UI for filtering by date
 * @function
 * @param {object} {data} Any stored collections data
 * @param {function} onClose The handler for closing this filter
 * @param {function} onChange The handler for when the filter data changes
 * @returns {object} The UI specific for filtering by collection
 */
export default function FilterCollections({data, onClose, onChange}) {
  const theme = useTheme();
  const collectionItems = React.useContext(CollectionsInfoContext);
  const [displayedCollections, setDisplayedCollections] = React.useState(collectionItems); // The visible collections
  const [selectedCollections, setSelectedCollections] = React.useState(data ? data : collectionItems.map((item)=>item.bucket)); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  // Set the initial data if we don't have any
  React.useEffect(() => {
    if (!data) {
      onChange(selectedCollections);
    }
  }, [selectedCollections]);

  /**
   * Handles selecting all collections to the filter
   * @function
   */
  function handleSelectAll() {
    const curCollections = displayedCollections.map((item) => item.bucket);
    const newCollections = curCollections.filter((item) => selectedCollections.findIndex((selItem) => selItem === item) < 0);
    const updatedSelections = [...selectedCollections, ...newCollections];
    setSelectedCollections(updatedSelections);
    onChange(updatedSelections);
    handleClearSearch();
  }

  /**
   * Clears all selected collections
   * @function
   */
  function handleSelectNone() {
    setSelectedCollections([]);
    onChange([]);
    handleClearSearch();
  }

  /**
   * Handles when the user selects or deselects a collection
   * @function
   * @param {object} event The triggering event object
   * @param {string} collectionName The name of the collection to add or remove
   */
  function handleCheckboxChange(event, collectionName) {

    if (event.target.checked) {
      const collectionIdx = selectedCollections.findIndex((item) => collectionName === item);
      // Add the collections in if we don't have it already
      if (collectionIdx < 0) {
        const curCollections = selectedCollections;
        curCollections.push(collectionName);
        setSelectedCollections(curCollections);
        onChange(curCollections);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the collections if we have it
      const curCollections = selectedCollections.filter((item) => item !== collectionName);
      if (curCollections.length < selectedCollections.length) {
        setSelectedCollections(curCollections);
        onChange(curCollections);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  /**
   * Handles the user changing the search criteria
   * @function
   * @param {object} event The triggering event
   */
  function handleSearchChange(event) {
    if (event.target.value) {
      const ucSearch = event.target.value.toUpperCase();
      setDisplayedCollections(collectionItems.filter((item) => item.bucket.toUpperCase().includes(ucSearch)));
    } else {
      setDisplayedCollections(collectionItems);
    }
  }

  /**
   * Handles resetting the search field
   * @function
   */
  function handleClearSearch() {
    const searchEl = document.getElementById('file-collections-search');
    if (searchEl) {
      searchEl.value = '';
      setDisplayedCollections(collectionItems);
    }
  }

  // Return the collection filter UI
  return (
    <FilterCard title="Collections Filter" onClose={onClose}
                actions={
                  <React.Fragment>
                    <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
                    <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
                  </React.Fragment>
                }
    >
      <Grid item sx={{minHeight:'160px', maxHeight:'160px', height:'160px', minWidth:'250px', overflow:'scroll',
                      border:'1px solid black', borderRadius:'5px', paddingLeft:'5px',
                      backgroundColor:'rgb(255,255,255,0.3)'
                    }}>
        <FormGroup>
          { displayedCollections.map((item) => 
              <FormControlLabel key={'filter-collections-' + item.name}
                                control={<Checkbox size="small" 
                                                   checked={selectedCollections.findIndex((curCollections) => curCollections===item.bucket) > -1 ? true : false}
                                                   onChange={(event) => handleCheckboxChange(event,item.bucket)}
                                          />} 
                                label={<Typography variant="body2">{item.name}</Typography>} />
            )
          }
        </FormGroup>
      </Grid>
      <FormControl fullWidth variant="standard">
        <TextField
          variant="standard"
          id="file-collections-search"
          label="Search"
          slotProps={{
            input: {
              endAdornment:(
                <InputAdornment position="end">
                  <IconButton onClick={handleClearSearch}>
                    <BackspaceOutlinedIcon/>
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

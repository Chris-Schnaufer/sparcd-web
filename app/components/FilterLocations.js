/** @module components/FilterLocations */

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

import { LocationsInfoContext } from '../serverInfo'

export default function FilterLocations({data, onClose, onChange}) {
  const theme = useTheme();
  const locationItems = React.useContext(LocationsInfoContext);
  const [displayedLocations, setDisplayedLocations] = React.useState(locationItems); // The visible locations
  const [selectedLocations, setSelectedLocations] = React.useState(data ? data : []); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  function handleSelectAll() {
    const curLocations = displayedLocations.map((item) => item.nameProperty);
    const newLocations = curLocations.filter((item) => selectedLocations.findIndex((selItem) => selItem === item) < 0);
    const updateSelections = [...selectedLocations, ...newLocations]
    setSelectedLocations(updateSelections);
    onChange(updateSelections);
  }

  function handleSelectNone() {
    setSelectedLocations([]);
    onChange([]);
  }

  function handleCheckboxChange(event, locationName) {

    if (event.target.checked) {
      const curIdx = selectedLocations.findIndex((item) => locationName === item);
      // Add the location in if we don't have it already
      if (curIdx < 0) {
        const curlocations = selectedLocations;
        curlocations.push(locationName);
        setSelectedLocations(curlocations);
        onChange(curlocations);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the location if we have it
      const curlocations = selectedLocations.filter((item) => item !== locationName);
      if (curlocations.length < selectedLocations.length) {
        setSelectedLocations(curlocations);
        onChange(curlocations);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  function handleSearchChange(event) {
    if (event.target.value) {
      const ucSearch = event.target.value.toUpperCase();
      const filtered = locationItems.filter((item) => item.nameProperty.toUpperCase().includes(ucSearch) || item.idProperty.toUpperCase().includes(ucSearch));
      setDisplayedLocations(filtered);
    } else {
      setDisplayedLocations(locationItems);
    }
  }

  function handleClearSearch(event) {
    const searchEl = document.getElementById('file-location-search');
    if (searchEl) {
      searchEl.value = '';
      setDisplayedLocations(locationItems);
    }
  }

  return (
    <Card id="filter-location" sx={{backgroundColor:'seashell', border:"none", boxShadow:"none"}}>
      <CardHeader title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid item>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Locations Filter
                        </Typography>
                      </Grid>
                      <Grid item sx={{marginLeft:'auto'}} >
                        <div onClick={onClose}>
                          <Tooltip title="Delete this filter">
                            <Typography gutterBottom variant="body2" noWrap="true"
                                        sx={{textTransform:'uppercase',
                                        color:'grey',
                                        cursor:'pointer',
                                        fontWeight:'500',
                                        backgroundColor:'rgba(0,0,0,0.03)',
                                        padding:'3px 3px 3px 3px',
                                        borderRadius:'3px',
                                        '&:hover':{backgroundColor:'rgba(255,255,255,0.7)', color:'black'}
                                     }}
                            >
                                X
                            </Typography>
                          </Tooltip>
                        </div>
                      </Grid>
                    </Grid>
                    }
                style={{paddingTop:'0px', paddingBottom:'0px'}}
      />
      <CardContent sx={{paddingTop:'0px', paddingBottom:'0px'}}>
          <Grid item sx={{minHeight:'160px', maxHeight:'160px', height:'160px', minWidth:'250px', overflow:'scroll',
                          border:'1px solid black', borderRadius:'5px', paddingLeft:'5px',
                          backgroundColor:'rgb(255,255,255,0.3)'
                        }}>
            <FormGroup>
              { displayedLocations.map((item, idx) => 
                  <FormControlLabel key={'filter-locations-' + item.nameProperty + item.latProperty + item.lngProperty + '-' + idx}
                                    control={<Checkbox size="small" 
                                                       checked={selectedLocations.findIndex((curLocation) => curLocation===item.nameProperty) > -1 ? true : false}
                                                       onChange={(event) => handleCheckboxChange(event,item.nameProperty)}
                                              />} 
                                    label={
                                      <Grid container direction="row" alignItems="center" justifyContent="start" wrap="nowrap" sx={{width:"220px"}}>
                                        <Grid item wrap="nowrap">
                                          <Typography variant="body2" sx={{fontWeight:'bold'}}>
                                            {item.idProperty}
                                          </Typography>
                                        </Grid>
                                        <Grid item sx={{marginLeft:"auto"}}>
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
          <FormControl fullWidth variant="standard">
            <TextField
              variant="standard"
              id="file-location-search"
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
      </CardContent>
      <CardActions>
              <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
              <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
      </CardActions>
    </Card>
  );
}

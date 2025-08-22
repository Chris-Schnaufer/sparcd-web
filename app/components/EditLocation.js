/** @module components/EditLocation */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import CloseOutlinedIcon from '@mui/icons-material/CloseOutlined';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { AddMessageContext, DefaultImageIconURL, geographicCoordinates, LocationsInfoContext, UserSettingsContext } from '../serverInfo';
import { Level } from './Messages';

/**
 * Handles editing a location's entry
 * @function
 * @param {object} {data} The location data. If falsy a new location is assumed
 * @param {function} onUpdate Called to update the location information when changes made
 * @param {function} onClose Called when the editing is completed
 * @return {object} The UI for editing locations
 */
export default function EditLocation({data, onUpdate, onClose}) {
  const theme = useTheme();
  const addMessage = React.useContext(AddMessageContext); // Function adds messages for display
  const locationItems = React.useContext(LocationsInfoContext);
  const userSettings = React.useContext(UserSettingsContext);  // User display settings
  const [isModified, setIsModified] = React.useState(false);
  const [selectedCoordinate, setSelectedCoordinate] = React.useState(userSettings['coordinatesDisplay']);
  const [selectedMeasure, setSelectedMeasure] = React.useState(userSettings['measurementFormat']);

  /**
   * Handles a change in the user's measurement selection
   * @function
   * @param {object} event The event object
   */
  function handleMeasureChange(event) {
    setSelectedMeasure(event.target.value);
  }

  /**
   * Handles a change in the user's coordinate selection
   * @function
   * @param {object} event The event object
   */
  function handleCoordinateChange(event) {
    setSelectedCoordinate(event.target.value);
  }

  /**
   * Handles saving the changes to the user
   * @function
   */
  function onSaveChanges() {
    console.log('HACK:LOCATION MODIFIED:',isModified, data);
    if (!isModified) {
      return;
    }

    // Save the edited location data
    let updatedData = data ? JSON.parse(JSON.stringify(data)) : {};

    let el = document.getElementById('edit-location-name');
    if (el) {
      updatedData.nameProperty = el.value;
      if (updatedData.nameProperty.length <= 0) {
        addMessage(Level.Warning, "Please enter a name for the location");
        el.focus();
        return;
      }
    }

    el = document.getElementById('edit-location-id');
    if (el) {
      updatedData.idProperty = el.value;
      if (updatedData.idProperty.length <= 2) {
        addMessage(Level.Warning, "Please enter a longer location identifier");
        el.focus();
        return;
      }
      const foundId = locationItems.filter((item) => item.idProperty === updatedData.idProperty);
      if (foundId && !data) {
        addMessage(Level.Warning, "The ID is already taken. Please enter an unused ID")
        el.focus();
        return;
      }
    }

    el = document.getElementById('edit-location-active');
    if (el) {
      updatedData.activeProperty = el.value;
    }

    updatedData.measure = selectedMeasure;

    el = document.getElementById('edit-location-elevation');
    if (el) {
      updatedData.elevationProperty = el.value;
      if (updatedData.elevationProperty.length <= 0) {
        addMessage(Level.Warning, "Please enter an elevation");
        el.focus();
        return;
      } else if (parseFloat(updatedData.elevationProperty) === NaN) {
        addMessage(Level.Warning, "Please enter a valid elevation");
        el.focus();
        return;
      }
    }

    updatedData.coordinate = selectedCoordinate;

    if (selectedCoordinate === 'LATLON') {
      el = document.getElementById('edit-location-lat');
      if (el) {
        updatedData.latProperty = el.value;
        if (updatedData.latProperty.length <= 0) {
          addMessage(Level.Warning, "Please enter a latitude");
          el.focus();
          return;
        } else if (parseFloat(updatedData.latProperty) === NaN) {
          addMessage(Level.Warning, "Please enter a valid latitude");
          el.focus();
          return;
        }
      }

      el = document.getElementById('edit-location-lon');
      if (el) {
        updatedData.lngProperty = el.value;
        if (updatedData.lngProperty.length <= 0) {
          addMessage(Level.Warning, "Please enter a valid longitude");
          el.focus();
          return;
        } else if (parseFloat(updatedData.lngProperty) === NaN) {
          addMessage(Level.Warning, "Please enter a valid longitude");
          el.focus();
          return;
        }
      }
    } else {
      el = document.getElementById('edit-location-utm-zone');
      if (el) {
        updatedData.utm_zone = el.value;
        if (updatedData.utm_zone.length <= 0) {
          addMessage(Level.Warning, "Please enter a UTM zone");
          el.focus();
          return;
        } else if (parseInt(updatedData.utm_zone) === NaN) {
          addMessage(Level.Warning, "Please enter a valid UTM zone");
          el.focus();
          return;
        }
      }

      el = document.getElementById('edit-location-utm-letter');
      if (el) {
        updatedData.utm_letter = el.value;
        if (updatedData.utm_letter.length <= 0) {
          addMessage(Level.Warning, "Please enter a UTM letter");
          el.focus();
          return;
        }
      }

      el = document.getElementById('edit-location-utm-x');
      if (el) {
        updatedData.utm_x = el.value;
        if (updatedData.utm_x.length <= 0) {
          addMessage(Level.Warning, "Please enter a UTM X value");
          el.focus();
          return;
        } else if (parseFloat(updatedData.utm_x) === NaN) {
          addMessage(Level.Warning, "Please enter a valid UTM X value");
          el.focus();
          return;
        }
      }

      el = document.getElementById('edit-location-utm-y');
      if (el) {
        updatedData.utm_y = el.value;
        if (updatedData.utm_y.length <= 0) {
          addMessage(Level.Warning, "Please enter a UTM Y value");
          el.focus();
          return;
        } else if (parseFloat(updatedData.utm_y) === NaN) {
          addMessage(Level.Warning, "Please enter a valid UTM Y value");
          el.focus();
          return;
        }
      }
    }

    onUpdate(updatedData, onClose, (message) => addMessage(Level.Warning, message));
  }

  /*
   * Check if we need to break the UTM code into zone and letter
   */
  if (data.utm_code && (!data.utm_zone || !data.utm_letter)) {
    data.utm_zone = parseInt(data.utm_code);
    data.utm_letter = data.utm_code[data.utm_code.length - 1];
  }

  console.log('HACK:',selectedMeasure,selectedCoordinate);
  return (
   <Grid sx={{minWidth:'50vw'}} > 
    <Card id="edit-species" sx={{backgroundColor:'#EFEFEF', border:"none", boxShadow:"none"}} >
      <CardHeader id='edit-species-header' title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Edit Location
                        </Typography>
                      </Grid>
                      <Grid sx={{marginLeft:'auto'}} >
                        <div onClick={onClose}>
                          <Tooltip title="Close without saving">
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
                                <CloseOutlinedIcon size="small" />
                            </Typography>
                          </Tooltip>
                        </div>
                      </Grid>
                    </Grid>
                    }
                style={{paddingTop:'0px', paddingBottom:'0px'}}
      />
      <CardContent id='edit-location-details' sx={{paddingTop:'0px', paddingBottom:'0px'}}>
        <Grid container direction="column" justifyContent="start" alignItems="stretch"
              sx={{minWidth:'400px', border:'1px solid black', borderRadius:'5px', backgroundColor:'rgb(255,255,255,0.3)' }}>
          <TextField required
                id='edit-location-name'
                label="Name"
                defaultValue={data ? data.nameProperty : null}
                size='small'
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <TextField disabled={!!data}
                id='edit-location-id'
                label="ID"
                defaultValue={data ? data.idProperty : null}
                size='small'
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <RadioGroup
            id='edit-location-measure'
            value={selectedMeasure}
            onChange={handleMeasureChange}              
          >
            <Grid container direction="row" spacing={2} justifyContent="stretch" alignItems="center">
              <FormControlLabel value="feet" control={<Radio size="small"/>} label=<Typography gutterBottom variant="body2" noWrap="true">Feet</Typography>
                                                 sx={{paddingLeft:'10px'}}/>
              <FormControlLabel value="meters" control={<Radio size="small"/>} label=<Typography gutterBottom variant="body2" noWrap="true">Meters</Typography>
                                                 />
            </Grid>
          </RadioGroup>
          <TextField 
                id='edit-location-elevation'
                label={"Elevation" + (selectedMeasure === 'feet' ? ' (feet)' : ' (meters)')}
                defaultValue={data ? data.elevationProperty : null}
                size='small'
                sx={{margin:'10px'}}
                onChange={() => setIsModified(true)}
                inputProps={{maxLength:1, style: {fontSize: 12}}}
                slotProps={{
                  inputLabel: {
                    shrink: true,
                  },
                }}
                />
          <RadioGroup
            id='edit-location-measure'
            value={selectedCoordinate}
            onChange={handleCoordinateChange}              
          >
            <Grid container direction="row" spacing={2} justifyContent="stretch" alignItems="center">
            { geographicCoordinates.map((item, idx) => 
                <FormControlLabel value={item.value} key={item.value} 
                                  control={<Radio size="small"/>}
                                                label=<Typography gutterBottom variant="body2" noWrap="true">{item.label}</Typography>
                                                sx={{paddingLeft:idx === 0 ? '10px' : 'revert'}}/>
              )
            }
            </Grid>
          </RadioGroup>
          { selectedCoordinate === 'LATLON' &&
            <React.Fragment>
            <TextField 
                  id='edit-location-lat'
                  label="Latitude"
                  defaultValue={data ? data.latProperty : null}
                  size='small'
                  sx={{margin:'10px'}}
                  onChange={() => setIsModified(true)}
                  inputProps={{style: {fontSize: 12}}}
                  slotProps={{
                    inputLabel: {
                      shrink: true,
                    },
                  }}
                  />
            <TextField 
                  id='edit-location-lon'
                  label="Longitude"
                  defaultValue={data ? data.lngProperty : null}
                  size='small'
                  sx={{margin:'10px'}}
                  onChange={() => setIsModified(true)}
                  inputProps={{style: {fontSize: 12}}}
                  slotProps={{
                    inputLabel: {
                      shrink: true,
                    },
                  }}
                  />
            </React.Fragment>
          }
          { selectedCoordinate === 'UTM' && 
            <React.Fragment>
            <TextField 
                  id='edit-location-utm-zone'
                  label="UTM Zone"
                  defaultValue={data && data.utm_zone ? data.utm_zone : null}
                  size='small'
                  sx={{margin:'10px'}}
                  onChange={() => setIsModified(true)}
                  inputProps={{style: {fontSize: 12}}}
                  slotProps={{
                    inputLabel: {
                      shrink: true,
                    },
                  }}
                  />
            <TextField 
                  id='edit-location-utm-letter'
                  label="Letter"
                  defaultValue={data && data.utm_letter ? data.utm_letter : null}
                  size='small'
                  sx={{margin:'10px'}}
                  onChange={() => setIsModified(true)}
                  inputProps={{style: {fontSize: 12}}}
                  slotProps={{
                    inputLabel: {
                      shrink: true,
                    },
                  }}
                  />
            <TextField 
                  id='edit-location-utm-x'
                  label="X"
                  defaultValue={data ? data.utm_x : null}
                  size='small'
                  sx={{margin:'10px'}}
                  onChange={() => setIsModified(true)}
                  inputProps={{style: {fontSize: 12}}}
                  slotProps={{
                    inputLabel: {
                      shrink: true,
                    },
                  }}
                  />
            <TextField 
                  id='edit-location-utm-y'
                  label="Y"
                  defaultValue={data ? data.utm_y : null}
                  size='small'
                  sx={{margin:'10px'}}
                  onChange={() => setIsModified(true)}
                  inputProps={{style: {fontSize: 12}}}
                  slotProps={{
                    inputLabel: {
                      shrink: true,
                    },
                  }}
                  />
            </React.Fragment>
          }
          <FormControlLabel key={'edit-location-active'} sx={{paddingLeft:'10px'}}
                            control={<Checkbox 
                                               size="small" 
                                               checked={data ? data.activeProperty : false}
                                      />} 
                            label={<Typography variant="body2">Active location entry</Typography>} />
        </Grid>          
        </CardContent>
        <CardActions id='filter-content-actions'>
          <Button sx={{flex:'1', disabled:isModified === false }} onClick={onSaveChanges}>Save</Button>
          <Button sx={{flex:'1'}} onClick={onClose} >Cancel</Button>
        </CardActions>
    </Card>
  </Grid>
  );
}
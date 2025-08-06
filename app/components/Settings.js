/** @module components/Settings */

import * as React from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import FormGroup from '@mui/material/FormGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import { useTheme } from '@mui/material/styles';

import { geographicCoordinates } from '../serverInfo';
import * as utils from '../utils';

// Default settings if we never received them
const defaultSettings = { dateFormat:'MDY', 
                          timeFormat:'24',
                          measurementFormat:'meters',
                          sandersonDirectory:false,
                          sandersonOutput:false,
                          autonext:true,
                          settingsChanged:false,
                          coordinatesDisplay:'LATLON'
                        };

/**
 * Ensures the settings have the same fields as the default
 * @function
 * @param {object} settings The settings to check
 * @return {object} The original or updated settings
 */
function ensure_settings(settings) {
  if (!settings) {
    return defaultSettings;
  }

  for (let one_key of Object.keys(defaultSettings)) {
    if (settings[one_key] === undefined || settings[one_key] === "undefined") {
      settings[one_key] = defaultSettings[one_key]
    }
  }

  return settings;
}

/**
 * Returns the UI for the user's settings
 * @function
 * @param {object} curSettings The working settings
 * @param {function} onChange Handler for when a setting is changed
 * @param {function} onClose Handler for when the settings are to be closed
 * @param {function} onLogout Handler for the user wants to log out
 * @returns {object} Returns the UI to render
 */
export default function Settings({curSettings, onChange, onClose, onLogout}) {
  const theme = useTheme();
  const [changedValue, setChangedValue] = React.useState(null); // Use to force redraw when settings change
  const [email, setEmail] = React.useState(curSettings.email); // The working email
  const [serverURL, setServerURL] = React.useState(utils.getServer());  // The server URL to use
  const [titlebarRect, setTitlebarRect] = React.useState(null); // Set when the UI displays
  const [userSettings, setUserSettings] = React.useState(curSettings ? ensure_settings(curSettings) : defaultSettings);

  // Built-in date formats
  const dateFormats = [
                        {label:'Month Day, Year -- January 3, 2025', value:'MDY', hint:'Full month name, day of month, four digit year'},
                        {label:'Short Month Day, Year -- Jan. 3, 2025', value:'SMDY', hint:'Abbreviated month name, day of month, four digit year'},
                        {label:'Numeric Month/Day/Year -- 1/3/2025', value:'NMDY', hint:'Month as a number, day of month, four digit year'},
                        {label:'Day Month, Year -- 3 January 2025', value:'DMY', hint:'Day of month, full month name, four digit year'},
                        {label:'Day Short Month, Year -- 3 Jan. 2025', value:'DSMY', hint:'Day of month, abbreviated month name, four digit year'},
                        {label:'Numeric Day/Month/Year -- 3/1/2025', value:'DNMY', hint:'Day of month, month as a number, four digit year'},
                        {label:'ISO Local Date -- 2025-1-3', value:'ISO', hint:'Four digit year, numeric month, day of month'},
                      ];
  // Built-in time formats
  const timeFormats = [
                        {label:'24 hour -- 14:36', value:'24', hint:'24 Hour day with minutes'},
                        {label:'24 hour with seconds -- 14:36:52', value:'24s', hint:'24 Hour day with minutes and seconds'},
                        {label:'12 hour with AM/PM-- 2:36 pm', value:'12', hint:'12 Hour day with minutes and AM or PM'},
                        {label:'12 hour with seconds and AM/PM-- 2:36:52 pm', value:'14', hint:'12 Hour day with minutes and seconds and AM or PM'},
                      ];
  // Build-in measurement formats
  const measurementFormats = [
                        {label:'Feet', value:'feet', hint:'Display measurements in feet'},
                        {label:'Meters', value:'meters', hint:'Display measurements in meters'},
                      ];

  // Recalcuate where to place ourselves
  React.useLayoutEffect(() => {
    calculateSizes();
  }, []);

  // Adds a resize handler to the window, and automatically removes it
  React.useEffect(() => {
      function onResize () {
        calculateSizes();
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  // Adds a mouse click handler to the document, and automatically removes it
  React.useEffect(() => {
      function onMouseClick (event) {
        const el = document.getElementById('settings-wrapper');
        const elRect = el.getBoundingClientRect();
        if (event.clientX < elRect.x || event.clientX > elRect.x + elRect.width ||
            event.clientY < elRect.y || event.clientY > elRect.y + elRect.height) {
          onClose();
        }
      }

      document.addEventListener("click", onMouseClick);
  
      return () => {
          document.removeEventListener("click", onMouseClick);
      }
  });

  /**
   * Calculate our sizes and positions
   * @function
   */
  function calculateSizes() {
    const titleEl = document.getElementsByTagName('header');
    if (titleEl) {
      const curRect = titleEl[0].getBoundingClientRect();
      setTitlebarRect(curRect);
      return curRect;
    }

    return null;
  }

  /**
   * Called when the user changes a value
   * @function
   * @param {string} valueKey The key of the value to change
   * @param {object} value The new value to store
   */
  function handleValueChange(valueKey, value) {
    const curSettings = userSettings;
    curSettings[valueKey] = value;
    setUserSettings(curSettings);
    setChangedValue(valueKey + value + '');
    onChange(curSettings);
  }

  /**
   * Handles the user changing the email field
   * @function
   * @param {object} event The event object
   */
  function handleEmailChange(event) {
    setEmail(event.target.value);
  }

  /**
   * Handles the blur of the email field
   * @function
   * @param {object} event The event object
   */
  function handleEmailBlur(event) {
    const curSettings = userSettings;
    curSettings.email = event.target.value;
    setUserSettings(curSettings);
    setChangedValue(event.target.value);
    onChange(curSettings);
  }

  // Default the titlebar dimensions if it's not rendered yet
  let workingRect = titlebarRect;
  if (workingRect == null) {
    workingRect = calculateSizes();
    if (workingRect == null) {
      workingRect = {x:20,y:40,width:640};
    }
  }

  // Return the UI
  return (
    <Box id='settings-wrapper'
         sx={{position:'absolute', top:(workingRect.y+20)+'px', right:'20px',
             border:'1px solid grey', backgroundColor:'silver', boxShadow:'2px 3px 3px #bbbbbb'}}
    >
      <Card id="settings-content">
        <CardHeader title="Settings" />
        <CardContent sx={{paddingTop:'0px', paddingBottom:'0px'}}>
          <Grid container direction="column" alignItems="start" justifyContent="start" wrap="nowrap"
                  spacing={1}
                  sx={{overflowY:'scroll', paddingTop:'5px'}}
          >
            <Grid id="setting-dates" >
              <Autocomplete
                disablePortal
                disableClearable
                options={dateFormats}
                value={dateFormats.find((item) => item.value === userSettings.dateFormat).label}
                onChange={(event, newValue) => handleValueChange('dateFormat', newValue.value)}
                sx={{ width: 300 }}
                renderInput={(params) => <TextField {...params} label="Dates" />}
              />
            </Grid>
            <Grid id="setting-time" >
              <Autocomplete
                disablePortal
                disableClearable
                options={timeFormats}
                value={timeFormats.find((item) => item.value === userSettings.timeFormat).label}
                onChange={(event, newValue) => handleValueChange('timeFormat', newValue.value)}
                sx={{ width: 300 }}
                renderInput={(params) => <TextField {...params} label="Times" />}
              />
            </Grid>
            <Grid id="setting-measurements" >
              <Autocomplete
                disablePortal
                disableClearable
                options={measurementFormats}
                value={measurementFormats.find((item) => item.value === userSettings.measurementFormat).label}
                onChange={(event, newValue) => handleValueChange('measurementFormat', newValue.value)}
                sx={{ width: 300 }}
                renderInput={(params) => <TextField {...params} label="Measurements" />}
              />
            </Grid>
            <Grid id="setting-coordinates" >
              <Autocomplete
                disablePortal
                disableClearable
                options={geographicCoordinates}
                value={geographicCoordinates.find((item) => item.value === userSettings.coordinatesDisplay).label}
                onChange={(event, newValue) => handleValueChange('coordinatesDisplay', newValue.value)}
                sx={{ width: 300 }}
                renderInput={(params) => <TextField {...params} label="Coordinates" />}
              />
            </Grid>
            <Grid id="setting-options" >
              <FormGroup>
                <FormControlLabel
                    control={
                        <Checkbox checked={userSettings.sandersonDirectory}
                                  onChange={(event) => handleValueChange('sandersonDirectory', event.target.checked)}
                        />
                    }
                    label="Dr. Sanderson's Directory Compatibility"
                />
                <FormControlLabel 
                    control={
                        <Checkbox checked={userSettings.sandersonOutput} 
                                  onChange={(event) => handleValueChange('sandersonOutput', event.target.checked)}
                        />
                    }
                    label="Show Dr. Sanderson's Output Replicas"
                />
                <FormControlLabel 
                    control={
                        <Checkbox checked={userSettings.autonext} 
                                  onChange={(event) => handleValueChange('autonext', event.target.checked)}
                        />
                    }
                    label="Automatically Select Next Image"
                />
              </FormGroup>
            </Grid>
            <Grid id="setting-email-wrapper" sx={{width:'100%'}} >
              <TextField id='setting-email' hiddenLabel value={email} variant='outlined' type='email' placeholder='email address'
                          onChange={handleEmailChange} onBlur={handleEmailBlur} pattern=".+@beststartupever\.com"
                          sx={{width:'100%', '&:invalid':{backgroundColor:'rgba(255,0,0.1)'}}} />
            </Grid>
          </Grid>
        </CardContent>
        <CardActions>
          <Grid container id="settings-actions-wrapper" direction="row" sx={{justifyContent:'space-between', alignItems:'center', width:'100%'}}
          >
            <Button variant="contained" onClick={() => onClose()}>Close</Button>
            <Button variant="contained" onClick={() => onLogout()}>Logout</Button>
          </Grid>
        </CardActions>
      </Card>
    </Box>
  );
}
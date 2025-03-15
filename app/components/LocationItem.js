/** @module components/LocationItem */

import * as React from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

/**
 * Returns the UI for a single location with tooltip. The tooltip information
 * is not displayed until the caller specifies that it's available by setting
 * the dataTT parameter to match the propsTT["data-option-index"] parameter field
 * @function
 * @param {string} shortName The short name, or ID, of the location
 * @param {string} longtName The full name of the location
 * @param {float} lat The working latitute of the location
 * @param {float} lng The working longitude of the location
 * @param {function} onTTOpen Handler for when a tool tip opens
 * @param {function} onTTClose Handler for when a tool tip closes
 * @param {object} dataTT Tooltip data
 * @param {object} propsTT Properties related to the tooltip
 * @returns {object} The UI of the location
 */
export default function LocationItem({shortName,longName,lat,lng,elevation, onTTOpen, onTTClose, dataTT, propsTT}) {
  const theme = useTheme();

  return (
    <React.Fragment>
      <Grid container>
        <Grid item sm={6} md={6} lg={6}>
          <Box display="flex" justifyContent="flex-start">
            {shortName}
          </Box>
        </Grid>
      <Grid item sm={6} md={6} lg={6} zeroMinWidth>
        <Box display="flex" justifyContent="flex-end">
          <Typography variant="body" sx={{ fontSize:'small', overflow:"clip"}}>
            {longName}
          </Typography>
          &nbsp;
          <Tooltip
            onOpen={() => onTTOpen(propsTT["data-option-index"])}
            onClose={() => onTTClose(propsTT["data-option-index"])}
            title={
              dataTT && dataTT.index==propsTT["data-option-index"] ?
                <React.Fragment>
                  <Typography color={theme.palette.text.primary} sx={{fontSize:'small'}}>{shortName}</Typography>
                  <Typography color={theme.palette.text.primary} sx={{fontSize:'x-small'}}>{lat+ ", " + lng}</Typography>
                  <Typography color={theme.palette.text.primary} sx={{fontSize:'x-small'}}>{'Elevation: '+elevation}</Typography>
                </React.Fragment>
                : 
                <React.Fragment>
                  <Typography color={theme.palette.text.secondary} sx={{fontSize:'small'}}>{shortName}</Typography>
                  <Typography color={theme.palette.text.secondary} sx={{fontSize:'x-small'}}>{"------, ------"}</Typography>
                  <Typography color={theme.palette.text.secondary} sx={{fontSize:'x-small'}}>{'Elevation: ----'}</Typography>
                  <div style={{...theme.palette.upload_edit_locations_spinner_background}}>
                  <CircularProgress size={40} sx={{position:'absolute', left:'17px', top:'12px'}}/>
                  </div>
                </React.Fragment>
            }
          >
          <InfoOutlinedIcon color="info" fontSize="small" id="InfoOutlinedIcon"/>
          </Tooltip>
        </Box>
        </Grid>
      </Grid>
    </React.Fragment>
  );

}

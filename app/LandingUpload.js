'use client'

/** @module LandingUpload */

import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Grid from '@mui/material/Grid';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import { CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext, TokenContext } from './serverInfo'

/**
 * Returns the UI for uploads on the Landing page
 * @function
 * @param {boolean} loadingSandbox Set to true when the sandbox information is getting loaded
 * @param {function} onChange Function to call when a new upload is selected
 * @returns {object} The rendered UI
 */
export default function LandingUpload({loadingSandbox, onChange}) {
  const theme = useTheme();
  const mobileDevice = React.useContext(MobileDeviceContext);
  const curSandboxInfo = React.useContext(SandboxInfoContext);
  const sandboxToken = React.useContext(TokenContext);
  const [selectedUpload, setSelectedUpload] = React.useState(null);
  const [refreshingUploads, setRefreshingUploads] = React.useState(true);

  /**
   * Handles a change in selected sandbox and calls the parent's change function
   * @function
   * @param {object} event The event object
   */ 
  function handleChange(event) {
    const uploadInfo = JSON.parse(event.target.value);
    setSelectedUpload(event.target.value);
    onChange(uploadInfo);
  }

  // TODO: cache these
  const sandboxItems = curSandboxInfo;
  const firstItem = sandboxItems && sandboxItems.length > 0 ? sandboxItems[0] : null;

  // Render the UI
  return (
    <React.Fragment>
      { firstItem ? (
        <React.Fragment>
          <Grid container direction="row" alignItems="sflex-tart" justifyContent="flex-start">
            <Grid size={{sm:4, md:4, lg:4}} sx={{left:'auto'}}>
              <Typography gutterBottom sx={{ ...theme.palette.landing_upload_prompt,
                          visibility: `${refreshingUploads?"visible":"hidden"}` }} >
                Unpublished uploads
              </Typography>
            </Grid>
            <Grid size={{sm:4, md:4, lg:4}}>
              <Typography gutterBottom sx={{ ...theme.palette.landing_upload_refresh,
                          visibility: `${refreshingUploads?"visible":"hidden"}` }} >
                Refreshing...
              </Typography>
            </Grid>
            <Grid size={{sm:4, md:4, lg:4}}>
              &nbsp;
            </Grid>
          </Grid>
          <Box sx={{ ...theme.palette.landing_upload }} >
            <FormControl>
              <RadioGroup
                name='sandbox-items'
                value={selectedUpload}
                onChange={handleChange}              
              >
                  {
                    sandboxItems && sandboxItems.map(function(obj, idx) {
                      return <FormControlLabel value={JSON.stringify(obj)} control={<Radio />} label={obj.name} key={obj.name} />
                    })
                  }
              </RadioGroup>
            </FormControl>
          </Box>
        </React.Fragment>
        ) : mobileDevice ? <Box>Nothing to do</Box>
            : <Typography gutterBottom sx={{ color: 'text.secondary', fontSize: 14, textAlign: 'center',  }} >
                No sandbox uploads
              </Typography>
      }
    </React.Fragment>
  );
}

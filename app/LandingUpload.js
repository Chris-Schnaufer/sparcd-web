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
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext, TokenContext } from './serverInfo'

/**
 * Returns the UI for uploads on the Landing page
 * @function
 * @param {function} setUploadInfo Function for receving the list of uploads from the server
 * @param {function} onChange Function to call when a new upload is selected
 * @returns {object} The rendered UI
 */
export default function LandingUpload({setUploadInfo, onChange}) {
  const theme = useTheme();
  const mobileDevice = React.useContext(MobileDeviceContext);
  const [selectedUpload, setSelectedUpload] = React.useState(null);
  const [refreshingUploads, setRefreshingUploads] = React.useState(true);
  const [sandboxUploads, setSandboxUploads] = React.useState(null);
  const curSandboxInfo = React.useContext(SandboxInfoContext);
  const sandboxToken = React.useContext(TokenContext);
  const sandboxUrl = React.useContext(BaseURLContext) + '/sandbox&' + sandboxToken;

  /**
   * Fetches the list of "sandbox" uploads from the server
   * @function
   * @returns The list of sandbox items
   */
  function getSandbox() {
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const resp = await fetch(sandboxUrl, {
      'method': 'POST'
    });
    console.log(resp);
    */

    // TODO: Remove refresh
    return [{'collectionId':'11111111-1111-4444-4444-121212121212','name': 'foo'},
            {'collectionId':'11111111-2222-4444-4444-121212121212',
             'name': 'bar',
             'location':'CAN06', 
             'images': [{'name':'image0001', 'url': '../IMAG0120.JPG', 'species': [{'name':'cat','count':'2'},{'name':'deer','count':'0'}]},
                        {'name':'image0002', 'url': '../IMAG0120.JPG', 'species': [{'name':'dog','count':'1'}]},
                        {'name':'image0004', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0005', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0006', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0007', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0008', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0009', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0010', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0011', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0012', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0013', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0014', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0015', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0016', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0017', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0018', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0019', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0020', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0021', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0022', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0023', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0024', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0025', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0026', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0027', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0028', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0029', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0030', 'url': '../IMAG0120.JPG', 'species': []},
                      ]
            }, 
            {'collectionId':'11111111-3333-4444-4444-121212121212','name': 'zar'},
            {'collectionId':'11111111-0000-4444-4444-121212121212','name': 'har'},
            {'collectionId':'11111111-5555-4444-4444-121212121212','name': 'gar'},
            {'collectionId':'11111111-6666-4444-4444-121212121212','name': 'far'},
            {'collectionId':'11111111-7777-4444-4444-121212121212','name': 'dar'},
            {'collectionId':'11111111-8888-4444-4444-121212121212','name': 'car'}];
    //return [];
  }

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
  const sandboxItems = curSandboxInfo || getSandbox();
  const firstItem = sandboxItems.length > 0 ? sandboxItems[0] : null;

  // Set the upload info for the parent
  React.useEffect(() => {
      function handleUploadInfo() {setUploadInfo(sandboxItems);};
      handleUploadInfo();
    },[]);

  // Render the UI
  return (
    <React.Fragment>
      { firstItem ? (
        <React.Fragment>
          <Grid container direction="row" alignItems="sflex-tart" justifyContent="flex-start">
            <Grid item sm={4} md={4} lg={4} sx={{left:'auto'}}>
              <Typography gutterBottom sx={{ ...theme.palette.landing_upload_prompt,
                          visibility: `${refreshingUploads?"visible":"hidden"}` }} >
                Unpublished uploads
              </Typography>
            </Grid>
            <Grid item sm={4} md={4} lg={4}>
              <Typography gutterBottom sx={{ ...theme.palette.landing_upload_refresh,
                          visibility: `${refreshingUploads?"visible":"hidden"}` }} >
                Refreshing...
              </Typography>
            </Grid>
            <Grid item sm={4} md={4} lg={4}>
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
                    sandboxItems.map(function(obj, idx) {
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

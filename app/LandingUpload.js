'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext, TokenContext } from './serverInfo'

export default function LandingUpload({uploadInfo_func, onChange_func}) {
  const theme = useTheme();
  const mobileDevice = React.useContext(MobileDeviceContext);
  const [selectedUpload, setSelectedUpload] = React.useState(null);
  const [refreshingUploads, setRefreshingUploads] = React.useState(true);
  const [sandboxUploads, setSandboxUploads] = React.useState(null);
  const curSandboxInfo = React.useContext(SandboxInfoContext);
  const sandboxToken = React.useContext(TokenContext);
  const sandboxUrl = React.useContext(BaseURLContext) + '/sandbox&' + sandboxToken;

  function getSandbox() {
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const resp = await fetch(sandboxUrl, {
      'method': 'POST'
    });
    console.log(resp);
    */

    // TODO: Remove refresh
    return [{'name': 'foo'},
            {'name': 'bar',
             'location':'CAN06', 
             'images': [{'name':'image1', 'url': '../public/sanimalBackground.JPG', 'species': [{'name':'cat','count':'2'},{'name':'deer','count':'0'}]},
                        {'name':'image2', 'url': '../public/sanimalBackground.JPG', 'species': [{'name':'dog','count':'1'}]},
                        {'name':'image3', 'url': '../public/sanimalBackground.JPG', 'species': null} ]
            }, 
            {'name': 'zar'}, {'name': 'har'}, {'name': 'gar'}, {'name': 'far'}, {'name': 'dar'}, {'name': 'car'}];
    //return [];
  }

  function handleChange(ev) {
    setSelectedUpload(ev.target.value);
    onChange_func(ev.target.value);
  }

  // TODO: cache these
  const sandboxItems = curSandboxInfo || getSandbox();
  const firstItem = sandboxItems.length > 0 ? sandboxItems[0] : null;

  // Set the upload info for the parent
  React.useEffect(() => {
      function setUploadInfo() {uploadInfo_func(sandboxItems);};
      setUploadInfo();
    },[]);

  return (
    <React.Fragment>
      { firstItem ? (
        <React.Fragment>
          <Typography gutterBottom sx={{ ...theme.palette.landing_upload_refresh,
                      visibility: `${refreshingUploads?"visible":"hidden"}` }} >
            Refreshing...
          </Typography>
          <Box sx={{ ...theme.palette.landing_upload }} >
            <FormControl>
              <RadioGroup
                name='sandbox-items'
                value={selectedUpload}
                onChange={handleChange}              
              >
                  {
                    sandboxItems.map(function(obj, idx) {
                      return <FormControlLabel value={obj.name} control={<Radio />} label={obj.name} key={obj.name} />
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

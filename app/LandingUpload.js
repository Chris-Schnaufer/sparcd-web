'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import { useTheme } from '@mui/material/styles';
import { BaseURLContext, MobileDeviceContext, TokenContext } from './serverInfo'

export default function LandingUpload({uploadCount_func}) {
  const theme = useTheme();
  const mobileDevice = React.useContext(MobileDeviceContext);

  function getSandbox() {
    const sandboxToken = React.useContext(TokenContext);
    const sandboxUrl = React.useContext(BaseURLContext) + '/sandbox&' + sandboxToken;
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const resp = await fetch(sandboxUrl, {
      'method': 'POST'
    });
    console.log(resp);
    */

    return [{'name': 'foo'}, {'name': 'bar'}, {'name': 'zar'}, {'name': 'har'}, {'name': 'gar'}, {'name': 'far'}, {'name': 'dar'}, {'name': 'car'}];
    //return [];
  }

  // TODO: cache these
  const sandboxItems = getSandbox();
  const firstItem = sandboxItems.length > 0 ? sandboxItems[0] : null;

  // Set the upload count for the parent
  React.useEffect(() => {
      function setUploadCount() {uploadCount_func(sandboxItems.length);};
      setUploadCount();
    },[]);

  return (
    <React.Fragment>
      { firstItem ? (
        <Box sx={{ border: '1px solid black', maxHeight: '30vh', overflow: 'scroll', padding: '0em 1em 0em 1em'}} >
          <FormControl>
            <RadioGroup
              defaultValue={firstItem.name}
              name='sandbox-items'
            >
                {
                  sandboxItems.map(function(obj, idx) {
                    return <FormControlLabel value={obj.name} control={<Radio />} label={obj.name} key={obj.name} />
                  })
                }
            </RadioGroup>
          </FormControl>
        </Box>
        ) : mobileDevice ? <Box>Nothing to do</Box>: null
      }
    </React.Fragment>
  );
}

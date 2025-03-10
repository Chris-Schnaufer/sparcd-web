'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, TokenContext } from './serverInfo'

export default function LandingCollections({collectionInfo_func, onChange_func}) {
  const theme = useTheme();
  const mobileDevice = React.useContext(MobileDeviceContext);
  const [selectedCollection, setSelectedCollection] = React.useState(null);
  const [refreshingUploads, setRefreshingUploads] = React.useState(true);
  const [collectionsList, setCollectionsList] = React.useState(null);
  const curCollectionsInfo = React.useContext(CollectionsInfoContext);
  const collectionToken = React.useContext(TokenContext);
  const collectionUrl = React.useContext(BaseURLContext) + '/collections&' + collectionToken;

  function getCollections() {
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

  function handleChange(ev) {
    setSelectedCollection(ev.target.value);
    onChange_func(ev.target.value);
  }

  // TODO: cache these
  const collectionItems = curCollectionsInfo || getCollections();
  const firstItem = collectionItems.length > 0 ? collectionItems[0] : null;

  // Set the upload info for the parent
  React.useEffect(() => {
      function setCollectionInfo() {collectionInfo_func(collectionItems);};
      setCollectionInfo();
    },[]);

  return (
    <React.Fragment>
      { firstItem ? (
        <React.Fragment>
          <Typography gutterBottom sx={{ ...theme.palette.landing_collections_refresh,
                      visibility: `${refreshingUploads?"visible":"hidden"}` }} >
            Refreshing...
          </Typography>
          <Box sx={{ ...theme.palette.landing_collections }} >
            <FormControl>
              <RadioGroup
                name='collection-items'
                value={selectedCollection}
                onChange={handleChange}              
              >
                  {
                    collectionItems.map(function(obj, idx) {
                      return <FormControlLabel value={obj.name} control={<Radio />} label={obj.name} key={obj.name} />
                    })
                  }
              </RadioGroup>
            </FormControl>
          </Box>
        </React.Fragment>
        ) : mobileDevice ? <Box>Nothing to do</Box>
            : <Typography gutterBottom sx={{ color: 'text.secondary', fontSize: 14, textAlign: 'center',  }} >
                No collections are available
              </Typography>
      }
    </React.Fragment>
  );
}

'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

import FolderUpload from './components/FolderUpload'
import LandingCard from './components/LandingCard'
import LandingCollections from './LandingCollections'
import LandingUpload from './LandingUpload'
import UserActions from './components/userActions'
import { MobileDeviceContext } from './serverInfo'

export default function Landing({onUserAction}) {
  const theme = useTheme();
  const [numSandboxUploads, setNumSandboxUploads] = React.useState(0);
  const [numCollections, setNumCollections] = React.useState(0);
  const [haveNewUpload, setHaveNewUpload] = React.useState(false);
  const mobileDevice = React.useContext(MobileDeviceContext);

  function updateSandboxCount(uploadCount) {
    setNumSandboxUploads(uploadCount);
  }

  function newUpload() {
    setHaveNewUpload(true);
  }

  function newUploadCancel() {
    setHaveNewUpload(false);
  }

  function updateCollectionCount(uploadCount) {
    setNumCollections(uploadCount);
  }

  function manageSandbox(collection, upload) {

  }

  function renderUploadOverlay() {
    return (
      <Box sx={{ ...theme.palette.screen_disable }} >
        <Grid
          container
          spacing={0}
          direction="column"
          alignItems="center"
          justifyContent="center"
          sx={{ minHeight: '100vh' }}
        >
          <Grid item="true" xs={3}>
            <FolderUpload cancel_func={() => setHaveNewUpload(false)}/>
          </Grid>
        </Grid>
      </Box>
    );
  }

  return (
    <React.Fragment>
      <Box id='landing-page' sx={{ flexGrow: 1 }} sx={{ 'width': '100vw' }} >
        <Grid container rowSpacing={{xs:1, sm:2, md:4}} columnSpacing={{xs:1, sm:2, md:4}} sx={{ 'margin': '4vw' }} >
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Upload Images" 
                         action={[!mobileDevice ? {'title':'New Upload', 'cb':() => newUpload() } : null,
                                  {'title':'Manage', 
                                   'cb':() => {console.log('Manage Sandbox');},
                                   'disabled': numSandboxUploads ? false : true
                                  }
                                 ]}
            >
              <LandingUpload uploadCount_func={updateSandboxCount} />
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Collections"
                         action={{'title':'Manage', 
                                  'cb':() => {console.log('Collections');onUserAction(UserActions.Collection);},
                                  'disabled': numCollections ? false : true}}
            >
              <LandingCollections collectionCount_func={updateCollectionCount} />
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Search Images" 
                         action={{'title':'Query', 'cb':() => {console.log('Query');onUserAction(UserActions.Query);} }}
            >
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Maps"
                         action={{'title':'Maps', 'cb':() => {console.log('Maps');onUserAction(UserActions.Maps);} }}
            >
            </LandingCard>
          </Grid>
        </Grid>
      </Box>
      {haveNewUpload 
        ? renderUploadOverlay()
        : null
      }
    </React.Fragment>
  );
}

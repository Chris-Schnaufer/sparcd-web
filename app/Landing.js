'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid2';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

import LandingCard from './components/LandingCard'
import LandingUpload from './LandingUpload'
import UserActions from './components/userActions'
import { MobileDeviceContext } from './serverInfo'

export default function Landing({onUserAction}) {
  const theme = useTheme();
  const [numSandboxUploads, setNumSandboxUploads] = React.useState(0);
  const [haveNewUpload, setHaveNewUpload] = React.useState(false);
  const mobileDevice = React.useContext(MobileDeviceContext);

  function updateSandboxUploads(newUploads) {
    setNumSandboxUploads(newUploads);
  }

  function newUpload() {
    setHaveNewUpload(true);
  }

  function newUploadCancel() {
    setHaveNewUpload(false);
  }

  function manageSandbox(collection, upload) {

  }

  function renderUploadOverlay() {
    return (
      <Box sx={{'position': 'absolute', 'left': 0, 'top': 0, 'width': '100vw', 'height': '100vh', 'backgroundColor': 'rgba(128, 128, 128, 0.50)'}} >
        <Grid
          container
          spacing={0}
          direction="column"
          alignItems="center"
          justifyContent="center"
          sx={{ minHeight: '100vh' }}
        >
          <Grid item="true" xs={3}>
            <input type="file" name="file" webkitdirectory="true" directory="true"></input>
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
                                  numSandboxUploads ? {'title':'Manage', 'cb':() => {console.log('Manage Sandbox');} } : null
                                 ]}
            >
              <Typography variant="h5" component="div">
                <LandingUpload uploadCount_func={updateSandboxUploads} />
              </Typography>
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Collections"
                         action={{'title':'Manage', 'cb':() => {console.log('Collections');onUserAction(UserActions.Collection);} }}
            >
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

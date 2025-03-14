'use client'

/** @module Landing */

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
import { CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext } from './serverInfo'

/**
 * Returns the UI for the Landing page
 * @function
 * @param {function} onUserAction Function to call when the user clicks an action element
 * @param {function} onSandboxUpdate Function to call when the sandbox information is updated
 * @param {function} onCollectionUpdate Function to call when the collection information is updated
 * @returns {object} The rendered UI
 */
export default function Landing({onUserAction, onSandboxUpdate, onCollectionUpdate}) {
  const theme = useTheme();
  const [haveNewUpload, setHaveNewUpload] = React.useState(false);
  const [selUploadInfo, setSelUploadInfo] = React.useState(null);
  const [selCollectionInfo, setSelCollectionInfo] = React.useState(null);
  const curCollectionInfo = React.useContext(CollectionsInfoContext);
  const curSandboxInfo = React.useContext(SandboxInfoContext);
  const mobileDevice = React.useContext(MobileDeviceContext);

  /**
   * Set the flag indicating there's a new upload
   * @function
   */
  function newUpload() {
    setHaveNewUpload(true);
  }

  /**
   * Set the flag indicating the upload has been cancelled
   * @function
   */
  function newUploadCancel() {
    setHaveNewUpload(false);
  }

  /**
   * Updates the list of image folders uploaded to the sandbox
   * @function
   * @param {array} sandboxInfo The list of objects representing uploaded folders
   */
  function updateSandboxInfo(sandboxInfo) {
//    setSandboxInfo(sandboxInfo);
    onSandboxUpdate(sandboxInfo);
  }

  /**
   * Updates the list of collections
   * @function
   * @param {array} collectionInfo The list of objects representing collections
   */
  function updateCollectionInfo(collectionInfo) {
//    setCollectionsInfo(collectionInfo);
    onCollectionUpdate(collectionInfo);
  }

  /**
   * Sets the selected upload from the sandbox
   * @function
   * @param {object} uploadInfo The selected upload identifier
   */
  function setUploadSelection(uploadInfo) {
    setSelUploadInfo(uploadInfo);
  }

  /**
   * Sets the selected collection
   * @function
   * @param {object} collectionInfo The selected collection identifier
   */
  function setCollectionSelection(collectionInfo) {
    setSelCollectionInfo(collectionInfo);
  }

  /**
   * Called when managing the sandbox
   * @function
   * @param {object} collection The collection the upload belongs to
   * @param {object} upload The upload to edit
   */
  function manageCollection(collection, upload) {

  }

  /**
   * Render the overlay for uploading images
   * @function
   */
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

  // Render the page depending upon user choices
  return (
    <React.Fragment>
      <Box id='landing-page' sx={{ flexGrow: 1, 'width': '100vw' }} >
        <Grid container rowSpacing={{xs:1, sm:2, md:4}} columnSpacing={{xs:1, sm:2, md:4}} sx={{ 'margin': '4vw' }} >
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Upload Images" 
                         action={[!mobileDevice ? {'title':'New Upload', 'onClick':() => newUpload() } : null,
                                  {'title':'Manage', 
                                   'onClick':() => {onUserAction(UserActions.Upload, selUploadInfo, selUploadInfo ? true : false);},
                                   'disabled': curSandboxInfo ? false : true
                                  }
                                 ]}
            >
              <LandingUpload uploadInfo_func={updateSandboxInfo} onChange_func={setUploadSelection} />
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Collections"
                         action={{'title':'Manage', 
                                  'onClick':() => {console.log('Collections');onUserAction(UserActions.Collection, selCollectionInfo);},
                                  'disabled': curCollectionInfo ? false : true}}
            >
              <LandingCollections collectionInfo_func={updateCollectionInfo} onChange_func={setCollectionSelection} />
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Search Images" 
                         action={{'title':'Query', 'onClick':() => {console.log('Query');onUserAction(UserActions.Query);} }}
            >
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Maps"
                         action={{'title':'Maps', 'onClick':() => {console.log('Maps');onUserAction(UserActions.Maps);} }}
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

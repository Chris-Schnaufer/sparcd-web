'use client'

/** @module Landing */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

import FolderUpload from './components/FolderUpload';
import LandingCard from './components/LandingCard';
import LandingCollections from './LandingCollections';
import LandingUpload from './LandingUpload';
import UserActions from './components/userActions';
import { CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext, SizeContext } from './serverInfo';

/**
 * Returns the UI for the Landing page
 * @function
 * @param {boolean} loadingCollections Set to true when collections are being loaded
 * @param {boolean} loadingSandbox Set to true when sandbox items are being loaded
 * @param {function} onUserAction Function to call when the user clicks an action element
 * @param {function} onEditUpload Called when the user wants to edit the selected upload
 * @returns {object} The rendered UI
 */
export default function Landing({loadingCollections, loadingSandbox, onUserAction, onEditUpload}) {
  const theme = useTheme();
  const curCollectionInfo = React.useContext(CollectionsInfoContext);
  const curSandboxInfo = React.useContext(SandboxInfoContext);
  const mobileDevice = React.useContext(MobileDeviceContext);
  const uiSizes = React.useContext(SizeContext);
  const [haveNewUpload, setHaveNewUpload] = React.useState(false);
  const [selUploadInfo, setSelUploadInfo] = React.useState(null);
  const [selCollectionInfo, setSelCollectionInfo] = React.useState(null);

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
   * Handles the user wanting to edit an upload
   * @function
   */
  function handleSandboxEdit() {
    console.log('HACK:UPLOADCLICK:',selUploadInfo);
    const curCollection = curCollectionInfo.find((item) => item.bucket === selUploadInfo.bucket);
    console.log('HACK:    COL:',curCollection);
    const curUpload = selUploadInfo.upload;
    console.log('HACK:    UPL:', curUpload);
    onEditUpload(curCollection.id, curUpload.key, null);
  }

  // Render the page depending upon user choices
  return (
    <React.Fragment>
      <Box id='landing-page' sx={{flexGrow:1, 'width':'100vw', overflow:'scroll'}} >
        <Grid container rowSpacing={{xs:1, sm:2, md:4}} columnSpacing={{xs:1, sm:2, md:4}} sx={{ 'margin': '4vw' }} >
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Upload Images" 
                         action={[!mobileDevice ? {'title':'New Upload', 'onClick':() => newUpload()} : null,
                                  {'title':'Manage', 
                                   'onClick': handleSandboxEdit,
                                   'disabled': curSandboxInfo && curSandboxInfo.length > 0 && selUploadInfo != null ? false : true
                                  }
                                 ]}
            >
              <LandingUpload loadingSandbox={loadingSandbox} onChange={setUploadSelection} />
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Collections"
                         action={{'title':'Manage', 
                                  'onClick':() => onUserAction(UserActions.Collection, selCollectionInfo, false, 'Home'),
                                  'disabled': curCollectionInfo || loadingCollections ? false : true}}
            >
              <LandingCollections loadingCollections={loadingCollections} onChange={setCollectionSelection} />
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Search Images" 
                         action={{'title':'Query', 'onClick':() => {onUserAction(UserActions.Query, null, false, 'Home');} }}
            >
            </LandingCard>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md:6 }}>
            <LandingCard title="Maps"
                         action={{'title':'Maps', 'onClick':() => {onUserAction(UserActions.Maps, null, false, 'Home');} }}
            >
            </LandingCard>
          </Grid>
        </Grid>
      </Box>
      { haveNewUpload && <FolderUpload onCancel={() => setHaveNewUpload(false)}/>
      }
    </React.Fragment>
  );
}

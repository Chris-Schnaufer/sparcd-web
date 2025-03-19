'use client'

/** @module components/FolderUpload */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

import ProgressWithLabel from './ProgressWithLabel'
import { BaseURLContext, TokenContext } from '../serverInfo'

/**
 * Renders the UI for uploading a folder of images
 * @function
 * @param {function} onCancel The function to call when the user cancels the upload
 * @returns {object} The rendered UI
 */
export default function FolderUpload({onCancel}) {
  const theme = useTheme();
  const [uploadingFiles, setUploadingFiles] = React.useState(false);
  const [filesSelected, setFilesSelected] = React.useState(0);
  const [inputSize, setInputSize] = React.useState({'width':252,'height':21}); // Updated when UI rendered
  const uploadToken = React.useContext(TokenContext);
  const uploadUrl = React.useContext(BaseURLContext) + '/upload&' + uploadToken + '&check';

  /**
   * Returns whether or not this is a new upload or a continuation of a previous one
   * @function
   * @param {string} path The path of the upload
   * @param {array} files The list of files to upload
   * @returns {array} An array of files that have not been uploaded (if a continuation) or a false truthiness value 
   *          for a new upload
   */
  function havePreviousUpload(path, files) {
    const formData = new FormData();
    // TODO: Add in a bunch of files and check - loop through all files to see what's not been uploaded
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const resp = await fetch(sandboxUrl, {
      'method': 'POST'
    });
    console.log(resp);
    */

    // Return null (no upload), or a list of files not uploaded
    return null;
  }

  /**
   * Handles uploading a folder of files
   * @function
   */
  function uploadFolder() {
    const formData = new FormData();
    // TODO: Add in a bunch of files and upload - loop through all files
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const fd = new FormData();

    // add all selected files
    e.target.files.forEach((file) => {
      fd.append(e.target.name, file, file.name);  
    });
    
    // create the request
    const xhr = new XMLHttpRequest();
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
          // we done!
      }
    };
    
    // path to server would be where you'd normally post the form to
    xhr.open('POST', '/path/to/server', true);
    xhr.send(fd);
    */
    setUploadingFiles(true);
  }

  /**
   * Handles the user wanting to upload files
   * @function
   * @param {object} event The event
   */
  function uploadFiles(event) {
    const el = document.getElementById('folder_select');

    // Return if there's nothing to do
    if (!el.files || !el.files.length) {
      // TODO: Add message about choosing a non-empty folder
      return;
    }

    const allFiles = el.files;
    let relativePath = allFiles[0].webkitRelativePath;
    if (!relativePath) {
      // TODO: have a problem (remove console.log)
      console.log('ERROR: Missing relative path');
      return;
    }
    relativePath = relativePath.substr(0, relativePath.length - allFiles[0].name.length - 1);

    const resp = havePreviousUpload(relativePath, allFiles);
    if (resp) {
      // Handle the response
    }

    uploadFolder(relativePath, allFiles);
  }

  /**
   * Handles the user changing the selected folder to upload
   * @function
   * @param {object} event The event
   */
  function selectionChanged(event) {
    const el = event.target;

    if (el.files && el.files.length != null) {
      setFilesSelected(el.files.length);
    } else {
      setFilesSelected(0);
    }
  }

  /**
   * Calls the cancelation function when the user clicks cancel
   * @function
   * @param {object} event The event
   */
  function cancelUpload(event) {
    onCancel();
  }

  /**
   * Renders the UI based upon how many images have been uploaded
   * @function
   */
  function renderInputControls() {
    const el = document.getElementById('folder_select');
    let curWidth = inputSize.width;
    let curHeight = inputSize.height;
    if (el) {
      const parentEl = el.parentNode;
      const elSize = el.getBoundingClientRect();

      if (inputSize.width != elSize.width || inputSize.height != elSize.height) {
        setInputSize({'width':elSize.width,'height':elSize.height});
        curWidth = elSize.width;
        curHeight = elSize.height;
      }
    }
    if (uploadingFiles) {
      // TODO: adjust upload percent to include already uploaded images
      return (
        <Grid id="grid" container justifyContent="center" sx={{'minWidth': `${curWidth}px`, 'minHeight':`${curHeight}px`}}>
          <ProgressWithLabel value='10'/>
        </Grid>
      );
    }

    return (
      <input id="folder_select" type="file" name="file" webkitdirectory="true" 
             directory="true" onChange={selectionChanged}></input>
    );
  }

  // Render the UI
  return (
    <Card variant="outlined" sx={{ ...theme.palette.folder_upload }} >
      <React.Fragment>
        <CardHeader sx={{ textAlign: 'center' }} title={
            <Typography gutterBottom variant="h6" component="h4">
              Upload Folder
            </Typography>
           }
           subheader="Select folder to upload"
         />
        <CardContent>
          {renderInputControls()}
        </CardContent>
        <CardActions>
          <Button id="folder_upload" sx={{'flex':'1'}} size="small" onClick={uploadFiles}
                  disabled={filesSelected > 0 ? false : true}>Upload</Button>
          <Button id="folder_cancel" sx={{'flex':'1'}} size="small" onClick={cancelUpload}>Cancel</Button>
        </CardActions>
      </React.Fragment>
    </Card>
  );
}
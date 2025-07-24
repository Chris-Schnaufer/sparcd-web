'use client'

/** @module components/FolderUpload */

import * as React from 'react';
import Autocomplete from '@mui/material/Autocomplete';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import FormControl from '@mui/material/FormControl';
import Grid from '@mui/material/Grid';
import MenuItem from '@mui/material/MenuItem';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { Level } from './Messages';
import LocationItem from './LocationItem';
import ProgressWithLabel from './ProgressWithLabel';
import { AddMessageContext, AllowedImageMime, BaseURLContext, CollectionsInfoContext, LocationsInfoContext,
                SizeContext, TokenContext, UserSettingsContext } from '../serverInfo';
import UploadProgress from './UploadProgress';


const MAX_FILE_SIZE = 80 * 1000 * 1024; // Number of bytes before a file is too large
const MIN_COMMENT_LEN = 10; // Minimum allowable number of characters for a comment
const MAX_CHUNKS = 8; // Maximum number of chunks to break file uploads into

const prevUploadCheckState = {
  noCheck: null,
  checkReset: 1,
  checkNew: 2
};

let curProgressInfo = Array.apply(null, Array(MAX_CHUNKS)).map(() => null);

/**
 * Renders the UI for uploading a folder of images
 * @function
 * @param {function} onCancel The function to call when the user cancels the upload
 * @returns {object} The rendered UI
 */
export default function FolderUpload({onCancel}) {
  const theme = useTheme();
  const addMessage = React.useContext(AddMessageContext); // Function adds messages for display
  const collectionInfo = React.useContext(CollectionsInfoContext);
  const locationItems = React.useContext(LocationsInfoContext);
  const serverURL = React.useContext(BaseURLContext);
  const uiSizes = React.useContext(SizeContext);
  const uploadToken = React.useContext(TokenContext);
  const userSettings = React.useContext(UserSettingsContext);  // User display settings
  const [collectionSelection, setCollectionSelection] = React.useState(null);
  const [comment, setComment] = React.useState(null);
  const [continueUploadInfo, setContinueUploadInfo] = React.useState(null); // Used when continuing a previous upload
  const [curLocationInfo, setCurLocationInfo] = React.useState(null);   // Working location when fetching tooltip
  const [curUploadCounts, setCurUploadCounts] = React.useState(Array.apply(null, Array(MAX_CHUNKS)).map(() => 0));
  const [filesSelected, setFilesSelected] = React.useState(0);
  const [forceRedraw, setForceRedraw] = React.useState(0);
  const [inputSize, setInputSize] = React.useState({'width':252,'height':21}); // Updated when UI rendered
  const [locationSelection, setLocationSelection] = React.useState(null);
  const [newUpload, setNewUpload] = React.useState(false); // Used to indicate that we have  a new upload
  const [newUploadFiles, setNewUploadFiles] = React.useState(null); // The list of files to upload
  const [prevUploadCheck, setPrevUploadCheck] = React.useState(prevUploadCheckState.noCheck); // Used to check if the user wants to perform a reset or new upload
  const [uploadCount, setUploadCount] = React.useState(0); // Number of files to upload
  const [uploadPath, setUploadPath] = React.useState(null);
  const [totalUploadCount, setTotalUploadCount] = React.useState(0); // The total number of files to be uploaded
  const [tooltipData, setTooltipData] = React.useState(null);       // Data for tooltip
  const [uploadingFiles, setUploadingFiles] = React.useState(false);

  const [curProgressError, setCurProgressError] = React.useState(Array.apply(null, Array(MAX_CHUNKS)).map(() => false));
  //const [curProgressInfo, setCurProgressInfo] = React.useState(Array.apply(null, Array(MAX_CHUNKS)).map(() => null));
  const [curProgressRetry, setCurProgressRetry] = React.useState(Array.apply(null, Array(MAX_CHUNKS)).map(() => 0));
  const [splitFiles, setSplitFiles] =  React.useState(null); // Split file list for uploading
  const [uploadId, setUploadId] = React.useState(null); // Contains the upload ID

  let testing = Array.apply(null, Array(MAX_CHUNKS)).map(() => null);

  let curLocationFetchIdx = -1; // Working index of location data to fetch

  const getTooltipInfoOpen = getTooltipInfo.bind(FolderUpload);

  let displayCoordSystem = 'LATLON';
  if (userSettings['coordinatesDisplay']) {
    displayCoordSystem = userSettings['coordinatesDisplay'];
  }

  /**
   * Calls the server to get location details for tooltips
   * @function
   * @param {int} locIdx The index of the location to get the details for
   */
  function getTooltipInfo(locIdx) {
    if (curLocationFetchIdx != locIdx) {
      curLocationFetchIdx = locIdx;
      const cur_loc = locationItems[curLocationFetchIdx];
      const locationInfoUrl = serverURL + '/locationInfo?t=' + encodeURIComponent(uploadToken);

      const formData = new FormData();

      formData.append('id', cur_loc.idProperty);
      formData.append('name', cur_loc.nameProperty);
      formData.append('lat', cur_loc.latProperty);
      formData.append('lon', cur_loc.lngProperty);
      formData.append('ele', cur_loc.elevationProperty);
      try {
        const resp = fetch(locationInfoUrl, {
          credentials: 'include',
          method: 'POST',
          body: formData
        }).then(async (resp) => {
              if (resp.ok) {
                return resp.json();
              } else {
                throw new Error(`Failed to get location information: ${resp.status}`, {cause:resp});
              }
            })
          .then((respData) => {
              // Save tooltip information
              const locInfo = Object.assign({}, respData, {'index':curLocationFetchIdx});

              if (locIdx === curLocationFetchIdx) {
                setTooltipData(locInfo);
              }
                })
          .catch(function(err) {
            console.log('Location tooltip Error: ',err);
        });
      } catch (error) {
        console.log('Location tooltip Unknown Error: ',err);
      }
    }
  }

  /**
   * Clears tooltip information when no longer needed. Ensures only the working tooltip is cleared
   * @function
   * @param {int} locIdx The index of the location to clear
   */
  function clearTooltipInfo(locIdx) {
    // Only clear the information if we're the active tooltip
    if (locIdx == curLocationFetchIdx) {
      setCurLocationInfo(null);
    }
  }

  /**
   * Returns whether or not this is a new upload or a continuation of a previous one
   * @function
   * @param {string} path The path of the upload
   * @param {array} files The list of files to upload
   * @returns {array} An array of files that have not been uploaded (if a continuation) or a false truthiness value 
   *          for a new upload
   */
  function checkPreviousUpload(path, files) {
    const sandboxPrevUrl = serverURL + '/sandboxPrev?t=' + encodeURIComponent(uploadToken);
    const formData = new FormData();
    console.log('HACK:PREV UPLOAD');

    formData.append('path', path);

    try {
      const resp = fetch(sandboxPrevUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to check upload: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Process the results
            console.log('HACK:RESPONSE:', respData);
            if (respData.exists === false) {
              setNewUpload(true);
              setNewUploadFiles(files);
              setUploadPath(path);
            } else {
              setUploadPath(path);

              // Acknowledge that upload should continue or be restarted or as a new one
              const notLoadedFiles = files.filter((item) => !respData.uploadedFiles.includes(item.webkitRelativePath));
              setContinueUploadInfo({files: notLoadedFiles,
                                     elapsedSec: parseInt(respData.elapsed_sec),
                                     allFiles: files,
                                     id:respData.id})
            }
        })
        .catch(function(err) {
          console.log('Previous Upload Error: ',err);
          addMessage(Level.Error, 'A problem ocurred while preparing for upload');
      });
    } catch (error) {
      console.log('Prev Upload Unknown Error: ',err);
      addMessage(Level.Error, 'An unkown problem ocurred while preparing for upload');
    }
  }

  /**
   * Uploads chunks of files from the list
   * @function
   * @param {object} fileChunk The array of files to upload
   * @param {string} uploadId The ID of the upload
   * @param {number} uploadIndex The index of this upload chunk for tracking upload counts
   * @param {number} attempts The remaining number of attempts to try
   */
  function uploadChunk(fileChunk, uploadId, uploadIndex, totalUploads, attempts = 3) {
    const sandboxFileUrl = serverURL + '/sandboxFile?t=' + encodeURIComponent(uploadToken);
    const formData = new FormData();
    const NUM_FILES_UPLOAD = 1;
    const myUploadCount = curUploadCounts[uploadIndex];  // The current number of uploads we've done
    console.log('HACK:UPLOAD CHUNK');

    formData.append('id', uploadId);
    for (let idx = 0; idx < NUM_FILES_UPLOAD && idx < fileChunk.length; idx++) {
      formData.append(fileChunk[idx].name, fileChunk[idx]);
    }

    try {
      const resp = fetch(sandboxFileUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to check upload: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Process the results
            const chunkUploadCount = curUploadCounts[uploadIndex] + Math.min(NUM_FILES_UPLOAD, fileChunk.length);
            setCurUploadCounts(curUploadCounts.map((item,idx) => idx == uploadIndex ? chunkUploadCount : item));
            const nextChunk = fileChunk.slice(NUM_FILES_UPLOAD);
            setForceRedraw(forceRedraw + 1);

            if (nextChunk.length > 0) {
              window.setTimeout(() => uploadChunk(nextChunk, uploadId, uploadIndex, totalUploads), 10);
            } else {
              console.log('HACK: Done UPLOAD');
              // Check if everyone is done
              let curUploadTotal = chunkUploadCount;
              for (let idx = 0; idx < curUploadCounts.length; idx++) {
                curUploadTotal += curUploadCounts[idx];
              }
              if (curUploadTotal === totalUploads) {
                console.log('HACK:EVERYTHING UPLOADED');
              }
            }
        })
        .catch(function(err) {
          if (attempts == 3) {
            console.log('Upload File Error: ',err);
          }
          if (--attempts > 0) {
            uploadChunk(fileChunk, uploadId, uploadIndex, totalUploads, attempts);
          } else {
            // TODO: Only show this message once
            addMessage(Level.Error, 'A problem ocurred while uploading images');
          }
      });
    } catch (error) {
      console.log('Upload Images Unknown Error: ',err);
      // TODO: Only show this message once
      addMessage(Level.Error, 'An unkown problem ocurred while uploading images');
    }
  }

  /**
   * Marks the upload as completed
   * @function
   * @param {string} uploadId The ID of the upload that's completed
   */
  function uploadCompleted(uploadId) {
    const sandboxCompleteUrl = serverURL + '/sandboxCompleted?t=' + encodeURIComponent(uploadToken);
    const formData = new FormData();

    formData.append('id', uploadId);

    try {
      const resp = fetch(sandboxCompleteUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to mark upload as completed: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Process the results
            console.log('HACK:COMPLETED UPLOAD');
            // TODO: Navigate to upload edit page
        })
        .catch(function(err) {
          console.log('Upload Images Completed Error: ', err);
          addMessage(Level.Error, 'A problem ocurred while completing image upload');
      });
    } catch (error) {
      console.log('Upload Images Completed Unknown Error: ',err);
      addMessage(Level.Error, 'An unkown problem ocurred while completing image upload');
    }
  }

  /**
   * Handles uploading a folder of files
   * @function
   * @param {array} uploadFiles The list of files to upload
   * @param {string} curUploadId The ID associated with the upload
   */
  function uploadFolder(uploadFiles, curUploadId) {
    // Check that we have something to upload
    if (!uploadFiles || uploadFiles.length <= 0) {
      // TODO: Make the message part of the displayed window?
      // TODO: Change to editing upload page after marking as complete
      addMessage(Level.Information, 'All files have been uploaded already');
      console.log('All files were uploaded', curUploadId);
      uploadCompleted(curUploadId);
      return;
    }

    setUploadingFiles(true);
    setTotalUploadCount(uploadFiles.length);

    // Figure out how many instances we want sending data
    const numInstance = uploadFiles.length < MAX_CHUNKS ? uploadFiles.length : MAX_CHUNKS;
    setCurUploadCounts(Array.apply(null, Array(MAX_CHUNKS)).map(() => 0));
    setCurProgressRetry(Array.apply(null, Array(MAX_CHUNKS)).map(() => 0));
    setCurProgressError(Array.apply(null, Array(MAX_CHUNKS)).map(() => false));

    const chunkSize = Math.ceil(uploadFiles.length / (numInstance * 1.0));
    let splitFiles = [];
    for (let idx = 0; idx < uploadFiles.length; idx += chunkSize) {
      splitFiles.push(uploadFiles.slice(idx, idx + chunkSize));
    }

    setSplitFiles(splitFiles);
    setUploadId(curUploadId);

//    for (let idx = 0; idx < splitFiles.length; idx++) {
//      window.setTimeout(() => uploadChunk(splitFiles[idx], curUploadId, idx, uploadFiles.length), 10);
//    }
//
//    setUploadCount(uploadFiles.length);

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
      addMessage(Level.Information, 'Please choose a folder with files to upload');
      return;
    }

    const allFiles = el.files;

    // Ensure that they aren't too large and that they're an acceptable image type
    let haveUnknown = 0;
    let tooLarge = 0;
    let allowedFiles = [];
    for (const one_file of allFiles) {
      if (one_file.size === undefined || one_file.type === undefined) {
        haveUnknown++;
      }
      if (one_file.type) {
        if (AllowedImageMime.find((item) => item.toLowerCase === one_file.type.toLowerCase) !== undefined) {
          if (!one_file.size || one_file.size <= MAX_FILE_SIZE) {
            allowedFiles.push(one_file);
          } else if (one_file.size && one_file.size > MAX_FILE_SIZE) {
            tooLarge++;
          }
        }
      }
    }

    // Let the user know if we have no more files left, or if we have some allowed files that are too large
    if (allowedFiles.length <= 0) {
      addMessage(Level.Information, 'No acceptable image files were found. Please choose another folder')
      console.log('No files left to upload: start count:', allFiles.length, ' unknown:',haveUnknown, ' too large:', tooLarge);
      return;
    }
    if (tooLarge > 0) {
      const maxMB = Math.round(MAX_FILE_SIZE / (1000.0 * 1024.0) * 100) / 100.0;
      addMessage(Level.Information, `Found ${tooLarge} files that are too large and won't be uploaded. Max size: ${maxMB}MB`);
    }

    // Check for a previous upload
    let relativePath = allowedFiles[0].webkitRelativePath;
    if (!relativePath) {
      addMessage(Level.Error, 'Unable to determine the source path. Please contact the developer of this site');
      console.log('ERROR: Missing relative path');
      console.log(allowedFiles[0]);
      return;
    }
    relativePath = relativePath.substr(0, relativePath.length - allowedFiles[0].name.length - 1);

    checkPreviousUpload(relativePath, allowedFiles);
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
   */
  function cancelUpload() {
    onCancel();
  }

  /**
   * Handles the user cancelling the current upload
   * @function
   */
  function cancelDetails() {
    setNewUpload(false);
    setNewUploadFiles(null);
  }

  /**
   * Handles when the user wants to continue a new upload
   * @function
   */
  function continueNewUpload() {
    // Add the upload to the server
    const sandboxNewUrl = serverURL + '/sandboxNew?t=' + encodeURIComponent(uploadToken);
    const formData = new FormData();
    console.log('HACK:CONTINUE NEW UPLOAD');

    formData.append('collection', collectionSelection.id);
    formData.append('location', locationSelection.idProperty);
    formData.append('path', uploadPath);
    formData.append('comment', comment);
    formData.append('files', JSON.stringify(newUploadFiles.map((item) => item.webkitRelativePath)));
    formData.append('ts', new Date().toISOString());
    formData.append('tz', Intl.DateTimeFormat().resolvedOptions().timeZone);

    try {
      const resp = fetch(sandboxNewUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to add new sandbox upload: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Process the results
            console.log('HACK:NEW SANDBOX RESPONSE:', respData);
            setNewUpload(false);
            window.setTimeout(() => uploadFolder(newUploadFiles, respData.id), 10);
        })
        .catch(function(err) {
          console.log('New Sandbox Error: ',err);
          addMessage(Level.Error, 'A problem ocurred while preparing for new sandbox upload');
      });
    } catch (error) {
      console.log('New Upload Unknown Error: ',err);
      addMessage(Level.Error, 'An unkown problem ocurred while preparing for new sandbox upload');
    }
  }

  /**
   * Continues a previous upload of images
   * @function
   */
  function prevUploadContinue() {
    setUploadingFiles(true);
    uploadFolder(continueUploadInfo.files, continueUploadInfo.id);
    setContinueUploadInfo(null);
  }

  /**
   * Restarts a folder upload
   * @function
   */
  function prevUploadRestart() {
    // If no images were uploaded, just restart the complete upload
    if (continueUploadInfo.files.length === continueUploadInfo.allFiles.length) {
      uploadFolder(continueUploadInfo.allFiles.length, continueUploadInfo.allFiles.id);
      setContinueUploadInfo(null);
    } else {
      setPrevUploadCheck(prevUploadCheckState.checkReset);
    }
  }

  /**
   * Handles restarting an upload from the beginning
   * @function
   */
  function prevUploadResetContinue() {
    // Reset the upload on the server and then restart the upload
    const sandboxResetUrl = serverURL + '/sandboxReset?t=' + encodeURIComponent(uploadToken);
    const formData = new FormData();
    console.log('HACK:RESET UPLOAD');

    formData.append('id', continueUploadInfo.id);
    formData.append('files', JSON.stringify(continueUploadInfo.files.map((item) => item.webkitRelativePath)));
    formData.append('ts', new Date().toISOString());
    formData.append('tz', Intl.DateTimeFormat().resolvedOptions().timeZone);

    try {
      const resp = fetch(sandboxResetUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to reset sandbox upload: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Process the results
            console.log('HACK:RESET SANDBOX RESPONSE:', respData);
            const curFiles = continueUploadInfo.files;
            const upload_id = continueUploadInfo.id;
            setPrevUploadCheck(prevUploadCheckState.noCheck);
            setContinueUploadInfo(null);
            window.setTimeout(() => uploadFolder(curFiles, upload_id), 10);
        })
        .catch(function(err) {
          console.log('Reset Sandbox Error: ',err);
          addMessage(Level.Error, 'A problem ocurred while preparing for reset sandbox upload');
      });
    } catch (error) {
      console.log('Reset Upload Unknown Error: ',err);
      addMessage(Level.Error, 'An unkown problem ocurred while preparing for reset sandbox upload');
    }
}

  /**
   * Creates a new upload for these files
   * @function
   */
  function prevUploadCreateNew() {
    setPrevUploadCheck(prevUploadCheckState.checkNew);
  }

  /**
   * Handles creating a new upload separate from an existing one
   * @function
   */
  function prevUploadCreateNewContinue() {
    const sandboxCompletedUrl = serverURL + '/sandboxCompleted?t=' + encodeURIComponent(uploadToken);
    const formData = new FormData();
    console.log('HACK:CREATE NEW UPLOAD');

    formData.append('id', continueUploadInfo.id);

    try {
      const resp = fetch(sandboxCompletedUrl, {
        method: 'POST',
        body: formData
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed for new reset sandbox upload: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
            // Process the results
            console.log('HACK:CREATE NEW SANDBOX RESPONSE:', respData);
            const uploadFiles = continueUploadInfo.allFiles;
            setContinueUploadInfo(null);
            setCollectionSelection(null);
            setLocationSelection(null);
            setComment(null);
            setNewUpload(true);
            setNewUploadFiles(uploadFiles);
        })
        .catch(function(err) {
          console.log('Reset New Sandbox Error: ',err);
          addMessage(Level.Error, 'A problem ocurred while preparing for a new sandbox upload');
      });
    } catch (error) {
      console.log('Reset New Unknown Error: ',err);
      addMessage(Level.Error, 'An unkown problem ocurred while preparing for a new sandbox upload');
    }
  }

  /**
   * Keeps track of a new user collection selection
   * @function
   * @param {object} event The event object
   * @param {object} value The selected collection
   */
  function handleCollectionChange(event, value) {
    setCollectionSelection(value);
    if (locationSelection !== null && comment != null && comment.length > MIN_COMMENT_LEN) {
      setForceRedraw(forceRedraw + 1);
    }
  }

  /**
   * Keeps track of a new user location selection
   * @function
   * @param {object} event The event object
   * @param {object} value The selected location
   */
  function handleLocationChange(event, value) {
    setLocationSelection(value);
    if (collectionSelection !== null && comment != null && comment.length > MIN_COMMENT_LEN) {
      setForceRedraw(forceRedraw + 1);
    }
  }

  /**
   * Handles the user changing the comment
   * @function
   * @param {object} event The triggering event
   */
  function handleCommentChange(event) {
    setComment(event.target.value);
    if (event.target.value != null && event.target.value.length > MIN_COMMENT_LEN && collectionSelection != null && locationSelection != null) {
      setForceRedraw(forceRedraw + 1);
    }
  }

  /**
   * Generates elapsed time string based upon the number of seconds specified
   * @function
   * @param {number} seconds The number of seconds to format
   * @return {string} The formatted string
   */
  function generateSecondsElapsedText(seconds) {
    let results = '';
    let remain_seconds = seconds;

    // Days
    let cur_num = Math.floor(remain_seconds / (24 * 60 * 60));
    if (cur_num > 0) {
      results += `${cur_num} hours `;
      remain_seconds -= cur_num * (24 * 60 * 60);
    }

    // Hours
    cur_num = Math.floor(remain_seconds / (60 * 60));
    if (results.length > 0 || cur_num > 0) {
      results += `${cur_num} hours `;
      remain_seconds -= cur_num * (60 * 60);
    }

    // Minutes
    cur_num = Math.floor(remain_seconds / 60);
    if (results.length > 0 || cur_num > 0) {
      results += `${cur_num} minutes `;
      remain_seconds -= cur_num * 60;
    }

    // Seconds
    if (results.length > 0 || remain_seconds > 0) {
      results += `${remain_seconds} seconds `;
    }

    return results;
  }

  /**
   * Renders the UI based upon how many images have been uploaded
   * @function
   * @return {object} The UI to render
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
      let uploadCount = 0.0;
      for (const curCount of curUploadCounts) {
        uploadCount += curCount;
      }
      let percentComplete = totalUploadCount ? Math.round((uploadCount / totalUploadCount) * 100) : 100;

      return (
        <Grid id="grid" container justifyContent="center" sx={{minWidth: curWidth+'px', minHeight: curHeight+'px'}}>
          <ProgressWithLabel value={percentComplete}/>
        </Grid>
      );
    }

    return (
      <input id="folder_select" type="file" name="file" webkitdirectory="true" 
             directory="true" onChange={selectionChanged}></input>
    );
  }

  /**
   * Renders the details controls for a new upload
   * @function
   * @return {object} The UI to render
   */
  function renderUploadDetails() {
    return (
      <Grid id='folder-upload-details-wrapper' container direction="column" alignItems="center" justifyContent="start" gap={2}>
        <FormControl fullWidth>
          <Autocomplete
            options={collectionInfo}
            id="folder-upload-collections"
            autoHighlight
            onChange={handleCollectionChange}
            defaultValue={null}
            getOptionLabel={(option) => option.name}
            getOptionKey={(option) => option.name+option.id}
            renderOption={(props, col) => {
              const { key, ...optionProps } = props;
              return (
                  <MenuItem id={col.id+'-'+key} value={col.name} key={key} {...optionProps}>
                    {col.name}
                  </MenuItem> 
              );
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Collection"
                required={true}
                slotProps={{
                  htmlInput: {
                    ...params.inputProps,
                    autoComplete: 'new-password', // disable autocomplete and autofill
                  },
                }}
              />
            )}
          >
          </Autocomplete>
        </FormControl>
        <FormControl fullWidth>
          <Autocomplete
            options={locationItems}
            id="folder-upload-location"
            autoHighlight
            onChange={handleLocationChange}
            defaultValue={null}
            getOptionLabel={(option) => option.idProperty}
            getOptionKey={(option) => option.idProperty+option.latProperty+option.lngProperty}
            renderOption={(props, loc) => {
              const { key, ...optionProps } = props;
              return (
                  <MenuItem id={loc.idProperty+'-'+key} value={loc.idProperty} key={key} {...optionProps}>
                    <LocationItem shortName={loc.idProperty} longName={loc.nameProperty}
                                  lat={displayCoordSystem === 'LATLON' ? loc.latProperty : loc.utm_x} 
                                  lng={displayCoordSystem === 'LATLON' ? loc.lngProperty: loc.utm_y} 
                                  elevation={userSettings['measurementFormat'] === 'feet' ? meters2feet(loc.elevationProperty) + 'ft' : loc.elevationProperty}
                                  coordType={displayCoordSystem === 'LATLON' ? undefined : loc.utm_code}
                                  onTTOpen={getTooltipInfoOpen} onTTClose={clearTooltipInfo}
                                  dataTT={tooltipData} propsTT={props}
                     />
                  </MenuItem> 
              );
            }}
            renderInput={(params) => (
              <TextField
                {...params}
                label="Location"
                required={true}
                slotProps={{
                  htmlInput: {
                    ...params.inputProps,
                    autoComplete: 'new-password', // disable autocomplete and autofill
                  },
                }}
              />
            )}
          >
          </Autocomplete>
        </FormControl>
        <FormControl fullWidth>
          <Grid container direction="column" alignContent="start" justifyContent="start" sx={{paddingTop:"10px"}} >
            <Typography gutterBottom variant="body">
              Mountain Range - Site Name - No. of images collected - Date Uploaded - Date collected
            </Typography>
            <Typography gutterBottom variant="body2">
              (e.g.: Santa Rita Mountains - SAN06 - 39 images - uploaded 04-10-2020 - collected 03-28-2000)
            </Typography>
            <TextField required fullWidth id="folder-upload-comment" label="Comment" onChange={handleCommentChange} />
          </Grid>
        </FormControl>
      </Grid>
    );
  }

  // Render the UI
  const details_continue_enabled = locationSelection != null && collectionSelection != null && comment != null && comment.length > MIN_COMMENT_LEN;
  return (
    <React.Fragment>
    { newUpload === false ?
      <Card id='folder-upload-select' variant="outlined" sx={{ ...theme.palette.folder_upload }} >
        <CardHeader sx={{ textAlign: 'center' }}
           title={
            <Typography gutterBottom variant="h6" component="h4">
              Upload Folder
            </Typography>
           }
           subheader={
            <React.Fragment>
              <Typography gutterBottom variant="body">
                Select folder to upload
              </Typography>
              <br />
              <Typography gutterBottom variant="body2">
                Step {!uploadingFiles ? '1' : '3'} of 3
              </Typography>
            </React.Fragment>
            }
         />
        <CardContent>
          {renderInputControls()}
        </CardContent>
        <CardActions>
        { !uploadingFiles &&
          <React.Fragment>
            <Button id="folder_upload" sx={{'flex':'1'}} size="small" onClick={uploadFiles}
                    disabled={filesSelected > 0 ? false : true}>Upload</Button>
            <Button id="folder_cancel" sx={{'flex':'1'}} size="small" onClick={cancelUpload}>Cancel</Button>
          </React.Fragment>
        }
        </CardActions>
      </Card>
    :
       <Card id='folder-upload-details' variant="outlined" sx={{ ...theme.palette.folder_upload, minWidth:(uiSizes.workspace.width * 0.8) + 'px' }} >
        <CardHeader sx={{ textAlign: 'center' }}
           title={
            <Typography gutterBottom variant="h6" component="h4">
              New Upload Details
            </Typography>
           }
           subheader={
            <React.Fragment>
              <Typography gutterBottom variant="body">
                Select Collection and Location to proceed
              </Typography>
              <br />
              <Typography gutterBottom variant="body2">
                Step 2 of 3
              </Typography>
            </React.Fragment>
            }
         />
        <CardContent>
          {renderUploadDetails()}
        </CardContent>
        <CardActions>
          <Button id="sandbox-upload-details-continue" sx={{'flex':'1'}} size="small" onClick={continueNewUpload}
                  disabled={details_continue_enabled ? false : true}>Continue</Button>
          <Button id="sandbox-upload-details-cancel" sx={{'flex':'1'}} size="small" onClick={cancelDetails}>Cancel</Button>
        </CardActions>
      </Card>
    }
    { continueUploadInfo !== null && 
        <Card id='folder-upload-continue' variant="outlined" sx={{ ...theme.palette.folder_upload, minWidth:(uiSizes.workspace.width * 0.8) + 'px' }} >
        <CardHeader sx={{ textAlign: 'center' }}
           title={
            <Typography gutterBottom variant="h6" component="h4">
              Upload Already Started
            </Typography>
           }
          />
        <CardContent>
          <Typography gutterBottom variant="body">
            An incomplete upload from '{uploadPath}' has been detected. How would you like to proceed?
          </Typography>
          <Typography gutterBottom variant="body2">
            {continueUploadInfo.allFiles.length-continueUploadInfo.files.length} out of {continueUploadInfo.allFiles.length} files have been uploaded
          </Typography>
          <Typography gutterBottom variant="body2">
            Uploaded created {generateSecondsElapsedText(continueUploadInfo.elapsedSec)} ago
          </Typography>
        </CardContent>
        <CardActions>
          <Button id="sandbox-upload-continue-continue" sx={{'flex':'1'}} size="small" onClick={prevUploadContinue}>Continue Upload</Button>
          <Button id="sandbox-upload-continue-restart" sx={{'flex':'1'}} size="small" onClick={prevUploadRestart}>Restart Upload</Button>
          <Button id="sandbox-upload-continue-create" sx={{'flex':'1'}} size="small" onClick={prevUploadCreateNew}>Create New Upload</Button>
          <Button id="sandbox-upload-continue-cancel" sx={{'flex':'1'}} size="small" onClick={() => setContinueUploadInfo(null)}>Cancel</Button>
        </CardActions>
     </Card>
   }
   { (continueUploadInfo !== null && prevUploadCheck !== prevUploadCheckState.noCheck) &&
        <Card id='folder-upload-reset' variant="outlined" sx={{ ...theme.palette.folder_upload, minWidth:(uiSizes.workspace.width * 0.8) + 'px' }} >
        <CardHeader sx={{ textAlign: 'center' }}
           title={
            <Typography gutterBottom variant="h6" component="h4">
              {prevUploadCheck === prevUploadCheckState.checkReset & "Restart Upload"}
              {prevUploadCheck === prevUploadCheckState.checkNew & "Create New Upload"}
            </Typography>
           }
          />
        <CardContent>
          <Typography gutterBottom variant="body">
            {prevUploadCheck === prevUploadCheckState.checkReset & "Are you sure you want to delete the previous uploaded files and restart?"}
            {prevUploadCheck === prevUploadCheckState.checNew & "Are you sure you want to abandon the previous uploaded?"}
          </Typography>
        </CardContent>
        <CardActions>
          {prevUploadCheck === prevUploadCheckState.checkReset & 
            <Button id="sandbox-upload-continue-yes" sx={{'flex':'1'}} size="small" onClick={prevUploadResetContinue}>Yes</Button>
          }
          {prevUploadCheck === prevUploadCheckState.checkNew & 
            <Button id="sandbox-upload-continue-yes" sx={{'flex':'1'}} size="small" onClick={prevUploadCreateNewContinue}>Yes</Button>
          }
          <Button id="sandbox-upload-continue-no" sx={{'flex':'1'}} size="small" onClick={() => setPrevUploadCheck(prevUploadCheckState.noCheck)}>No</Button>
        </CardActions>
     </Card>
   }
    </React.Fragment>
  );
}
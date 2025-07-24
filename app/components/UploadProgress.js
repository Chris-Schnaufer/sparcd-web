'use client'

/** @module components/UploadProgress */

import * as React from 'react';
import LinearProgress from '@mui/material/LinearProgress';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import { v4 as uuidv4 } from 'uuid';

import { AddMessageContext, BaseURLContext, SizeContext, TokenContext } from '../serverInfo';

const MAX_UPLOADS = 2;

/**
 * Handles upload of files
 * @function
 * @param {object} progressId Unique identifier for this progress instance
 * @param {object} files Array of files to upload
 * @param {number} startOffset The starting position of the upload
 * @param {string} uploadId The permission ID of the upload
 * @param {object} workingInfo Previously specified progress information, or null
 * @param {function} onWorkingInfo Called to set the ID of the current upload
 * @param {function} onUploaded Called when a chunk of the upload has completed
 * @param {function} onRetry Called when the upload could be retried
 * @param {boolean} haveError Set to true if an error had been detected
 * @return {object} The UI to render for this upload
 */
export default function UploadProgress({progressId, files, startOffset, uploadId, workingInfo, onWorkingInfo, onUploaded, onRetry, onError, haveError}) {
  const theme = useTheme();
  const serverURL = React.useContext(BaseURLContext);
  const uiSizes = React.useContext(SizeContext);
  const uploadToken = React.useContext(TokenContext);

  React.useLayoutEffect(() => {
    // Don't do anything if we still have an upload in progress
    if ((workingInfo === null || workingInfo === undefined) && files && files.length > startOffset) {
      const uploadProgressId = uuidv4();
      const NUM_FILES_UPLOAD = 1;   // HACK

      const sandboxFileUrl = serverURL + '/sandboxFile?t=' + encodeURIComponent(uploadToken);
      const formData = new FormData();

      formData.append('id', uploadId);
      for (let idx = 0; idx < NUM_FILES_UPLOAD && idx < files.length; idx++) {
        formData.append(files[idx].name, files[idx]);
      }

      onWorkingInfo(progressId, uploadProgressId);

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
              onUploaded(progressId, Math.min(NUM_FILES_UPLOAD, files.length));
          })
          .catch(function(err) {
              onRetry(progressId);
        });
      } catch (error) {
        console.log('Upload Images Unknown Error: ',err);
        // TODO: Only show this message once
        onError(progressId, 'An unkown problem ocurred while uploading images');
      }
    }
  }, [files. startOffset, uploadId, workingInfo, onWorkingInfo, onUploaded, onRetry, onError]);

  const percentComplete = !files ? 0 : files.length ? Math.round(((startOffset * 1.0) / files.length) * 100) : 100;
  const extraParams = !haveError ? {} : {color: 'red'};
  console.log('UPLOAD',progressId, percentComplete);
  return (
    <React.Fragment>
      <LinearProgress variant="determinate" value={percentComplete} {...extraParams} sx={{minWidth:'120px', minHeight:'20px'}}/>
    </React.Fragment>
  );
}

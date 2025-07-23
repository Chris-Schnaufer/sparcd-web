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
 * @param {object} files Array of files to upload
 * @param {number} startOffset The starting position of the upload
 * @param {string} uploadId The permission ID of the upload
 * @param {object} prevProgressInfo Previously specified progress information, or null
 * @param {function} onProgressInfo Called to set the ID of the current upload
 * @param {function} onUploaded Called when a chunk of the upload has completed
 * @param {function} onRetry Called when the upload could be retried
 * @return {object} The UI to render for this upload
 */
export default function UploadProgress({files, startOffset, uploadId, prevProgressInfo, onProgressInfo, onUploaded, onRetry, onError}) {
  const theme = useTheme();
  const serverURL = React.useContext(BaseURLContext);
  const uiSizes = React.useContext(SizeContext);
  const uploadToken = React.useContext(TokenContext);

  React.useLayoutEffect(() => {
    // Don't do anything if we still have an upload in progress
    if (prevProgressInfo === null || prevProgressInfo === undefined) {
      const progressId = uuidv4();
      const NUM_FILES_UPLOAD = 1;   // HACK

      const sandboxFileUrl = serverURL + '/sandboxFile?t=' + encodeURIComponent(uploadToken);
      const formData = new FormData();

      formData.append('id', uploadId);
      for (let idx = 0; idx < NUM_FILES_UPLOAD && idx < files.length; idx++) {
        formData.append(files[idx].name, files[idx]);
      }

      onProgressInfo(progressId);

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
  }, [files. startOffset, uploadId, prevProgressInfo, onProgressInfo, onUploaded, onRetry, onError]);

  const percentComplete = !files ? 0 : files.length ? Math.round(((startOffset * 1.0) / files.length) * 100) : 100;
  return (
    <React.Fragment>
      <LinearProgress variant="determinate" value={percentComplete} />
    </React.Fragment>
  );
}

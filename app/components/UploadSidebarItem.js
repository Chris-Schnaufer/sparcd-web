'use client'

/** @module components/UploadSidebarItem */

import * as React from 'react';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';

/**
 * Renders an single uploaded folder item in the upload sidebar
 * @function
 * @param {object} uploadItem On instance of an uploaded item
 * @param {boolean} selected Set truthiness to true if this upload is selected
 * @param {function} onClick The parent handler when a new upload is selected
 * @returns {object} The rendered UI
 */
export default function UploadSidebarItem({uploadItem, selected, onClick}) {
  const theme = useTheme();

  // Setup the elements appearance
  let curTheme = {...theme.palette.left_sidebar_item, ...{cursor:'pointer'}};
  if (selected) {
    curTheme = {...curTheme, ...theme.palette.left_sidebar_item_selected}
  }

  // Returns the upload item UI
  return (
    <Grid display='flex' justifyContent='left' size='grow' sx={{...curTheme}} onClick={onClick} >
      {uploadItem.name}
    </Grid>
  );
}
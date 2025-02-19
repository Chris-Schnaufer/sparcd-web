'use client'

import * as React from 'react';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';

export default function UploadSidebarItem({uploadItem, selected}) {
  const theme = useTheme();

  let curTheme = theme.palette.left_sidebar_item;
  if (selected) {
    curTheme = {...curTheme, ...theme.palette.left_sidebar_item_selected}
  }

  return (
    <Grid display='flex' justifyContent='left' size='grow' sx={{...curTheme}} >
      {uploadItem.name}
    </Grid>
  );
}
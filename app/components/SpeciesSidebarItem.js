'use client'

/** @module components/SpeciesSidebarItem */

import * as React from 'react';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

/**
 * Renders a single species item
 * @function
 * @param {object} species Contains the name, speciesIconURL, and keybinding for the species
 * @param {function} onClick_func Function to call when the species UI is clicked
 * @returns The rendered UI item
 */
export default function SpeciesSidebarItem({species, onClick_func}) {
  const theme = useTheme();

  // Render the UI
  return (
    <Grid id={'card-' + species.name} display='flex' justifyContent='left' size='grow' spacing='1' onClick={onClick_func} sx={{'maxWidth':'150px'}}>
      <Card sx={{ ...theme.palette.species_sidebar_item }} >
        <CardMedia
          sx={{ ...theme.palette.species_sidebar_item_media }}
          image={species.speciesIconURL}
          title={species.name}
        />
        <CardActions>
          <Typography variant='body3' nowrap='true' sx={{ flex:'1',color:'text.primary' }}>
            {species.name}
          </Typography>
          <Button sx={{flex:'1'}} size="small">{species.keyBinding == null ? "Keybind" : "<" + species.keyBinding + ">"}</Button>
        </CardActions>
      </Card>
    </Grid>
  );
}

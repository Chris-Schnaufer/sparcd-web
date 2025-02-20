'use client'

import * as React from 'react';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

export default function SpeciesSidebarItem({species, onClick_func}) {
  const theme = useTheme();

  return (
    <Grid display='flex' justifyContent='left' size='grow' spacing='1' onClick={onClick_func} >
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

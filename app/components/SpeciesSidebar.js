
import * as React from 'react';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';

import SpeciesSidebarItem from './SpeciesSidebarItem'

/**
 * Returns the UI for the species sidebar
 * @function
 * @param {array} species The array of species to display
 * @param {string} position One of "left" or "top"
 * @param {object} speciesSidebarRef React reference for the sidebar
 * @param {string} workingDim The working height ("left") or width ("top") of the control
 * @param {int} topX The top X pixel position
 * @param {function} onKeybind Handler for changing keybinding
 * @param {function} onZoom Handler for zooming in on species image
 * @returns {object} The rendered UI
 */
export default function SpeciesSidebar({species, position, speciesSidebarRef, workingDim, topX, onKeybind, onZoom}) {
  const theme = useTheme();
  let sidebarPositionalAttributes = {direction:'row'};
  let sidebarStyleAttributes = Object.assign({},
                                {'minHeight':workingDim, 'maxHeight':workingDim, 'height':workingDim},
                                theme.palette.species_left_sidebar);
  let speciesSidebarItemAttributes = {};

  if (position === 'top') {
    sidebarPositionalAttributes = {direction:'column'};
    sidebarStyleAttributes = Object.assign({}, 
                                {'minWidth':workingDim, 'maxWidth':workingDim, 'width':workingDim},
                                theme.palette.species_top_sidebar);
    speciesSidebarItemAttributes = {size:"small"};
  }

  return (
    <Grid id='species-sidebar' ref={speciesSidebarRef} container alignItems='stretch' columns='1' {...sidebarPositionalAttributes}
        style={{ ...sidebarStyleAttributes, 'position':'absolute', 'overflow':'scroll', 'top':topX+'px' }} >
      { species.map((item) => <SpeciesSidebarItem id={'card-' + item.name}  species={item} key={item.name} {...speciesSidebarItemAttributes}
                                                  keybindClick_func={(event) => onKeybind(event, item)}
                                                  zoomClick_func={(event) => onZoom(event, item)}
                              />)
      }
    </Grid>
  );
}

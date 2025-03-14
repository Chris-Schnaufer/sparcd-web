'use client'

/** @module components/LandingCard */

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import Grid from '@mui/material/Grid2';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';

/**
 * Returns the common card UI for actions on the Landing page
 * @function
 * @param {string} title The title of the card
 * @param {array} action Array of objects with onClick handler, disabled flag, and title (aka. name) for a card
 * @param {object} [children] The children elements of the card
 * @returns {object} The rendered Landing card
 */
export default function LoginCard({title, action, children}) {
  const [isNarrow, setIsNarrow] = React.useState(false);
  const theme = useTheme();
  const narrowWindow = isNarrow;

  // Sets the narrow flag when the window is less than 600 pixels
  React.useEffect(() => setIsNarrow(window.inner_width <= 600), []);

  // Adds a resize handler to the window, and automatically removes it
  React.useEffect(() => {
      function onResize () {
          setIsNarrow(window.inner_width <= 600);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  // Handle actions as array or an object
  let curAction = action;
  if (curAction instanceof Array) {
    curAction = curAction.filter((act) => act != null);
    if (curAction.length == 1) {
      curAction = curAction[0];
    }
  }
  const actionsIsArray = curAction instanceof Array;

  // Render the card UI
  return (
    <Card variant="outlined" sx={{backgroundColor: `${theme.palette.landing_card.background}`, 
                                  maxWidth: narrowWindow ? `${theme.palette.landing_card.maxWidth}` : '100vw',
                                  minHeight: `${theme.palette.landing_card.minHeight}` }} >
      <CardContent sx={{minHeight: `${theme.palette.landing_card.minHeight}`}}>
        <Typography gutterBottom sx={{ color: 'text.primary', fontSize: 14, textAlign: 'center' }} >
          {title}
        </Typography>
        {children}
      </CardContent>
      <CardActions>
        { actionsIsArray ? 
          curAction.map(function(obj, idx) {
            return <Button size="small" onClick={obj.onClick} key={obj.title} sx={{'flex':'1'}} disabled={obj.disabled}>{obj.title}</Button>;
          })
          : <Button size="small" onClick={curAction.onClick} disabled={curAction.disabled}>{curAction.title}</Button>
        }
      </CardActions>
    </Card>
  );
}

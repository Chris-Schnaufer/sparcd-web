'use client'

import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import Grid from '@mui/material/Grid';
import Typography from '@mui/material/Typography';

export default function SpeciesKeybind({keybind, name, parentId, onClose_func, onChange_func}) {
  const [parentX, setParentX] = React.useState(0);
  const [curKeybind, setCurKeybind] = React.useState(keybind);

  React.useLayoutEffect(() => {
      function onResize () {
        const el = document.getElementById(parentId);
        if (el) {
          setParentX(el.getBoundingClientRect().x);
        }
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  React.useEffect(() => {
    function onKeypress(event) {
      if (event.key !== 'Meta') {
        setCurKeybind(event.key.toUpperCase());
        event.preventDefault();
      }
    }
    document.addEventListener("keydown", onKeypress);

    return () => {
      document.removeEventListener("keydown", onKeypress);
    }
  }, []);

  if (parentX === 0) {
    const el = document.getElementById(parentId);
    if (el) {
      setParentX(el.getBoundingClientRect().x);
    }
  }
  return (
    <Card>
      <CardContent>
        <Typography gutterBottom sx={{ color: 'text.primary', fontSize: 14, textAlign: 'center' }} >
          Setting new keybinding for &nbsp;
          <span style={{ fontSize: 16, fontWeight:'bold'}} >
            {name}
          </span>
        </Typography>
        <Typography gutterBottom sx={{ color: 'text.primary', fontSize: 14, textAlign: 'center', fontWeight:'bold' }} >
          Press a key
        </Typography>
        <Typography gutterBottom variant='h5' sx={{ color: 'text.primary', textAlign: 'center' }} >
          {curKeybind ? (curKeybind === ' ' ? 'SPACE' : curKeybind) : '<none>'}
        </Typography>
      </CardContent>
      <CardActions>
        <Button sx={{flex:'1'}} onClick={() => {setCurKeybind(null);onChange_func(null);}}>Clear</Button>
        <Button sx={{flex:'1'}} onClick={() => {onChange_func(curKeybind);onClose_func();}}>Done</Button>
    </CardActions>
    </Card>
  );
}
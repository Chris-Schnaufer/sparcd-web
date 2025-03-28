/** @module components/FilterElevation */

import * as React from 'react';
import Box from '@mui/material/Box';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import Grid from '@mui/material/Grid';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import InputAdornment from '@mui/material/InputAdornment';
import MenuItem from '@mui/material/MenuItem';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

export default function FilterElevations({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedElevation, setSelectedElevation] = React.useState(data ? data : {type:"=", value:0.0, units:"meters"}); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  const elevationChoices = [
    {name:"Equal To", type:"="},
    {name:"Greater Than", type:">"},
    {name:"Greater Than or Equal To", type:">="},
    {name:"Less Than", type:"<"},
    {name:"Less Than or Equal To",type:"<="}
  ];

  const elevationUnits = [
    "meters",
    "feet"
  ];

  function handleChangeComparison(event) {
    const curElevation = selectedElevation;
    curElevation.type = event.target.value;
    setSelectedElevation(curElevation);
    onChange(curElevation);
  }

  function handleElevationChange(event) {
    const curElevation = selectedElevation;
    curElevation.value = parseFloat(event.target.value);//event.target.value;
    if (event.target.value[event.target.value.length-1] ==='.') {
      const numDots = event.target.value.match(/\./g) || [];
      if (numDots.length == 1) {
        curElevation.value += '.';
      }
    }
    setSelectedElevation(curElevation);
    onChange(curElevation);
    setSelectionRedraw(curElevation.value);
  }

  function handleChangeUnits(event) {
    const curElevation = selectedElevation;
    curElevation.units = event.target.value;
    setSelectedElevation(curElevation);
    onChange(curElevation);
  }

  return (
    <Card id="filter-elevation" sx={{backgroundColor:'seashell', border:"none", boxShadow:"none"}}>
      <CardHeader title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid item>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Elevation Filter
                        </Typography>
                      </Grid>
                      <Grid item sx={{marginLeft:'auto'}} >
                        <div onClick={onClose}>
                          <Tooltip title="Delete this filter">
                            <Typography gutterBottom variant="body2" noWrap="true"
                                        sx={{textTransform:'uppercase',
                                        color:'grey',
                                        cursor:'pointer',
                                        fontWeight:'500',
                                        backgroundColor:'rgba(0,0,0,0.03)',
                                        padding:'3px 3px 3px 3px',
                                        borderRadius:'3px',
                                        '&:hover':{backgroundColor:'rgba(255,255,255,0.7)', color:'black'}
                                     }}
                            >
                                X
                            </Typography>
                          </Tooltip>
                        </div>
                      </Grid>
                    </Grid>
                    }
                style={{paddingTop:'0px', paddingBottom:'0px'}}
      />
      <CardContent sx={{paddingTop:'0px', paddingBottom:'0px'}}>
          <Grid item sx={{minHeight:'230px', maxHeight:'230px', height:'230px', minWidth:'250px', overflow:'scroll',
                          paddingLeft:'5px', backgroundColor:'rgb(255,255,255,0.3)'
                        }}>
            <Stack spacing={1}>
              <Typography gutterBottom variant="body2" noWrap="true">
                Return all elevations which are
              </Typography>
              <TextField id="elevation-compare-types" select defaultValue={selectedElevation.type}
                        onChange={(event) => handleChangeComparison(event)}
              >
              { elevationChoices.map((item) => 
                    <MenuItem key={'elevation-choice-' + item.type} value={item.type}>
                      {item.name}
                    </MenuItem>
                )
              }
              </TextField>
              <Grid container direction="row" alignItems="start" justifyItems="start">
                <Grid item>
                  <TextField id="elevation-value" value={selectedElevation.value} label="Elevation" variant="standard" 
                             onChange={handleElevationChange}
                             slotProps={{htmlInput: {style: {maxWidth:"130px"}} }}
                  />
                </Grid>
                <Grid item sx={{marginLeft:'auto'}}>
                  <TextField id="elevation-value-units" select label="Units" defaultValue={selectedElevation.units}
                             onChange={handleChangeUnits}
                  >
                  { elevationUnits.map((item) => 
                        <MenuItem key={'elevation-choice-' + item} value={item}>
                          {item}
                        </MenuItem>
                    )
                  }
                  </TextField>
                </Grid>
              </Grid>
            </Stack>
          </Grid>
      </CardContent>
    </Card>
  );
}

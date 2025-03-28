/** @module components/FilterYear */

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

export default function FilterYear({data, onClose, onChange}) {
  const theme = useTheme();
  const curYear = new Date().getFullYear();
  const [selectedYearEnd, setSelectedYearEnd] = React.useState(data ? data.start : curYear); // The user's end year
  const [selectedYearStart, setSelectedYearStart] = React.useState(data ? data.end : curYear); // The user's start year
  const [yearEndError, setYearEndError] = React.useState(false); // The user's end year is in error
  const [yearStartError, setYearStartError] = React.useState(false); // The user's start year is in error

  function handleYearStartChange(event) {
    const newYear = parseInt(event.target.value);
    setSelectedYearStart(newYear);
    if (newYear <= selectedYearEnd || newYear.length > 4) {
      setYearStartError(false);
      onChange({start:newYear, end:selectedYearEnd});
    } else {
      setYearStartError(true);
    }
  }

  function handleYearEndChange(event) {
    const newYear = parseInt(event.target.value);
    setSelectedYearEnd(newYear);
    if (newYear >= selectedYearStart || newYear.length > 4) {
      setYearEndError(false);
      onChange({start:selectedYearStart, end:newYear});
    } else {
      setYearEndError(true);
    }
  }

  return (
    <Card id="filter-year" sx={{backgroundColor:'seashell', border:"none", boxShadow:"none"}}>
      <CardHeader title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid item>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Year Filter
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
          <Grid item sx={{minHeight:'230px', maxHeight:'230px', height:'230px', minWidth:'250px', maxWidth:'250px',
                          overflowX:'clip', overflowY:'scroll', paddingLeft:'5px', backgroundColor:'rgb(255,255,255,0.3)'
                        }}>
            <Stack spacing={1}>
              <TextField id="start-year-value" error={yearStartError ? true : false} value={selectedYearStart} type="numeric" label="Start Year" variant="standard" 
                         onChange={handleYearStartChange}
              />
              <Typography gutterBottom variant="body2" noWrap sx={{textAlign:'center'}}>
                Up to, and including
              </Typography>
              <TextField id="end-year-value" error={yearEndError ? true : false} value={selectedYearEnd} type="numeric" label="End Year" variant="standard" 
                         onChange={handleYearEndChange}
              />
              <Typography gutterBottom variant='body2' color='error' sx={{textAlign:'start'}}>
                { yearStartError || yearEndError ? 'End year must be equal or greater than start year' : ''}
              </Typography>
            </Stack>
          </Grid>
      </CardContent>
    </Card>
  );
}

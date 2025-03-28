/** @module components/FilterDayOfWeek */

import * as React from 'react';
import BackspaceOutlinedIcon from '@mui/icons-material/BackspaceOutlined';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Checkbox from '@mui/material/Checkbox';
import Grid from '@mui/material/Grid';
import FormGroup from '@mui/material/FormGroup';
import FormControl from '@mui/material/FormControl';
import FormControlLabel from '@mui/material/FormControlLabel';
import IconButton from '@mui/material/IconButton';
import InputAdornment from '@mui/material/InputAdornment';
import TextField from '@mui/material/TextField';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

export default function FilterDayOfWeek({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedDays, setSelectedDays] = React.useState(data ? data : []); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  const dayNames = [
    'MONDAY',
    'TUESDAY',
    'WEDNESDAY',
    'THURSDAY',
    'FRIDAY',
    'SATURDAY',
    'SUNDAY'
  ];

  function handleSelectAll() {
    setSelectedDays(dayNames);
    onChange(dayNames);
  }

  function handleSelectNone() {
    setSelectedDays([]);
    onChange([]);
  }

  function handleCheckboxChange(event, dayName) {

    if (event.target.checked) {
      const dayIdx = selectedDays.findIndex((item) => dayName === item);
      // Add the day in if we don't have it already
      if (dayIdx < 0) {
        const curDay = selectedDays;
        curDay.push(dayName);
        setSelectedDays(curDay);
        onChange(curDay);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the day if we have it
      const curDay = selectedDays.filter((item) => item !== dayName);
      if (curDay.length < selectedDays.length) {
        setSelectedDays(curDay);
        onChange(curDay);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  return (
    <Card id="filter-day" sx={{backgroundColor:'seashell', border:"none", boxShadow:"none"}}>
      <CardHeader title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid item>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          Day of Week Filter
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
          <Grid item sx={{minHeight:'210px', maxHeight:'210px', height:'210px', minWidth:'250px', overflow:'scroll',
                          border:'1px solid black', borderRadius:'5px', paddingLeft:'5px',
                          backgroundColor:'rgb(255,255,255,0.3)'
                        }}>
            <FormGroup>
              { dayNames.map((item) => 
                  <FormControlLabel key={'filter-day-' + item}
                                    control={<Checkbox size="small" 
                                                       checked={selectedDays.findIndex((curDay) => curDay===item) > -1 ? true : false}
                                                       onChange={(event) => handleCheckboxChange(event,item)}
                                              />} 
                                    label={<Typography variant="body2">{item}</Typography>} />
                )
              }
            </FormGroup>
          </Grid>
      </CardContent>
      <CardActions>
              <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
              <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
      </CardActions>
    </Card>
  );
}

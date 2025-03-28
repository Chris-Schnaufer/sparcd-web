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

import FilterCard from './FilterCard'

const dayNames = [
  'MONDAY',
  'TUESDAY',
  'WEDNESDAY',
  'THURSDAY',
  'FRIDAY',
  'SATURDAY',
  'SUNDAY'
];

export default function FilterDayOfWeek({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedDays, setSelectedDays] = React.useState(data ? data : dayNames); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  React.useEffect(() => {
    if (!data) {
      onChange(selectedDays);
    }
  }, [selectedDays]);

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
    <FilterCard title="Day of Week Filter" onClose={onClose} 
                actions={
                  <React.Fragment>
                    <Button sx={{'flex':'1'}} size="small" onClick={handleSelectAll}>Select All</Button>
                    <Button sx={{'flex':'1'}} size="small" onClick={handleSelectNone}>Select None</Button>
                  </React.Fragment>
                }
    >
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
    </FilterCard>
  );
}

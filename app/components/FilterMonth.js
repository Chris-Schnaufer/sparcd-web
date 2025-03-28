/** @module components/FilterMonth */

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

const monthNames = [
  'JANUARY',
  'FEBRUARY',
  'MARCH',
  'APRIL',
  'MAY',
  'JUNE',
  'JULY',
  'AUGUST',
  'SEPTEMBER',
  'OCTOBER',
  'NOVEMBER',
  'DECEMBER'
];

export default function FilterMonth({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedMonths, setSelectedMonths] = React.useState(data ? data : monthNames); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  React.useEffect(() => {
    if (!data) {
      onChange(selectedMonths);
    }
  }, [selectedMonths]);

  function handleSelectAll() {
    setSelectedMonths(monthNames);
    onChange(monthNames);
  }

  function handleSelectNone() {
    setSelectedMonths([]);
    onChange([]);
  }

  function handleCheckboxChange(event, monthName) {

    if (event.target.checked) {
      const monthIdx = selectedMonths.findIndex((item) => monthName === item);
      // Add the month in if we don't have it already
      if (monthIdx < 0) {
        const curMonths = selectedMonths;
        curMonths.push(monthName);
        setSelectedMonths(curMonths);
        onChange(curMonths);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the month if we have it
      const curMonths = selectedMonths.filter((item) => item !== monthName);
      if (curMonths.length < selectedMonths.length) {
        setSelectedMonths(curMonths);
        onChange(curMonths);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  return (
    <FilterCard title="Month Filter" onClose={onClose} 
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
          { monthNames.map((item) => 
              <FormControlLabel key={'filter-months-' + item}
                                control={<Checkbox size="small" 
                                                   checked={selectedMonths.findIndex((curMonth) => curMonth===item) > -1 ? true : false}
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

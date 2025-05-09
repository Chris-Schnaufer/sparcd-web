/** @module components/FilterHour */

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

// The names of the hours to use
const hoursNames = [
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '10',
  '11',
  '12',
  '13',
  '14',
  '15',
  '16',
  '17',
  '18',
  '19',
  '20',
  '21',
  '22',
  '23',
  '24',
];

/**
 * Adds hour information to form data
 * @function
 * @param {object} data The saved data to add to the form
 * @param {object} formData The FormData to add the fields to
 */
export function FilterHourFormData(data, formData) {
  formData.append('hour', JSON.stringify(data.map((item) => parseInt(item))));
}

/**
 * Returns the UI for filtering by hours
 * @param {object} {data} Saved hour data
 * @param {function} onClose The handler for closing this filter
 * @param {function} onChange The handler for when the filter data changes
 * @returns {object} The UI specific for filtering by hour
 */
export default function FilterHour({data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedHours, setSelectedHours] = React.useState(data ? data : hoursNames); // The user's selections
  const [selectionRedraw, setSelectionRedraw] = React.useState(0); // Used to redraw the UI

  // Set the default data if we don't have any yet
  React.useEffect(() => {
    if (!data) {
      onChange(selectedHours);
    }
  }, [selectedHours]);

  /**
   * Handles selecting all the filter choices
   * @function
   */
  function handleSelectAll() {
    setSelectedHours(hoursNames);
    onChange(hoursNames);
  }

  /**
   * Handles clearing all of the filter choices
   * @function
   */
  function handleSelectNone() {
    setSelectedHours([]);
    onChange([]);
  }


  /**
   * Handles the user selecting or deselecting an hour
   * @function
   * @param {object} event The triggering event data
   * @param {string} hourName The name of the hour to add or remove from the filter
   */
  function handleCheckboxChange(event, hourName) {

    if (event.target.checked) {
      const hourIdx = selectedHours.findIndex((item) => hourName === item);
      // Add the hour in if we don't have it already
      if (hourIdx < 0) {
        const curHours = selectedHours;
        curHours.push(hourName);
        setSelectedHours(curHours);
        onChange(curHours);
        setSelectionRedraw(selectionRedraw + 1);
      }
    } else {
      // Remove the hour if we have it
      const curHours = selectedHours.filter((item) => item !== hourName);
      if (curHours.length < selectedHours.length) {
        setSelectedHours(curHours);
        onChange(curHours);
        setSelectionRedraw(selectionRedraw + 1);
      }
    }
  }

  // Return the UI for filtering by the hour
  return (
    <FilterCard title="Hour Filter" onClose={onClose}
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
          { hoursNames.map((item) => 
              <FormControlLabel key={'filter-hours-' + item}
                                control={<Checkbox size="small" 
                                                   checked={selectedHours.findIndex((curHour) => curHour===item) > -1 ? true : false}
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

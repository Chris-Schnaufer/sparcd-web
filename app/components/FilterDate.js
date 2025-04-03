/** @module components/FilterStartDate */

import * as React from 'react';
import dayjs from 'dayjs';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import Grid from '@mui/material/Grid';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import Tooltip from '@mui/material/Tooltip';
import Typography from '@mui/material/Typography';
import { useTheme } from '@mui/material/styles';

import FilterCard from './FilterCard'

export function FilterDateFormData(fieldName, data, formData) {
  formData.append(fieldName, data.$d);
}

export default function FilterStartDate({title, data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedDateTime, setSelectedDateTime] = React.useState(data ? data.end : dayjs()); // The user's start year

  React.useEffect(() => {
    if (!data) {
      onChange(selectedDateTime);
    }
  }, [selectedDateTime]);

  function handleDateTimeChange(event) {
    setSelectedDateTime(event);
    onChange(event);
  }

  return (
    <FilterCard title={title} onClose={onClose} >
      <Grid item sx={{minHeight:'230px', maxHeight:'230px', height:'230px', minWidth:'250px', maxWidth:'250px',
                      overflowX:'clip', overflowY:'scroll', paddingLeft:'5px', backgroundColor:'rgb(255,255,255,0.3)'
                    }}>
        <LocalizationProvider dateAdapter={AdapterDayjs}>
          <DateTimePicker ampm={false} value={selectedDateTime} timeSteps={{minutes: 1}} onChange={handleDateTimeChange} />
        </LocalizationProvider>
      </Grid>
    </FilterCard>
  );
}

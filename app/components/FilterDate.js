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

export default function FilterStartDate({title, data, onClose, onChange}) {
  const theme = useTheme();
  const [selectedDateTime, setSelectedDateTime] = React.useState(data ? data.end : dayjs()); // The user's start year

  function handleDateTimeChange(event) {
    setSelectedDateTime(event);
  }

  return (
    <Card id="filter-start-date" sx={{backgroundColor:'seashell', border:"none", boxShadow:"none"}}>
      <CardHeader title={
                    <Grid container direction="row" alignItems="start" justifyContent="start" wrap="nowrap">
                      <Grid item>
                        <Typography gutterBottom variant="h6" component="h4" noWrap="true">
                          {title}
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
            <LocalizationProvider dateAdapter={AdapterDayjs}>
              <DateTimePicker ampm={false} value={selectedDateTime} timeSteps={{minutes: 1}} onChange={handleDateTimeChange} />
            </LocalizationProvider>
          </Grid>
      </CardContent>
    </Card>
  );
}

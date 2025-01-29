import { createTheme } from '@mui/material/styles';
import { grey } from '@mui/material/colors';

const theme = createTheme({
  typography: {
    button: {
      textTransform: 'none'
    }
  },
  palette: {
    background: {
      default: grey[500],
      paper: grey[500],
    },
    login_button: {
      main: '#EFEFEF',
      light: '#FFFFFF',
      dark: '#E0E0E0',
      contrastText: '#000000'
    }
  }
});

export default theme;

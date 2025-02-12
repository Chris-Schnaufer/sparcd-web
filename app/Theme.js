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
    },
    landing_card: {
      background: 'lightgrey',
      minHeight: '20vh',
      maxWidth: '40vw',
      uploadImage: "https://arizona.box.com/shared/static/dcxcm0y8u6cnwcz6tftovo68ixkcd2c0.jpg",
      collectionsImage: '../public/CollectionsImage.jpg',
      searchImage: '../public/SearchImage.jpg',
      mapsImage: '../public/MapsImage.jpg',
    }
  }
});

export default theme;

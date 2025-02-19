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
    },
    landing_upload: {
      border: '1px solid black',
      maxHeight: '24vh',
      overflow: 'scroll',
      padding: '0em 1em 0em 1em'
    },
    landing_upload_refresh: {
      color: 'text.secondary',
      fontSize: 'x-small', 
      textAlign: 'center'
    },
    landing_collections: {
      border: '1px solid black',
      maxHeight: '24vh',
      overflow: 'scroll',
      padding: '0em 1em 0em 1em'
    },
    landing_collections_refresh: {
      color: 'text.secondary',
      fontSize: 'x-small', 
      textAlign: 'center'
    },
    folder_upload: {
      background: 'white',
      padding: '1em 2em 1em 2em'
    },
    left_sidebar: {
      height: '100%',
      width: '15vw',
      maxWidth: '15vw',
      minWidth: '150px',
      background: 'white',
      borderRight: '1px solid black',
    },
    left_sidebar_item: {
      margin: '10px 10px 10px 10px'
    },
    left_sidebar_item_selected: {
      background: 'lightpink'
    },
    screen_disable: {
      'position': 'absolute',
      'left': 0,
      'top': 0,
      'width': '100vw',
      'height': '100vh',
      'backgroundColor': 'rgba(128, 128, 128, 0.50)'
    }
  }
});

export default theme;

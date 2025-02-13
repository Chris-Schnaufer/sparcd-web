
import * as React from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardActions from '@mui/material/CardActions';
import CardContent from '@mui/material/CardContent';
import CardHeader from '@mui/material/CardHeader';
import CircularProgress from '@mui/material/CircularProgress';
import Grid from '@mui/material/Grid';
import { useTheme } from '@mui/material/styles';
import Typography from '@mui/material/Typography';
import { BaseURLContext, TokenContext } from '../serverInfo'

export default function FolderUpload({cancel_func}) {
  const theme = useTheme();
  const [uploadingFiles, setUploadingFiles] = React.useState(false);
  const [filesSelected, setFilesSelected] = React.useState(0);
  const [inputSize, setInputSize] = React.useState({'width':252,'height':21});
  const uploadToken = React.useContext(TokenContext);
  const uploadUrl = React.useContext(BaseURLContext) + '/upload&' + uploadToken + '&check';

function CircularProgressWithLabel(props) {
  return (
    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress variant="determinate" {...props} />
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography
          variant="caption"
          component="div"
          sx={{ color: 'text.secondary' }}
        >
          {`${Math.round(props.value)}%`}
        </Typography>
      </Box>
    </Box>
  );
}

  function havePreviousUpload(path, files) {
    const formData = new FormData();
    // TODO: Add in a bunch of files and check - loop through all files to see what's not been uploaded
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const resp = await fetch(sandboxUrl, {
      'method': 'POST'
    });
    console.log(resp);
    */

    // Return null (no upload), or a list of files not uploaded
    return null;
  }

  function uploadFolder() {
    const formData = new FormData();
    // TODO: Add in a bunch of files and upload - loop through all files
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and sandbox items
    const fd = new FormData();

    // add all selected files
    e.target.files.forEach((file) => {
      fd.append(e.target.name, file, file.name);  
    });
    
    // create the request
    const xhr = new XMLHttpRequest();
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
          // we done!
      }
    };
    
    // path to server would be where you'd normally post the form to
    xhr.open('POST', '/path/to/server', true);
    xhr.send(fd);
    */
    setUploadingFiles(true);
  }

  function uploadFiles(ev) {
    const el = document.getElementById('folder_select');

    // Return if there's nothing to do
    if (!el.files || !el.files.length) {
      // TODO: Add message about choosing a non-empty folder
      return;
    }

    const allFiles = el.files;
    let relativePath = allFiles[0].webkitRelativePath;
    if (!relativePath) {
      // TODO: have a problem (remove console.log)
      console.log('ERROR: Missing relative path');
      return;
    }
    relativePath = relativePath.substr(0, relativePath.length - allFiles[0].name.length - 1);

    const resp = havePreviousUpload(relativePath, allFiles);
    if (resp) {
      // Handle the response
    }

    uploadFolder(relativePath, allFiles);
  }

  function selectionChanged(ev) {
    const el = ev.target;

    if (el.files && el.files.length != null) {
      setFilesSelected(el.files.length);
    } else {
      setFilesSelected(0);
    }
  }

  function cancelUpload(ev) {
    cancel_func();
  }

  function renderInputControls() {
    const el = document.getElementById('folder_select');
    let curWidth = inputSize.width;
    let curHeight = inputSize.height;
    if (el) {
      const parentEl = el.parentNode;
      const elSize = el.getBoundingClientRect();
      console.log(elSize);
      if (inputSize.width != elSize.width || inputSize.height != elSize.height) {
        setInputSize({'width':elSize.width,'height':elSize.height});
        curWidth = elSize.width;
        curHeight = elSize.height;
      }
    }
    console.log(inputSize.width, inputSize.height);
    if (uploadingFiles) {
      // TODO: adjust upload percent to include already uploaded images
      return (
        <Grid id="grid" container justifyContent="center" sx={{'minWidth': `${curWidth}px`, 'minHeight':`${curHeight}px`}}>
          <CircularProgressWithLabel value='10'/>
        </Grid>
      );
    } else {
      return (
        <input id="folder_select" type="file" name="file" webkitdirectory="true" directory="true" onChange={selectionChanged}></input>
      );
    }
  }

  return (
    <Card variant="outlined" sx={{'backgroundColor': `${theme.palette.folder_upload.background}`, 'padding': `${theme.palette.folder_upload.padding}`}} >
      <React.Fragment>
        <CardHeader sx={{ textAlign: 'center' }} title={
            <Typography gutterBottom variant="h6" component="h4">
              Upload Folder
            </Typography>
           }
           subheader="Select folder to upload"
         />
        <CardContent>
          {renderInputControls()}
        </CardContent>
        <CardActions>
          <Button id="folder_upload" sx={{'flex':'1'}} size="small" onClick={uploadFiles} disabled={filesSelected > 0 ? false : true}>Upload</Button>
          <Button id="folder_cancel" sx={{'flex':'1'}} size="small" onClick={cancelUpload}>Cancel</Button>
        </CardActions>
      </React.Fragment>
    </Card>
  );
}
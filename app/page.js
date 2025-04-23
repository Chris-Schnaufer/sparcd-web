'use client'

import * as React from 'react';
import Grid from '@mui/material/Grid';
import styles from './page.module.css';
import { ThemeProvider } from "@mui/material/styles";
import Typography from '@mui/material/Typography';

import CircularProgress from '@mui/material/CircularProgress';
import CollectionsManage from './CollectionsManage';
import FooterBar from './components/FooterBar';
import Landing from './Landing';
import Login from './Login';
import Maps from './Maps';
import Queries from './Queries';
import theme from './Theme';
import TitleBar from './components/TitleBar';
import UploadManage from './UploadManage';
import UploadEdit from './UploadEdit';
import UserActions from './components/userActions';
import { LoginCheck, LoginValidContext, DefaultLoginValid } from './checkLogin';
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, NarrowWindowContext, 
         SandboxInfoContext, TokenContext, UploadEditContext } from './serverInfo';
import * as utils from './utils';

// This is declared here so that it doesn't raise an error on server-side compile
const loginStore = {

  loadURL() {
    if (typeof window !== "undefined") {
      return window.localStorage.getItem('login.url')
    }
  },

  loadUsername() {
    if (typeof window !== "undefined") {
      return window.localStorage.getItem('login.user');
    }
  },

  loadRemember() {
    if (typeof window !== "undefined") {
      return window.localStorage.getItem('login.remember');
    }
  },

  saveURL(url) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem('login.url', "" + url);
    }
  },

  saveUsername(username) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem('login.user', "" + username);
    }
  },

  saveRemember(remember) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem('login.remember', !!remember);
    }
  },

  loadLoginInfo() {
    if (!this.loadURL()) {
      this.clearLoginInfo();
    }

    return {
      'url': this.loadURL(),
      'user': this.loadUsername(),
      'remember': this.loadRemember()
    };
  },

  saveLoginInfo(url, username, remember) {
    this.saveURL(url);
    this.saveUsername(username);
    this.saveRemember(remember);
  },

  clearLoginInfo() {
    this.saveURL('');
    this.saveUsername('');
    this.saveRemember(false);
  },

  loadLoginToken() {
    if (typeof window !== "undefined") {
      let curToken = window.localStorage.getItem('login.token');
      console.log('LAST LOGIN TOKEN',curToken)
      return curToken ? curToken : null;
    }

    return null;
  },

  saveLoginToken(token) {
    if (typeof window !== "undefined") {
      console.log('SAVE LOGIN TOKEN',token)
      window.localStorage.setItem('login.token', "" + token);
    }
  },

  clearLoginToken(token) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem('login.token', '');
    }
  }
};

export default function Home() {
  const [breadcrumbs, setBreadcrumbs] = React.useState([]);
  const [checkedToken, setCheckedToken] = React.useState(false);
  const [collectionInfo, setCollectionInfo] = React.useState(null);
  const [curSearchTitle, setCurSearchTitle] = React.useState(null);
  const [curAction, setCurAction] = React.useState(UserActions.None);
  const [curActionData, setCurActionData] = React.useState(null);
  const [curSearchHandler, setCurSearchHandler] = React.useState(null);
  const [dbUser, setDbUser] = React.useState('');
  const [dbURL, setDbURL] = React.useState('');
  const [editing, setEditing] = React.useState(false);
  const [isNarrow, setIsNarrow] = React.useState(null);
  const [lastToken, setLastToken] = React.useState(null);
  const [loginValid, setLoginValid] = React.useState(DefaultLoginValid);
  const [loggedIn, setLoggedIn] = React.useState(null);
  const [mobileDeviceChecked, setMobileDeviceChecked] = React.useState(false);
  const [mobileDevice, setMobileDevice] = React.useState(null);
  const [dbRemember, setDbRemember] = React.useState(false);
  const [sandboxInfo, setSandboxInfo] = React.useState(null);
  const [savedLoginFetched, setSavedLoginFetched] = React.useState(false);
  const [savedTokenFetched, setSavedTokenFetched] = React.useState(false);
  const [serverURL, setServerURL] = React.useState(utils.getServer());
  const [userSettings, setUserSettings] =  React.useState(null);
  const [windowSize, setWindowSize] = React.useState({width:640, height:480});

  const loginValidStates = loginValid;
  let settingsTimeoutId = null;   // Used to manage of the settings calls to the server
  let settingsRequestId = 0;        // Used to prevent sending multiple requests to server
  let curLoggedIn = loggedIn;

  handleSearch = handleSearch.bind(Home);
  setupSearch = setupSearch.bind(Home);
  restoreBreadcrumb = restoreBreadcrumb.bind(Home);

  // TODO: change dependencies to Theme & use @media to adjust
  // Sets the narrow flag when the window is less than 600 pixels
  React.useEffect(() => setIsNarrow(window.innerWidth <= 640), []);

  // TODO: Global window resize handler?
  // Recalcuate available space in the window
  React.useLayoutEffect(() => {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setWindowSize(newSize);
  }, []);

  // Adds a resize handler to the window, and automatically removes it
  React.useEffect(() => {
      function onResize () {
          const newSize = {'width':window.innerWidth,'height':window.innerHeight};

          // TODO: transition to MaterialUI sizes          
          setIsNarrow(newSize.width <= 640);
          setWindowSize(newSize);
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, []);

  // Load saved token and see if session is still valid
  React.useLayoutEffect(() => {
    if (!savedTokenFetched && !curLoggedIn) {
      const lastLoginToken = loginStore.loadLoginToken();
      setSavedTokenFetched(true);
      setLastToken(lastLoginToken);
      if (lastLoginToken) {
        loginUserToken(lastLoginToken,
          () => {setCheckedToken(true);
                 // Load collections
                 loadCollections();
                },
          () => {
            loginStore.clearLoginToken()
            setLastToken(null);
            setCheckedToken(true);
            const loInfo = loginStore.loadLoginInfo();
            setSavedLoginFetched(true);
            if (loInfo != null) {
              setDbURL(loInfo.url);
              setDbUser(loInfo.user);
              setDbRemember(loInfo.remember === 'true');
            }
        });
      } else {
        setCheckedToken(true);
      }
    }

    // Load saved user information: if we haven't already and we're not logged in
    if (!savedLoginFetched && !curLoggedIn) {
      const loInfo = loginStore.loadLoginInfo();
      setSavedLoginFetched(true);
      if (loInfo != null) {
        setDbURL(loInfo.url);
        setDbUser(loInfo.user);
        setDbRemember(loInfo.remember === 'true');
      }
    }
  }, [checkedToken, savedTokenFetched, savedLoginFetched]);

  function restoreBreadcrumb(breadcrumb) {
    const curCrumbs = breadcrumbs;
    let curRestore = null;
    do {
      curRestore = curCrumbs.pop();
      if (curRestore && curRestore.name !== breadcrumb.name) {
      }
    } while (curRestore && curRestore.name !== breadcrumb.name);
    setCurAction(breadcrumb.action);
    setCurActionData(breadcrumb.actionData);
    setEditing(breadcrumb.editing);
    setBreadcrumbs(curCrumbs);
  }

  function setCurrentAction(action, actionData, areEditing, breadcrumbName) {
    if (Object.values(UserActions).indexOf(action) > -1) {
      if (!actionData) {
        actionData = null;
      }
      // TODO: save state and data (and auto-restore)
      const prevAction = curAction;
      const prevActionData = curActionData;
      const prevEditing = editing;
      let curCrumbs = breadcrumbs;
      let newBreadcrumb = {name:breadcrumbName, action:prevAction, actionData:prevActionData, editing:prevEditing};
      curCrumbs.push(newBreadcrumb);
      setBreadcrumbs(curCrumbs);
      setCurAction(action);
      setCurActionData(actionData);
      setEditing(!!areEditing);
    } else {
      // TODO: Put up informational message about not valid command
      console.log('Invalid current action specified', action);
    }
  }

  /**
   * Fetches the collections from the server
   * @function
   */
  function loadCollections() {
    const collectionUrl =  serverURL + '/collections&token=' + lastToken
    try {
      const resp = fetch(collectionUrl, {
        method: 'GET'
      }).then(async (resp) => {
              if (resp.ok) {
                return resp.json();
              } else {
                throw new Error(`Failed to get collections: ${resp.status}`, {cause:resp});
              }
          })
        .then((respData) => {
            // Save response data
            
        })
        .catch(function(err) {
          console.log('Error: ',err);
          if (onFailure && typeof(onFailure) === 'function') {
            onFailure();
          }
      });
    } catch (error) {
      if (onFailure && typeof(onFailure) === 'function') {
        onFailure();
      }
    }
  }


  function updateSandboxInfo(sandboxInfo) {
    setSandboxInfo(sandboxInfo);
  }

  function updateCollectionInfo(collectionInfo) {
    setCollectionInfo(collectionInfo);
  }

  function commonLoginUser(formData, onSuccess, onFailure) {
    const loginUrl = serverURL + '/login';
    try {
      const resp = fetch(loginUrl, {
        credentials: 'include',
        method: 'POST',
        body: formData
      }).then(async (resp) => {
              if (resp.ok) {
                return resp.json();
              } else {
                throw new Error(`Failed to log in: ${resp.status}`, {cause:resp});
              }
          })
        .then((respData) => {
            // Save token and set status
            const loginToken = respData['value'];
            loginStore.saveLoginToken(loginToken);
            let userSettings = null;
            try {
              userSettings = JSON.parse(respData['settings']);
            } catch (ex) {
              console.log('Exception thrown for user settings', respData['settings']);
              console.log(ex);
              userSettings = {};
            }
            setUserSettings({name:resp['name'], settings:userSettings, admin:resp['admin']});
            setLoggedIn(true);
            setLastToken(loginToken);
            if (onSuccess && typeof(onSuccess) === 'function') {
              onSuccess();
            }
        })
        .catch(function(err) {
          console.log('Error: ',err);
          if (onFailure && typeof(onFailure) === 'function') {
            onFailure();
          }
      });
    } catch (error) {
      if (onFailure && typeof(onFailure) === 'function') {
        onFailure();
      }
    }
  }

  function loginUser(url, user, password, onSuccess, onFailure) {
    const formData = new FormData();

    formData.append('url', url);
    formData.append('user', user);
    formData.append('password', password);

    commonLoginUser(formData, onSuccess, onFailure);
  }

  function loginUserToken(token, onSuccess, onFailure) {
    const formData = new FormData();
    formData.append('token', token);
    commonLoginUser(formData, onSuccess, onFailure);
  }

  function handleLogin(url, user, password, remember) {
    setDbUser(user);
    setDbURL(url);
    setDbRemember(remember);
    // Check parameters
    const validCheck = LoginCheck(url, user, password);

    setLoginValid(validCheck);
    if (validCheck.valid) {
      // TODO: UI indication while logging in (throbber?)

      // Try to log user in
      loginUser(url, user, password, () => {
        // If log in successful then...
        if (remember === true) {
          loginStore.saveLoginInfo(url, user, remember);
        } else {
          loginStore.clearLoginInfo();
        }
        // Load collections
        loadCollections();
      }, () => {
        // If log in fails
        console.log('LOGIN BY USER FAILED');
      });
    }
  }

  function editCollectionUpload(collectionId, uploadName, breadcrumbName) {
    const uploadUrl = serverURL + '/upload';
    // Get the information on the upload
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(uploadUrl, {
      'method': 'POST',
      'data': formData
    });
    console.log(resp);
    */

    // Set the uploaded information
    let fakeLoadedData = sandboxInfo.find((item) => item.collectionId === collectionId && item.name === uploadName);
    if (!fakeLoadedData) {
      const curCollection = collectionInfo.find((item) => item.id === collectionId);
      if (curCollection) {
        const curUpload = curCollection.uploads.find((item) => item.name === uploadName);
        if (curUpload) {
          fakeLoadedData = {collectionId, name:curUpload.name, location:curUpload.location,
             'images': [{'name':'image1111', 'url': '../IMAG0120.JPG', 'species': [{'name':'cat','count':'2'},{'name':'deer','count':'0'}]},
                        {'name':'image0002', 'url': '../IMAG0120.JPG', 'species': [{'name':'dog','count':'1'}]},
                        {'name':'image0004', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0005', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0006', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0007', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0008', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0009', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0010', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0011', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0012', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0013', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0014', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0015', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0016', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0017', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0018', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0019', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0020', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0021', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0022', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0023', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0024', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0025', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0026', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0027', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0028', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0029', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0030', 'url': '../IMAG0120.JPG', 'species': []},
                      ]
                   }
        }
      }
    }
    if (!fakeLoadedData) {
      fakeLoadedData = {collectionId, name:uploadName, 'location':'CAN06', 
             'images': [{'name':'image3333', 'url': '../IMAG0120.JPG', 'species': [{'name':'cat','count':'2'},{'name':'deer','count':'0'}]},
                        {'name':'image0002', 'url': '../IMAG0120.JPG', 'species': [{'name':'dog','count':'1'}]},
                        {'name':'image0004', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0005', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0006', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0007', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0008', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0009', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0010', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0011', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0012', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0013', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0014', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0015', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0016', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0017', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0018', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0019', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0020', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0021', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0022', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0023', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0024', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0025', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0026', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0027', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0028', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0029', 'url': '../IMAG0120.JPG', 'species': []},
                        {'name':'image0030', 'url': '../IMAG0120.JPG', 'species': []},
                      ]
                   }
    }
    setCurrentAction(UserActions.UploadEdit, fakeLoadedData, true, breadcrumbName);
  }

  function handleSearch(searchTerm) {
    return curSearchHandler(searchTerm);
  }

  function clearSearch() {
    setCurSearchTitle(null);
    setCurSearchHandler(null);
  }

  function setupSearch(searchLabel, searchHandler) {
    if (searchLabel == undefined && searchHandler == undefined) {
      clearSearch();
      return;
    }
    if (!searchHandler || typeof searchHandler != "function") {
      console.log('Error: Invalid function passed when setting up search for \"'+searchLabel+'\"');
      return;
    }

    setCurSearchTitle(searchLabel);
    setCurSearchHandler(() => searchHandler);
  }

  function getUserSettings() {
    const settingsUrl = serverURL + '/settings';
    // Get the information on the upload
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(settingsUrl, {
      'method': 'GET',
      'data': formData
    });
    console.log(resp);
    S
    */
  }

  function updateUserSettings(userSettings) {
    const settingsUrl = serverURL + '/settings';
    // Get the information on the upload
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(settingsUrl, {
      'method': 'POST',
      'data': formData
    });
    console.log(resp);
    */
    setUserSettings(userSettings);
  }

  function handleSettings(userSettings) {
    const mySettingsId = settingsRequestId = settingsRequestId+1;
    const workingTimeoutId = settingsTimeoutId;
    settingsTimeoutId = null;
    if (workingTimeoutId != null) {
      window.clearTimeout(workingTimeoutId);
    }
    window.setTimeout(() => {
      // If we're still the only one trying to send settings, send them
      if (settingsRequestId === mySettingsId) {
        settingsTimeoutId = window.setTimeout(() =>
                  {
                    if (settingsRequestId === mySettingsId) updateUserSettings(userSettings)
                  }
        );
      }
    }, 500);
  }

  // Get mobile device information if we don't have it yet
  if (mobileDevice == null && !mobileDeviceChecked) {
    setMobileDevice(navigator.userAgent.indexOf('Mobi') > -1);
    setMobileDeviceChecked(true);
  }

  function renderAction(action, editing) {
    // TODO: Store lastToken fetched (and be sure to update it)
    switch(action) {
      case UserActions.None:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <CollectionsInfoContext.Provider value={collectionInfo}>
                <SandboxInfoContext.Provider value={sandboxInfo}>
                  <Landing onUserAction={setCurrentAction} onSandboxUpdate={updateSandboxInfo} onCollectionUpdate={updateCollectionInfo} />
                </SandboxInfoContext.Provider>
              </CollectionsInfoContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
        );
      case UserActions.Upload:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <SandboxInfoContext.Provider value={sandboxInfo}>
                <UploadManage selectedUpload={curActionData} onEditUpload={editCollectionUpload} />
              </SandboxInfoContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
        );
      case UserActions.UploadEdit:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <UploadEditContext.Provider value={curActionData}>
                <UploadEdit selectedUpload={curActionData.uploadName}
                            onCancel={() => setCurrentAction(UserActions.Upload, curActionData, false)} 
                            searchSetup={setupSearch} />
              </UploadEditContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
        );
      case UserActions.Collection:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <CollectionsInfoContext.Provider value={collectionInfo}>
                <CollectionsManage selectedCollection={curActionData} onEditUpload={editCollectionUpload} 
                                   searchSetup={setupSearch} />
              </CollectionsInfoContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
      );
      case UserActions.Query:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <CollectionsInfoContext.Provider value={collectionInfo}>
                <Queries />
              </CollectionsInfoContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
        );
      case UserActions.Maps:
        return (
            <TokenContext.Provider value={lastToken}>
              <Maps />
            </TokenContext.Provider>
        );
    }
  }

  const narrowWindow = isNarrow;
  return (
    <main className={styles.main} style={{position:'relative'}}>
      <ThemeProvider theme={theme}>
        <MobileDeviceContext.Provider value={mobileDevice}>
          <NarrowWindowContext.Provider value={narrowWindow}>
            <TitleBar search_title={curSearchTitle} onSearch={handleSearch} onSettings={loggedIn ? handleSettings : null}
                      size={narrowWindow?"small":"normal"} 
                      breadcrumbs={breadcrumbs} onBreadcrumb={restoreBreadcrumb}/>
            {!curLoggedIn ? 
               <LoginValidContext.Provider value={loginValidStates}>
                <Login prev_url={dbURL} prev_user={dbUser} prev_remember={dbRemember} onLogin={handleLogin} />
               </LoginValidContext.Provider>
              :
              renderAction(curAction, editing)
            }
            <FooterBar/>
            <Grid id="login-checking-wrapper" container direction="row" alignItems="center" justifyContent="center" something={lastToken}
                  sx={{position:'absolute', top:0, left:0, width:'100vw', height:'100vh', backgroundColor:'rgb(0,0,0,0.5)', zIndex:11111,
                       visibility:checkedToken ? 'hidden':'visible', display:checkedToken ? 'none':'inherit'}}
            >
              <div style={{backgroundColor:'rgb(0,0,0,0.8)', border:'1px solid grey', borderRadius:'15px', padding:'25px 10px'}}>
                <Grid container direction="column" alignItems="center" justifyContent="center" >
                    <Typography gutterBottom variant="body2" color="lightgrey">
                      Restoring previous session, please wait...
                    </Typography>
                    <CircularProgress variant="indeterminate" />
                </Grid>
              </div>
            </Grid>
          </NarrowWindowContext.Provider>
        </MobileDeviceContext.Provider>
      </ThemeProvider>
    </main>
  )
}

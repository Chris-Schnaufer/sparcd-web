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
      return curToken ? curToken : null;
    }

    return null;
  },

  saveLoginToken(token) {
    if (typeof window !== "undefined") {
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
  const DEFAULT_DISPLAY_WIDTH = 800.0;  // Used as default until the window is ready
  const DEFAULT_DISPLAY_HEIGHT = 600.0; // Used as default until the window is ready
  const DEFAULT_HEADER_HEIGHT = 63.0;   // Used as default until the window is ready
  const DEFAULT_FOOTER_HEIGHT = 76.0;   // Used as default until the window is ready
  const footerRef = React.useRef();   // Used for sizeing
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
  const [loadingCollections, setLoadingCollections] = React.useState(false);
  const [loginValid, setLoginValid] = React.useState(DefaultLoginValid);
  const [loggedIn, setLoggedIn] = React.useState(null);
  const [mobileDeviceChecked, setMobileDeviceChecked] = React.useState(false);
  const [mobileDevice, setMobileDevice] = React.useState(null);
  const [dbRemember, setDbRemember] = React.useState(false);
  const [sandboxInfo, setSandboxInfo] = React.useState(null);
  const [savedLoginFetched, setSavedLoginFetched] = React.useState(false);
  const [savedTokenFetched, setSavedTokenFetched] = React.useState(false);
  const [sizeFooter, setSizeFooter] = React.useState({top:DEFAULT_DISPLAY_HEIGHT-76.0,left:0.0, width:DEFAULT_DISPLAY_WIDTH, height:76.0});
  const [sizeTitle, setSizeTitle] = React.useState({top:0.0, left:0.0, width:DEFAULT_DISPLAY_WIDTH, height:DEFAULT_HEADER_HEIGHT});
  const [sizeWindow, setSizeWindow] = React.useState({DEFAULT_DISPLAY_WIDTH:640, DEFAULT_DISPLAY_HEIGHT:480});
  const [sizeWorkspace, setSizeWorkspace] = React.useState({top:DEFAULT_HEADER_HEIGHT,
                                                            left:0.0,
                                                            width:DEFAULT_DISPLAY_WIDTH, 
                                                            height:DEFAULT_DISPLAY_HEIGHT-DEFAULT_HEADER_HEIGHT-DEFAULT_FOOTER_HEIGHT});
  const [serverURL, setServerURL] = React.useState(utils.getServer());
  const [userSettings, setUserSettings] =  React.useState(null);

  const loginValidStates = loginValid;
  let settingsTimeoutId = null;   // Used to manage of the settings calls to the server
  let settingsRequestId = 0;        // Used to prevent sending multiple requests to server
  let curLoggedIn = loggedIn;

  handleSearch = handleSearch.bind(Home);
  setupSearch = setupSearch.bind(Home);
  restoreBreadcrumb = restoreBreadcrumb.bind(Home);

  // TODO: load locations dynamically
  // TODO: load species dynamically

  // TODO: change dependencies to Theme & use @media to adjust
  // Sets the narrow flag when the window is less than 600 pixels
  React.useEffect(() => setIsNarrow(window.innerWidth <= 640), []);

  // Calcuate available space in the window and what the control sizes are
  React.useLayoutEffect(() => {
    calculateLayoutSizes();
  }, [footerRef]);

  // Adds a resize handler to the window, and automatically removes it
  React.useEffect(() => {
      function onResize () {
          // TODO: transition to MaterialUI sizes          
          const newSize = {'width':window.innerWidth,'height':window.innerHeight};
          setIsNarrow(newSize.width <= 640);
          calculateLayoutSizes();
      }

      window.addEventListener("resize", onResize);
  
      return () => {
          window.removeEventListener("resize", onResize);
      }
  }, [footerRef]);

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
                 window.setTimeout(() => loadCollections(lastLoginToken), 500);
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
  }, [checkedToken, curLoggedIn, loadCollections, loginUserToken, savedTokenFetched, savedLoginFetched]);

  /**
   * Calculates the sizes of the window, header, footer, and workspace area (not used by header or footer)
   * @function
   */
  function calculateLayoutSizes() {
    const newSize = {'width':window.innerWidth,'height':window.innerHeight};
    setSizeWindow(newSize);    

    // Get the title size
    let titleSize = {top:0.0, left:0.0, width:newSize.width, height:DEFAULT_HEADER_HEIGHT};
    const titleEl = document.getElementById('sparcd-header');
    if (titleEl) {
      titleSize = titleEl.getBoundingClientRect();
      setSizeTitle({top:0.0, left:0.0, width:window.width, height:titleSize});
    }

    // Get the title size
    let footerSize = {top:newSize.height-DEFAULT_FOOTER_HEIGHT, left:0.0, width:newSize.width, height:DEFAULT_FOOTER_HEIGHT};
    const footerEl = document.getElementById('sparcd-footer');
    if (footerEl) {
      footerSize = footerEl.getBoundingClientRect();
      setSizeFooter({top:newSize.width-footerSize, left:0.0, width:newSize.width, height:footerSize});
    }

    // Set the workspace size
    const workspaceSize = {top:titleSize.height, left:titleSize.left, width:titleSize.width, 
                            height:newSize.height-titleSize.height-footerSize.height}
    setSizeWorkspace(workspaceSize);
  }

  /**
   * Restores the indicated navigation breadcrumb
   * @function
   * @param {object} breadcrumb The breadcrumb to restore
   */
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

  /**
   * Sets the current action based upon the users selection
   * @function
   * @param {object} action The working user action
   * @param {object} actionData Data associated with the action
   * @param {boolean} areEditing Is this an editing command
   * @param {string} breadcrumbName What is the display name of this action
   */
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

  // For some reason changing this to useCallback() causes the build to fail 
  /**
   * Fetches the collections from the server
   * @function
   */
  function loadCollections(token) {
    const cur_token = token || lastToken;
    console.log('LOADCOLLECTIONS')
    setLoadingCollections(true);
    const collectionUrl =  serverURL + '/collections?token=' + encodeURIComponent(cur_token)
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
          setLoadingCollections(false);
          const curCollections = respData.sort((first, second) => first.name.localeCompare(second.name, undefined, { sensitivity: "base" }));
          console.log('COLLECTIONS',curCollections);
          setCollectionInfo(curCollections);
        })
        .catch((err) => {
          console.log('Error: ',err);
          setLoadingCollections(false);
      });
    } catch (error) {
      console.log('Error: ',error);
      setLoadingCollections(false);
    }
  }

  /**
   * Sets the information of the sandbox items
   * @function
   * @param {array} sandboxInfo Array of sandbox items
   */
  function updateSandboxInfo(sandboxInfo) {
    setSandboxInfo(sandboxInfo);
  }

  /**
   * Sets the information of the collection items
   * @function
   * @param {array} collectionInfo Array of collection items
   */
  function updateCollectionInfo(collectionInfo) {
    setCollectionInfo(collectionInfo);
  }

  /**
   * Common function for logging the user in
   * @function
   * @param {object} formData The form data for logging in
   * @param {function} onSuccess Function to call upon success
   * @param {function} onFailure Function to call when there's a login failure
   */
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
              onSuccess(loginToken);
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

  /**
   * Attempts to login the user with credentials
   * @function
   * @param {string} url The url of the storage to access (used as the login validator by the server)
   * @param {string} user The usernanme for logging in
   * @param {string} password The user's associated password
   * @param {function} onSuccess Function to call upon success
   * @param {function} onFailure Function to call when there's a login failure
   */
  function loginUser(url, user, password, onSuccess, onFailure) {
    const formData = new FormData();

    formData.append('url', url);
    formData.append('user', user);
    formData.append('password', password);

    commonLoginUser(formData, onSuccess, onFailure);
  }

  // For some reason changing this to useCallback() causes the build to fail 
  /**
   * Attempts to login the user with a stored token
   * @function
   * @param {string} token The token to try to log in with
   * @param {function} onSuccess Function to call upon success
   * @param {function} onFailure Function to call when there's a login failure
   */
  function loginUserToken(token, onSuccess, onFailure) {
    const formData = new FormData();
    formData.append('token', token);
    commonLoginUser(formData, onSuccess, onFailure);
  }

  /**
   * Handles logging in the user and saves the login information
   * @function
   * @param {string} url The url of the storage to access (used as the login validator by the server)
   * @param {string} user The usernanme for logging in
   * @param {string} password The user's associated password
   * @param {boolean} remember Set to a truthy value to indicate saving non-sensitive login information
   */
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
      loginUser(url, user, password, (new_token) => {
        // If log in successful then...
        if (remember === true) {
          loginStore.saveLoginInfo(url, user, remember);
        } else {
          loginStore.clearLoginInfo();
        }
        // Load collections
        window.setTimeout(() => loadCollections(new_token), 500);
      }, () => {
        // If log in fails
        console.log('LOGIN BY USER FAILED');
      });
    }
  }

  /**
   * Logs the user out
   * @function
   */
  function handleLogout() {
    setUserSettings(null);
    setLastToken(null);
    setEditing(false);
    setLoggedIn(false);
    loginStore.clearLoginToken();
  }

  /**
   * Common function that loads the upload information for editing purposes
   * @function
   * @param {string} collectionId The ID of the collection containing the upload 
   * @param {string} uploadId The ID of the upload to edit
   * @param {string} breadcrumbName The name of the navigation breadcrumb to use
   */
  function editCollectionUpload(collectionId, uploadId, breadcrumbName) {
    const uploadUrl = serverURL + '/upload?token=' + encodeURIComponent(lastToken) + 
                                          '&id=' + encodeURIComponent(collectionId) + 
                                          '&up=' + encodeURIComponent(uploadId);
    // Get the information on the upload
    try {
      const resp = fetch(uploadUrl, {
        method: 'GET',
      }).then(async (resp) => {
            if (resp.ok) {
              return resp.json();
            } else {
              throw new Error(`Failed to log in: ${resp.status}`, {cause:resp});
            }
          })
        .then((respData) => {
          const curCollection = collectionInfo.find((item) => item.id === collectionId);
          if (curCollection) {
            const curUpload = curCollection.uploads.find((item) => item.key === uploadId);
            if (curUpload) {
              // Add our token in
              const cur_images = respData.map((img) => {img['url'] = img['url'] + '&t=' + lastToken; return img;})
              setCurrentAction(UserActions.UploadEdit, 
                               {collectionId, name:curUpload.name, location:curUpload.location, images:cur_images},
                               true,
                               breadcrumbName);
            } else {
              console.log('ERROR: unable to find upload ID', uploadId, 'for collection ID', collectionId);
            }
          } else {
            console.log('ERROR: unable to find collection ID', collectionId);
          }
        })
        .catch(function(err) {
          console.log('Error: ',err);
      });
    } catch (error) {
      console.log('Error: ',error);
    }
  }

  /**
   * Calls the callback to perform a search
   * @function
   * @param {string} searchTerm The search term to pass to the callback
   */
  function handleSearch(searchTerm) {
    return curSearchHandler(searchTerm);
  }

  /**
   * Clears the search and the controls
   * @function
   */
  function clearSearch() {
    setCurSearchTitle(null);
    setCurSearchHandler(null);
  }

  /**
   * Enables the setting up of searching feature
   * @function
   * @param {string} searchLabel The label of the search
   * @param {function} searchHandler Function to call when the user wants to search
   */
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

  /**
   * Fetches the user's settings from the server
   * @function
   */
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

  /**
   * Updates the user's settings on the server
   * @function
   * @param {object} userSettings The settings to save on the server for the user
   */
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

  /**
   * Sets the remember login information flag to true or false (is it truthy, or not?)
   * @function
   * @param {boolean} newRemember Set to true for non-sensitive login details to be remembered, or false
   */
  function handleRememberChanged(newRemember) {
    setDbRemember(newRemember);
  }

  /**
   * Handles displaying the user settings
   * @function
   * @param {object} userSettings The user settings to have managed
   */
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
  if (typeof window !== 'undefined') {
    if (mobileDevice == null && !mobileDeviceChecked) {
      setMobileDevice(navigator.userAgent.indexOf('Mobi') > -1);
      setMobileDeviceChecked(true);
    }
  }

  /**
   * Returns the UI components for the specified action
   * @function
   * @param {object} action The well known user action
   * @param {boolean} editing The state of the user editing something
   * @return {object} The rendered action UI
   */
  function renderAction(action, editing) {
    // TODO: Store lastToken fetched (and be sure to update it)
    switch(action) {
      case UserActions.None:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <CollectionsInfoContext.Provider value={collectionInfo}>
                <SandboxInfoContext.Provider value={sandboxInfo}>
                  <Landing loadingCollections={loadingCollections} onUserAction={setCurrentAction} onSandboxUpdate={updateSandboxInfo} onCollectionUpdate={updateCollectionInfo} />
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
                <CollectionsManage loadingCollections={loadingCollections} selectedCollection={curActionData} 
                                   onEditUpload={editCollectionUpload} searchSetup={setupSearch} />
              </CollectionsInfoContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
      );
      case UserActions.Query:
        return (
           <BaseURLContext.Provider value={serverURL}>
             <TokenContext.Provider value={lastToken}>
              <CollectionsInfoContext.Provider value={collectionInfo}>
                <Queries loadingCollections={loadingCollections}  />
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

  // Render the UI
  const narrowWindow = isNarrow;
  return (
    <main className={styles.main} style={{position:'relative'}}>
      <ThemeProvider theme={theme}>
        <MobileDeviceContext.Provider value={mobileDevice}>
          <NarrowWindowContext.Provider value={narrowWindow}>
            <TitleBar search_title={curSearchTitle} onSearch={handleSearch} onSettings={loggedIn ? handleSettings : null}
                      onLogout={handleLogout} size={narrowWindow?"small":"normal"} 
                      breadcrumbs={breadcrumbs} onBreadcrumb={restoreBreadcrumb}/>
            {!curLoggedIn ? 
              <LoginValidContext.Provider value={loginValidStates}>
                <Login prev_url={dbURL} prev_user={dbUser} prev_remember={dbRemember} onLogin={handleLogin}
                       onRememberChange={handleRememberChanged} />
              </LoginValidContext.Provider>
              :
              renderAction(curAction, editing)
            }
            <FooterBar ref={footerRef} />
            <Grid id="login-checking-wrapper" container direction="row" alignItems="center" justifyContent="center"
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

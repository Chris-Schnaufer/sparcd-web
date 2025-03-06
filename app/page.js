'use client'

import * as React from 'react';
import styles from './page.module.css'
import { ThemeProvider } from "@mui/material/styles";

import theme from './Theme'
import Landing from './Landing'
import FooterBar from './components/FooterBar'
import Login from './Login'
import TitleBar from './components/TitleBar'
import UploadManage from './UploadManage'
import UploadEdit from './UploadEdit'
import UserActions from './components/userActions'
import { LoginCheck, LoginValidContext, DefaultLoginValid } from './checkLogin'
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext, TokenContext } from './serverInfo'
import * as utils from './utils'

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
      return window.localStorage.getItem('login.token');
    }
  },

  saveLoginToken(token) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem('login.token', "" + token);
    }
  },

  clearLoginToken(token) {
    if (typeof window !== "undefined") {
      window.localStorage.setItem('login.token', null);
    }
  }
};

export default function Home() {
  const [savedLoginFetched, setSavedLoginFetched] = React.useState(false);
  const [savedTokenFetched, setSavedTokenFetched] = React.useState(false);
  const [curSearchTitle, setCurSearchTitle] = React.useState(null);
  const [loggedIn, setLoggedIn] = React.useState(null);
  const [dbUser, setDbUser] = React.useState('');
  const [dbURL, setDbURL] = React.useState('');
  const [remember, setRemember] = React.useState(false);
  const [loginValid, setLoginValid] = React.useState(DefaultLoginValid);
  const [serverURL, setServerURL] = React.useState(utils.getServer());
  const [curAction, setCurAction] = React.useState(UserActions.None);
  const [curActionData, setCurActionData] = React.useState(null);
  const [editing, setEditing] = React.useState(false);
  const [mobileDeviceChecked, setMobileDeviceChecked] = React.useState(false);
  const [mobileDevice, setMobileDevice] = React.useState(null);
  const [sandboxInfo, setSandboxInfo] = React.useState(null);
  const [collectionInfo, setCollectionInfo] = React.useState(null);
  const [lastToken, setLastToken ] = React.useState(null);
  const loginValidStates = loginValid;
  let curLoggedIn = loggedIn;
  let curSearchHandler = null;

  function setCurrentAction(action, actionData, areEditing) {
    if (Object.values(UserActions).indexOf(action) > -1) {
      if (!actionData) {
        actionData = null;
      }
      // TODO: save state and data (and auto-restore)
      setCurAction(action);
      setCurActionData(actionData);
      setEditing(!!areEditing);
    } else {
      // TODO: Put up informational message about not valid command
      console.log('Invalid current action specified', action);
    }
  }

  function updateSandboxInfo(sandboxInfo) {
    setSandboxInfo(sandboxInfo);
  }

  function updateCollectionInfo(collectionInfo) {
    setCollectionInfo(collectionInfo);
  }

  function commonLoginUser(formData) {
    const loginUrl = serverURL + '/login';
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(loginUrl, {
      'method': 'POST',
      'data': formData
    });
    console.log(resp);
    */

    return crypto.randomUUID();
  }

  function loginUser(url, user, password) {
    const formData = new FormData();

    formData.append('url', url);
    formData.append('user', user);
    formData.append('password', password);

    return commonLoginUser(formData);
  }

  function loginUserToken(token) {
    const formData = new FormData();
    formData.append('token', token);
    console.log('LOGIN TOKEN', token);
    // TODO: make call
    // return commonLoginUser(formData);
    return true;
  }

  function handleLogin(url, user, password, remember) {
    setDbUser(user);
    setDbURL(url);
    setRemember(remember);
    // Check parameters
    const validCheck = LoginCheck(url, user, password);

    setLoginValid(validCheck);
    if (validCheck.valid) {
      // TODO: UI indication while logging in (throbber?)

      // Try to log user in
      const login_token = loginUser(url, user, password);
      // TODO: remove login this indication flag
      setLoggedIn(login_token);
      if (!!login_token) {
        setLoggedIn(true);
        loginStore.saveLoginToken(login_token);

        // If log in successful then...
        if (remember == true) {
          loginStore.saveLoginInfo(url, user, remember);
        } else {
          loginStore.clearLoginInfo();
        }
        // Load catalogs
      }
    }
  }

  function editUpload(uploadInfo) {
    setEditing(true);
    console.log('NOW',curActionData,uploadInfo);
    setCurActionData(uploadInfo);
  }

  function handleSearch(searchTerm) {
    console.log('SEARCH', searchTerm);
    curSearchFunc(searchTerm);
  }

  function handleImageSearch(searchTerm) {
    console.log('IMAGE SEARCH 2', searchTerm);
  }

  function clearSearch() {
    setCurSearchTitle(null);
    curSearchHandler(null);
  }

  function setupSearch(searchLabel, searchHandler) {
    if (!searchHandler || typeof searchHandler != "function") {
      console.log('Error: Invalid function passed when setting up search for \"'+searchLabel+'\"');
      return;
    }

    setCurSearchTitle(searchLabel);
    curSearchHandler = searchHandler;
  }

  // Load saved token and see if session is still valid
  React.useLayoutEffect(() => {
    if (!savedTokenFetched && !curLoggedIn) {
      const lastLoginToken = loginStore.loadLoginToken();
      setSavedTokenFetched(true);
      if (lastLoginToken) {
        curLoggedIn = loginUserToken(lastLoginToken);
        setLoggedIn(curLoggedIn);
      }
      if (!lastLoginToken || !curLoggedIn) {
        loginStore.clearLoginToken();
      }
    }

    // Load saved user information: if we haven't already and we're not logged in
    if (!savedLoginFetched && !curLoggedIn) {
      const loInfo = loginStore.loadLoginInfo();
      setSavedLoginFetched(true);
      if (loInfo != null) {
        setDbURL(loInfo.url);
        setDbUser(loInfo.user);
        setRemember(!!loInfo.remember);
      }
    }
  }, []);

  if (mobileDevice == null && !mobileDeviceChecked) {
    setMobileDevice(navigator.userAgent.indexOf('Mobi') > -1);
    setMobileDeviceChecked(true);
  }

  // Load the last token to make it available for rendering
  React.useLayoutEffect(() => {
    setLastToken(loginStore.loadLoginToken());
  }, []);

  function renderAction(action, editing) {
    // TODO: Store lastToken fetched (and be sure to update it)
    //const lastToken = loginStore.loadLoginToken();
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
                { editing == false ? 
                  <UploadManage selectedUpload={curActionData} onEdit_func={editUpload} />
                  : <UploadEdit selectedUpload={curActionData} onCancel_func={() => setEditing(false)} 
                                searchSetup_func={setupSearch} />
                }
              </SandboxInfoContext.Provider>
             </TokenContext.Provider>
           </BaseURLContext.Provider>
        );
    }
  }

  return (
    <main className={styles.main}>
      <ThemeProvider theme={theme}>
        <MobileDeviceContext.Provider value={mobileDevice}>
          <TitleBar search_title={curSearchTitle} search_func={handleSearch} />
          {!curLoggedIn ? 
             <LoginValidContext.Provider value={loginValidStates}>
              <Login prev_url={dbURL} prev_user={dbUser} prev_remember={remember} login_func={handleLogin} />
             </LoginValidContext.Provider>
            :
            renderAction(curAction, editing)
          }
          <FooterBar/>
        </MobileDeviceContext.Provider>
      </ThemeProvider>
    </main>
  )
}

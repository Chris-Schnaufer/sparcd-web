'use client'

import { useState } from 'react';
import { useContext } from 'react';
import styles from './page.module.css'
import { ThemeProvider } from "@mui/material/styles";

import theme from './Theme'
import Landing from './Landing'
import FooterBar from './components/FooterBar'
import Login from './Login'
import ManageUpload from './ManageUpload'
import TitleBar from './components/TitleBar'
import UserActions from './components/userActions'
import { LoginCheck, LoginValidContext, DefaultLoginValid } from './checkLogin'
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, SandboxInfoContext, TokenContext } from './serverInfo'
import * as utils from './utils'

// This is declared here so that it doesn't raise an error on server-side compile
const loginStore = {

  loadURL() {
    return window.localStorage.getItem('login.url')
  },

  loadUsername() {
    return window.localStorage.getItem('login.user');
  },

  loadRemember() {
    return window.localStorage.getItem('login.remember');
  },

  saveURL(url) {
    window.localStorage.setItem('login.url', "" + url)
  },

  saveUsername(username) {
    window.localStorage.setItem('login.user', "" + username)
  },

  saveRemember(remember) {
    window.localStorage.setItem('login.remember', !!remember)
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
    return window.localStorage.getItem('login.token');
  },

  saveLoginToken(token) {
    window.localStorage.setItem('login.token', "" + token)
  },

  clearLoginToken(token) {
    window.localStorage.setItem('login.token', null)
  }
};

export default function Home() {
  const [savedLoginFetched, setSavedLoginFetched] = useState(false);
  const [savedTokenFetched, setSavedTokenFetched] = useState(false);
  const [loggedIn, setLoggedIn] = useState(null);
  const [dbUser, setDbUser] = useState('');
  const [dbURL, setDbURL] = useState('');
  const [remember, setRemember] = useState(false);
  const [loginValid, setLoginValid] = useState(DefaultLoginValid);
  const [serverURL, setServerURL] = useState(utils.getServer());
  const [curAction, setCurAction] = useState(UserActions.None);
  const [curActionData, setCurActionData] = useState(null);
  const [mobileDeviceChecked, setMobileDeviceChecked] = useState(false);
  const [mobileDevice, setMobileDevice] = useState(null);
  const [sandboxInfo, setSandboxInfo] = useState(null);
  const [collectionInfo, setCollectionInfo] = useState(null);
  const loginValidStates = loginValid;
  let curLoggedIn = loggedIn;

  function setCurrentAction(action, actionData) {
    if (Object.values(UserActions).indexOf(action) > -1) {
      if (!actionData) {
        actionData = null;
      }
      // TODO: save state and data (and auto-restore)
      setCurAction(action);
      setCurActionData(actionData);
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
      // TODO: remove login indication
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

  // Load saved token and see if session is still valid
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

  if (mobileDevice == null && !mobileDeviceChecked) {
    setMobileDevice(navigator.userAgent.indexOf('Mobi') > -1);
    setMobileDeviceChecked(true);
  }

  function renderAction(action) {
    // TODO: Store lastToken fetched (and be sure to update it)
    const lastToken = loginStore.loadLoginToken();
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
                <ManageUpload selectedUpload={curActionData} />
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
          <TitleBar/>
          {!curLoggedIn ? 
             <LoginValidContext.Provider value={loginValidStates}>
              <Login prev_url={dbURL} prev_user={dbUser} prev_remember={remember} login_func={handleLogin} />
             </LoginValidContext.Provider>
            :
            renderAction(curAction)
          }
          <FooterBar/>
        </MobileDeviceContext.Provider>
      </ThemeProvider>
    </main>
  )
}

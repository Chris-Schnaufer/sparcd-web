'use client'

import * as React from 'react';
import styles from './page.module.css'
import { ThemeProvider } from "@mui/material/styles";

import CollectionsManage from './CollectionsManage'
import FooterBar from './components/FooterBar'
import Landing from './Landing'
import Login from './Login'
import Queries from './Queries'
import theme from './Theme'
import TitleBar from './components/TitleBar'
import UploadManage from './UploadManage'
import UploadEdit from './UploadEdit'
import UserActions from './components/userActions'
import { LoginCheck, LoginValidContext, DefaultLoginValid } from './checkLogin'
import { BaseURLContext, CollectionsInfoContext, MobileDeviceContext, NarrowWindowContext, 
         SandboxInfoContext, TokenContext, UploadEditContext } from './serverInfo'
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
  const [breadcrumbs, setBreadcrumbs] = React.useState([]);
  const [collectionInfo, setCollectionInfo] = React.useState(null);
  const [curSearchTitle, setCurSearchTitle] = React.useState(null);
  const [curAction, setCurAction] = React.useState(UserActions.None);
  const [curActionData, setCurActionData] = React.useState(null);
  const [curSearchHandler, setCurSearchHandler] = React.useState(null);
  const [dbUser, setDbUser] = React.useState('');
  const [dbURL, setDbURL] = React.useState('');
  const [editing, setEditing] = React.useState(false);
  const [isNarrow, setIsNarrow] = React.useState(null);
  const [lastToken, setLastToken ] = React.useState(null);
  const [loginValid, setLoginValid] = React.useState(DefaultLoginValid);
  const [loggedIn, setLoggedIn] = React.useState(null);
  const [mobileDeviceChecked, setMobileDeviceChecked] = React.useState(false);
  const [mobileDevice, setMobileDevice] = React.useState(null);
  const [remember, setRemember] = React.useState(false);
  const [sandboxInfo, setSandboxInfo] = React.useState(null);
  const [savedLoginFetched, setSavedLoginFetched] = React.useState(false);
  const [savedTokenFetched, setSavedTokenFetched] = React.useState(false);
  const [serverURL, setServerURL] = React.useState(utils.getServer());

  const loginValidStates = loginValid;
  let curLoggedIn = loggedIn;

  handleSearch = handleSearch.bind(Home);
  setupSearch = setupSearch.bind(Home);
  restoreBreadcrumb = restoreBreadcrumb.bind(Home);

  // TODO: change dependencies to Theme & use @media to adjust
  // Sets the narrow flag when the window is less than 600 pixels
  React.useEffect(() => setIsNarrow(window.innerWidth <= 640), []);

  // TODO: Global window resize handler?

  // Adds a resize handler to the window, and automatically removes it
  React.useEffect(() => {
      function onResize () {
          setIsNarrow(window.innerWidth <= 640);
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

  // Load the last token to make it available for rendering
  React.useLayoutEffect(() => {
    setLastToken(loginStore.loadLoginToken());
  }, []);

  function restoreBreadcrumb(breadcrumb) {
    const curCrumbs = breadcrumbs;
    curCrumbs.forEach((x) => console.log('RESTOREBREADCRUMBS',x));
    let curRestore = null;
    do {
      curRestore = curCrumbs.pop();
      if (curRestore && curRestore.name !== breadcrumb.name) {
      }
    } while (curRestore && curRestore.name !== breadcrumb.name);
    console.log('       ',breadcrumb.name);
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

  function editCollectionUpload(collectionId, uploadName, breadcrumbName) {
    const uploadUrl = serverURL + '/upload';
    // Get the information on the upload
    /* TODO: make call and wait for respone & return correct result
             need to handle null, 'invalid', and token values
    const resp = await fetch(loginUrl, {
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

  // Get mobile device information if we don't have it yet
  if (mobileDevice == null && !mobileDeviceChecked) {
    setMobileDevice(navigator.userAgent.indexOf('Mobi') > -1);
    setMobileDeviceChecked(true);
  }

  function renderAction(action, editing) {
    // TODO: Store lastToken fetched (and be sure to update it)
    //const lastToken = loginStore.loadLoginToken();
    switch(action) {
      case UserActions.None:
        console.log('NONE');
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
        console.log('UPLOAD');
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
        console.log('UPLOAD EDIT');
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
        console.log('COLLECTION');
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
        console.log('QUERY');
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
        console.log('MAPS');
        return ( <React.Fragment/>
        );
    }
  }

  console.log('REDRAW',curAction,curActionData,editing);
  const narrowWindow = isNarrow;
  return (
    <main className={styles.main}>
      <ThemeProvider theme={theme}>
        <MobileDeviceContext.Provider value={mobileDevice}>
          <NarrowWindowContext.Provider value={narrowWindow}>
          <TitleBar search_title={curSearchTitle} onSearch={handleSearch} size={narrowWindow?"small":"normal"} 
                    breadcrumbs={breadcrumbs} onBreadcrumb={restoreBreadcrumb}/>
          {!curLoggedIn ? 
             <LoginValidContext.Provider value={loginValidStates}>
              <Login prev_url={dbURL} prev_user={dbUser} prev_remember={remember} onLogin={handleLogin} />
             </LoginValidContext.Provider>
            :
            renderAction(curAction, editing)
          }
          <FooterBar/>
          </NarrowWindowContext.Provider>
        </MobileDeviceContext.Provider>
      </ThemeProvider>
    </main>
  )
}

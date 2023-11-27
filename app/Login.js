import Image from 'next/image'
import styles from './page.module.css'
import wildcatResearch from '../public/wildcatResearch.png'

export default function Login() {
  return (
    <div className={styles.login_background}>
    <div className={styles.login_wrapper}>
      <div className={styles.login_dialog_wrapper}>
        <div className={styles.login_dialog}>
          <Image height='60' alt="Wildcats Research" src={wildcatResearch} placeholder="blur" />
          <div className={styles.login_dialog_items}>
            <label htmlFor="url_entry" className={styles.login_dialog_label_item}>URL: </label>
            <input type="url" id="url_entry" autoComplete="url" 
                   aria-describedby="url_entry_hint"
                   placeholder="enter URL"
                   className={styles.login_dialog_url_item} />
            <span id="url_entry_hint" className={styles.login_dialog_entry_hint}>Example: the URL to the SPARC'd database</span>
            <label htmlFor="username_entry" className={styles.login_dialog_label_item}>Username: </label>
            <input type="text" id="username_entry" autoComplete="username"
                   aria-describedby="username_entry_hint"
                   placeholder="enter username"
                   className={styles.login_dialog_account_item} />
            <span id="username_entry_hint" className={styles.login_dialog_entry_hint}>Example: Your SPARC'd login name</span>
            <label htmlFor="password_entry" className={styles.login_dialog_label_item}>Password: </label>
            <input type="password" id="password_entry" autoComplete="current-password"
                   aria-describedby="password_entry_hint"
                   placeholder="enter password"
                   className={styles.password_dialog_account_item} />
            <span id="password_entry_hint" className={styles.login_dialog_entry_hint}>Example: Your SPARC'd password</span>
            <div className={styles.input_dialog_checkbox_wrapper}>
              <input type="checkbox" id="remember_login_fields"
                     name="remember_login_fields"
                     aria-describedby="remember_fields_hint" 
                     className={styles.login_dialog_remember_field} />
              <label htmlFor="remember_login_fields" className={styles.login_dialog_label_checkbox}>Remember URL and username</label>
            </div>
            <span id="remember_fields_hint" className={styles.login_dialog_entry_hint}>Remember fields when you log in next time</span>
            <div className={styles.login_dialog_login_button_wrap}>
              <input id="login_dialog_login_button" type="button" className={styles.login_dialog_login_button} value="Login" />
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
}
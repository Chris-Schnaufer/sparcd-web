import Image from 'next/image'
import styles from './components.module.css'

export default function TitleBar({children}) {
  return (
    <header className={styles.titlebar} role="banner">
      <div
        aria-description="Scientific Photo Analysis for Research & Conservation database"
        className={styles.titlebar_title}>SPARC&apos;d
      </div>
      <img src="/sparcd.png"
           alt="SPARC'd Logo"
           className={styles.titlebar_image} 
      />
      {children}
    </header>
    );
}

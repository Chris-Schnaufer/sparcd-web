import styles from './page.module.css'
import FooterBar from './components/FooterBar'
import Login from './Login'
import TitleBar from './components/TitleBar'

export default function Home() {
  return (
    <main className={styles.main}>
      <TitleBar/>
      <Login/>
      <FooterBar/>
    </main>
  )
}

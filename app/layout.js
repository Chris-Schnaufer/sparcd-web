import './globals.css'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'SPARCd',
  description: 'Scientific Photo Analysis for Research & Conservation database',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body id="MyBody" className={inter.className}>{children}</body>
    </html>
  )
}

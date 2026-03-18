import './globals.css'

export const metadata = {
  title: 'Aegis Cyber-Shield | Multimodal Security',
  description: 'AI-Powered Bulletproof Security Shield',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  )
}

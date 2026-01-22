import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Fleet Management System',
  description: 'Fleet Management and Tracking System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

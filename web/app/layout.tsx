import './styles.css';
import Link from 'next/link';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <header className="topnav">
          <nav>
            <Link href="/">Upcoming</Link>
            <Link href="/live">Live</Link>
            <Link href="/recent">Recent</Link>
            <a className="cta" href="https://t.me/your_bot?start=web_subscribe_tier1" target="_blank" rel="noreferrer">Подписаться в Telegram</a>
          </nav>
        </header>
        <main className="container">{children}</main>
      </body>
    </html>
  );
}



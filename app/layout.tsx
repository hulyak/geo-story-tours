import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Geo-Story Micro-Tours | Discover Cities Through Stories",
  description: "User-created micro-tours with 90-second audio+video clips pinned to locations. Follow curated routes and discover hidden city stories.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}

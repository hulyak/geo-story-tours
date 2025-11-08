import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PocketGuide | AI-Powered Audio Tours",
  description: "Discover cities with AI-generated walking tours. Get personalized 90-second stories at every location, optimized routes, and professional audio guides.",
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

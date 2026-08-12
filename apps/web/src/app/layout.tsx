import type { Metadata } from "next";
import { AuthProvider } from "@/lib/auth-context";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClipMind AI",
  description:
    "Turn a long video into a timestamped transcript, concise AI summary, and explainable key moments.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-clipmind-bg text-clipmind-text antialiased">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}

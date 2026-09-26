import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { AuthProvider } from "@/context/AuthContext";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Bangladesh Crop Intelligence Assistant | AI Agri-Dashboard",
  description:
    "National precision agriculture platform for Bangladesh. Access crop taxonomies, phenological growth stages, pathology management, and agro-ecological zone mapping.",
  keywords: [
    "Bangladesh Agriculture",
    "Crop Intelligence",
    "FastAPI",
    "Supabase",
    "Boro Rice",
    "Aman Rice",
    "Agricultural AI",
  ],
  icons: {
    icon: "/logo.png",
    shortcut: "/logo.png",
    apple: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark scroll-smooth">
      <body className={`${inter.className} bg-[#060907] text-zinc-100 min-h-screen flex flex-col relative selection:bg-emerald-500 selection:text-black`}>
        {/* Ambient background glow effects */}
        <div className="pointer-events-none fixed inset-0 z-0 overflow-hidden">
          <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[500px] w-[800px] rounded-full bg-emerald-500/10 blur-[140px]" />
          <div className="absolute top-1/3 -left-40 h-[400px] w-[500px] rounded-full bg-lime-500/5 blur-[120px]" />
          <div className="absolute bottom-1/4 -right-40 h-[400px] w-[500px] rounded-full bg-emerald-600/5 blur-[120px]" />
        </div>

        <AuthProvider>
          <Navbar />
          <main className="flex-1 relative z-10">{children}</main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}


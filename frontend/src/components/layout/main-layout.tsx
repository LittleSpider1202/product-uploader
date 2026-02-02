"use client";

import { Nav } from "./nav";

interface MainLayoutProps {
  children: React.ReactNode;
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <main className="max-w-7xl mx-auto px-6 py-6">{children}</main>
    </div>
  );
}

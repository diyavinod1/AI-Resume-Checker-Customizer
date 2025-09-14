"use client";

import React from "react";
import { FileText } from "lucide-react";
import useAppLevelAuth from "@/hooks/useAppLevelAuth";
import { createPageUrl } from "@/utils";
import Link from "next/link";

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const { isLoggedIn } = useAppLevelAuth();

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 font-sans antialiased">
      <header className="bg-white border-b border-slate-200 sticky top-0 z-20">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-white shadow-lg">
                <FileText className="h-5 w-5" />
              </div>
              <h1 className="text-xl font-bold text-slate-800">
                ResumeMaster Pro
              </h1>
            </div>
            {!isLoggedIn && (
               <Link
                  href={createPageUrl('login')}
                  className="inline-flex justify-center items-center py-2 px-4 rounded-lg text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 transition-all duration-200"
                >
                  Sign In
                </Link>
            )}
          </div>
        </div>
      </header>
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}

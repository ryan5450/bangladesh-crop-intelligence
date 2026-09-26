"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { motion } from "framer-motion";
import { Lock, Mail, ShieldCheck, AlertCircle, ArrowRight, Sprout, Loader2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAdmin, user } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // If already logged in as admin, can quickly redirect
  React.useEffect(() => {
    if (user && isAdmin) {
      router.push("/agri-control-panel/dashboard");
    }
  }, [user, isAdmin, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!email || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    try {
      const result = await login(email.trim(), password);
      if (result.success) {
        router.push("/agri-control-panel/dashboard");
      } else {
        setErrorMessage(result.error || "Authentication failed. Verify credentials.");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to log in. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative min-h-[85vh] flex items-center justify-center px-4 py-16">
      {/* Background ambient radial gradients */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-96 w-96 rounded-full bg-emerald-500/10 blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative w-full max-w-md"
      >
        {/* Header Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 mb-4 shadow-glow">
            <Sprout className="h-7 w-7" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white">
            Admin Control Panel
          </h1>
          <p className="mt-2 text-sm text-zinc-400">
            Sign in with authorized credentials to manage crops and images
          </p>
        </div>

        {/* Glass Card */}
        <div className="glass-panel rounded-2xl p-8 border border-white/[0.08] shadow-2xl relative overflow-hidden">
          {/* Top Emerald Accent Glow */}
          <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />

          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-6 rounded-xl bg-red-500/10 border border-red-500/30 p-4 text-xs text-red-300 flex items-start gap-3"
            >
              <AlertCircle className="h-4 w-4 shrink-0 text-red-400 mt-0.5" />
              <div>
                <p className="font-semibold text-red-200">Authentication Failed</p>
                <p className="mt-0.5 leading-relaxed">{errorMessage}</p>
              </div>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email Field */}
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1.5 uppercase tracking-wider">
                Admin Email
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Mail className="h-4 w-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="user@example.com"
                  className="w-full rounded-xl bg-black/40 border border-white/[0.1] pl-10 pr-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-xs font-medium text-zinc-300 mb-1.5 uppercase tracking-wider">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-zinc-500">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full rounded-xl bg-black/40 border border-white/[0.1] pl-10 pr-4 py-2.5 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-black font-semibold py-3 px-4 text-sm transition-all shadow-glow hover:shadow-glow-lg disabled:opacity-50 disabled:cursor-not-allowed mt-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Verifying Credentials...</span>
                </>
              ) : (
                <>
                  <span>Sign In</span>
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </form>

          {/* Security Assurance Footer */}
          <div className="mt-6 pt-5 border-t border-white/[0.06] flex items-center justify-between text-xs text-zinc-500">
            <div className="flex items-center gap-1.5">
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
              <span>Encrypted Authentication</span>
            </div>
            <Link
              href="/"
              className="hover:text-zinc-300 transition-colors"
            >
              Back to Home
            </Link>
          </div>
        </div>

        {/* First Time Admin Guidance */}
        <div className="mt-6 text-center text-xs text-zinc-500">
          <p>
            Authorized agricultural personnel and administrators only.
          </p>
        </div>
      </motion.div>
    </div>
  );
}


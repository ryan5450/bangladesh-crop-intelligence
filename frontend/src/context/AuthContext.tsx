"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { Session, User } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabaseClient";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  isAdmin: boolean;
  role: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  getToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  isAdmin: false,
  role: null,
  loading: true,
  error: null,
  login: async () => ({ success: false }),
  logout: async () => {},
  getToken: async () => null,
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [role, setRole] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const checkAdminRole = async (userId: string): Promise<boolean> => {
    try {
      const { data, error: adminErr } = await supabase
        .from("admins")
        .select("role")
        .eq("user_id", userId)
        .maybeSingle();

      if (adminErr) {
        console.warn("[Auth] Admins table check error:", adminErr.message);
        // If admins table is not yet created, allow login for initial setup preview
        if (adminErr.message.includes("does not exist") || adminErr.code === "PGRST205") {
          console.warn("[Auth] Admins table not yet created in Supabase. Granting temporary access for setup.");
          setIsAdmin(true);
          setRole("admin");
          return true;
        }
        setIsAdmin(false);
        setRole(null);
        return false;
      }

      if (data && data.role === "admin") {
        setIsAdmin(true);
        setRole("admin");
        return true;
      } else {
        setIsAdmin(false);
        setRole(data?.role || null);
        return false;
      }
    } catch (err: any) {
      console.error("[Auth] Role verification exception:", err);
      setIsAdmin(false);
      return false;
    }
  };

  useEffect(() => {
    let mounted = true;

    async function initAuth() {
      try {
        const { data: { session: initialSession } } = await supabase.auth.getSession();
        if (mounted) {
          setSession(initialSession);
          setUser(initialSession?.user ?? null);
          if (initialSession?.user) {
            await checkAdminRole(initialSession.user.id);
          } else {
            setIsAdmin(false);
            setRole(null);
          }
          setLoading(false);
        }
      } catch (err: any) {
        if (mounted) {
          console.error("[Auth] Failed to get session:", err);
          setLoading(false);
        }
      }
    }

    initAuth();

    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (_event, newSession) => {
        if (!mounted) return;
        setSession(newSession);
        setUser(newSession?.user ?? null);
        if (newSession?.user) {
          await checkAdminRole(newSession.user.id);
        } else {
          setIsAdmin(false);
          setRole(null);
        }
        setLoading(false);
      }
    );

    return () => {
      mounted = false;
      subscription.unsubscribe();
    };
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setError(null);
    try {
      const { data, error: signInError } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (signInError) {
        setError(signInError.message);
        return { success: false, error: signInError.message };
      }

      if (!data.user) {
        setError("User authentication failed.");
        return { success: false, error: "User authentication failed." };
      }

      setUser(data.user);
      setSession(data.session);

      const hasAdmin = await checkAdminRole(data.user.id);
      if (!hasAdmin) {
        const msg = "Access Denied. Your account does not have administrator privileges in the 'admins' table.";
        setError(msg);
        return { success: false, error: msg };
      }

      return { success: true };
    } catch (err: any) {
      const msg = err.message || "An unexpected error occurred during login.";
      setError(msg);
      return { success: false, error: msg };
    }
  };

  const logout = async () => {
    try {
      await supabase.auth.signOut();
      setUser(null);
      setSession(null);
      setIsAdmin(false);
      setRole(null);
      setError(null);
    } catch (err) {
      console.error("[Auth] Logout error:", err);
    }
  };

  const getToken = async (): Promise<string | null> => {
    if (session?.access_token) {
      return session.access_token;
    }
    const { data } = await supabase.auth.getSession();
    return data.session?.access_token ?? null;
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        session,
        isAdmin,
        role,
        loading,
        error,
        login,
        logout,
        getToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}


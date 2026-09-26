"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AdminRootRedirect() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/agri-control-panel/dashboard");
  }, [router]);

  return null;
}


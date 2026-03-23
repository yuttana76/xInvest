"use client";

import * as React from "react";
import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/Button";

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = React.useState(false);

  // Avoid hydration mismatch
  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <Button variant="outline" size="sm" className="w-9 h-9 p-0 opacity-0">
        <Sun size={18} />
      </Button>
    );
  }

  return (
    <Button
      variant="outline"
      size="sm"
      className="w-9 h-9 p-0 border-white/10 dark:hover:bg-white/5 transition-colors"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
      aria-label="Toggle theme"
    >
      {theme === "dark" ? (
        <Sun size={18} className="text-secondary" />
      ) : (
        <Moon size={18} className="text-accent" />
      )}
    </Button>
  );
}

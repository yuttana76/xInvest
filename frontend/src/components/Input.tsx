import React from 'react';
import { cn } from '@/utils/cn';

export const Input: React.FC<React.ComponentPropsWithoutRef<'input'>> = ({ className, ...props }) => {
  return (
    <input
      className={cn(
        "flex h-11 w-full rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm text-white ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/20 focus-visible:ring-offset-0 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200",
        className
      )}
      {...props}
    />
  );
};

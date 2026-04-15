'use client';

import React from 'react';
import { Button } from './Button';
import { ThemeToggle } from './ThemeToggle';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import { User, LogOut } from 'lucide-react';
import { LogoutConfirmModal } from './LogoutConfirmModal';

export const Navbar: React.FC = () => {
    const { isAuthenticated, user, logout } = useAuth();
    const [isLogoutModalOpen, setIsLogoutModalOpen] = React.useState(false);

    const handleLogout = () => {
        setIsLogoutModalOpen(false);
        logout();
    };
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border transition-colors duration-300">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-20">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20 rotate-12">
                            <span className="text-white font-bold text-2xl -rotate-12">x</span>
                        </div>
                        <span className="text-2xl font-bold tracking-tight text-foreground transition-colors">Invest</span>
                    </Link>

                    <div className="hidden md:flex items-center gap-8">
                        {isAuthenticated && user?.role === 'admin' ? (
                            <Link href="/admin-portal" className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">Admin Portal</Link>
                        ) : isAuthenticated && user?.role === 'operator' ? (
                            <Link href="/operator" className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">Portal</Link>
                        ) : isAuthenticated && (user?.role === 'marketing' || user?.role === 'agent') ? (
                            <Link href={`/${user.role}`} className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">Dashboard</Link>
                        ) : isAuthenticated && user?.role === 'investor' ? (
                            <Link href="/dashboard" className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">Dashboard</Link>
                        ) : null}
                        {/* <Link href="/" className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">Home</Link> */}
                        {!isAuthenticated && (
                            <>
                                <Link href="/discovery" className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">Discovery</Link>
                                <Link href="/about" className="text-sm font-medium text-slate-500 dark:text-slate-400 hover:text-foreground transition-colors">About X</Link>
                            </>
                        )}
                    </div>

                    <div className="flex items-center gap-4">
                        <ThemeToggle />
                        {!isAuthenticated ? (
                            <>
                                <Link href="/login">
                                    <Button variant="ghost" size="sm" className="hidden sm:inline-flex">Log in</Button>
                                </Link>
                                <Button size="sm">Get Started</Button>
                            </>
                        ) : (
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10">
                                    <User className="w-4 h-4 text-primary" />
                                    <span className="text-sm font-medium text-slate-600 dark:text-slate-300">{user?.username}</span>
                                </div>
                                <Button variant="ghost" size="icon" onClick={() => setIsLogoutModalOpen(true)} title="Logout">
                                    <LogOut className="w-5 h-5 text-slate-500 hover:text-red-400 transition-colors" />
                                </Button>
                                <LogoutConfirmModal 
                                    isOpen={isLogoutModalOpen} 
                                    onClose={() => setIsLogoutModalOpen(false)} 
                                    onConfirm={handleLogout} 
                                />
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};

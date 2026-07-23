'use client';

import React, { useEffect, useState } from 'react';
import { LayoutDashboard, Users, Settings, BarChart3, LogOut, ClipboardList, Inbox as InboxIcon, Menu, X } from 'lucide-react';
import { cn } from '@/utils/cn';
import { useAuth } from '@/hooks/useAuth';
import { LogoutConfirmModal } from './LogoutConfirmModal';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { APP_NAME_BADGE } from '@/lib/branding';

interface SidebarItemProps {
  icon: React.ReactNode;
  label: string;
  href: string;
  onNavigate?: () => void;
}

const SidebarItem = ({ icon, label, href, onNavigate }: SidebarItemProps) => {
  const pathname = usePathname();
  const active = pathname === href;

  return (
    <Link href={href} onClick={onNavigate}>
      <div className={cn(
        "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 cursor-pointer group",
        active ? "bg-primary text-white shadow-lg shadow-emerald-500/20" : "text-slate-400 hover:bg-white/5 hover:text-white"
      )}>
        <span className={cn("transition-transform group-hover:scale-110", active ? "text-white" : "text-slate-400")}>
          {icon}
        </span>
        <span className="font-medium text-sm">{label}</span>
      </div>
    </Link>
  );
};

export const Sidebar: React.FC = () => {
  const { user, logout, hasRole } = useAuth();
  const [isLogoutModalOpen, setIsLogoutModalOpen] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const pathname = usePathname();

  // Close the mobile drawer whenever the route changes (link click, back/forward, etc.)
  useEffect(() => {
    setIsMobileOpen(false);
  }, [pathname]);

  const handleLogout = () => {
    setIsLogoutModalOpen(false);
    logout();
  };

  const getMenuItems = () => {
    const workflowItems = [
      { icon: <ClipboardList size={20} />, label: "My Requests", href: "/workflow/my-requests" },
      { icon: <InboxIcon size={20} />, label: "Approval Inbox", href: "/workflow/inbox" },
    ];

    console.log("this is role", user?.role)

    if (hasRole('admin')) {
      return [
        { icon: <LayoutDashboard size={20} />, label: "Overview", href: "/admin-portal" },
        ...workflowItems,
      ];
    } else if (hasRole('operator')) {
      return [
        { icon: <LayoutDashboard size={20} />, label: "Dashboard", href: "/operator/dashboard" },
        // { icon: <Users size={20} />, label: "Customers", href: "/operator/customers" },
        // { icon: <BarChart3 size={20} />, label: "Reports", href: "/operator/reports" },
        ...workflowItems,
      ];
    } 
    else if (hasRole('marketing')) {
      return [
        { icon: <LayoutDashboard size={20} />, label: "Dashboard", href: "/marketing/dashboard" },
        // { icon: <Users size={20} />, label: "My Investors", href: "/marketing/investors" },
        ...workflowItems,
      ];
    } 
    // else if (hasRole('agent')) {
    //   return [
    //     { icon: <LayoutDashboard size={20} />, label: "Performance", href: "/agent/dashboard" },
    //     { icon: <Users size={20} />, label: "My Clients", href: "/agent/investors" },
    //     ...workflowItems,
    //   ];
    // } 
    else {
    return [
        // { icon: <LayoutDashboard size={20} />, label: "Overview", href: "/admin-portal" },
        // { icon: <Users size={20} />, label: "Customers", href: "/admin-portal/customers" },
        // { icon: <Settings size={20} />, label: "Settings", href: "/admin-portal/settings" },
        ...workflowItems,
      ];
    }
  };

  const menuItems = getMenuItems();

  const getPortalName = () => {
    if (hasRole('operator')) return 'Operator';
    if (hasRole('marketing')) return 'Marketing';
    if (hasRole('agent')) return 'Agent';
    return 'Admin';
  };

  return (
    <>
      {/* Mobile/tablet hamburger toggle — hidden on desktop where the sidebar is always visible */}
      <button
        type="button"
        onClick={() => setIsMobileOpen(true)}
        aria-label="Open menu"
        className="fixed top-24 left-4 z-40 lg:hidden flex items-center justify-center w-10 h-10 rounded-xl glass border border-white/5 text-slate-300"
      >
        <Menu size={20} />
      </button>

      {/* Backdrop — closes the drawer on tap, only rendered while open on mobile/tablet */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      <aside className={cn(
        "w-64 h-screen glass border-r border-white/5 fixed left-0 top-0 flex flex-col p-6 overflow-y-auto z-50",
        "transition-transform duration-300 lg:translate-x-0",
        isMobileOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex items-center justify-between gap-2 mb-10 px-2 shrink-0">
          <Link href="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center rotate-12">
                  <span className="text-white font-bold text-lg -rotate-12">{APP_NAME_BADGE}</span>
              </div>
              <span className="text-xl font-bold tracking-tight">
                  {getPortalName()}
              </span>
          </Link>
          <button
            type="button"
            onClick={() => setIsMobileOpen(false)}
            aria-label="Close menu"
            className="lg:hidden text-slate-400 hover:text-white p-1"
          >
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 space-y-2">
          {menuItems.map((item, idx) => (
              <SidebarItem key={idx} {...item} onNavigate={() => setIsMobileOpen(false)} />
          ))}
        </div>

        <div className="pt-6 border-t border-white/5 mt-auto shrink-0">
          <div
              onClick={() => setIsLogoutModalOpen(true)}
              className="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-all duration-200 cursor-pointer"
          >
              <LogOut size={20} />
              <span className="font-medium text-sm">Log out</span>
          </div>
        </div>

        <LogoutConfirmModal
          isOpen={isLogoutModalOpen}
          onClose={() => setIsLogoutModalOpen(false)}
          onConfirm={handleLogout}
      />
      </aside>
    </>
  );
};

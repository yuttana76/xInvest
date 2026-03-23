'use client';

import React from 'react';
import { Button } from './Button';
import { LogOut, X } from 'lucide-react';

interface LogoutConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
}

export const LogoutConfirmModal: React.FC<LogoutConfirmModalProps> = ({ isOpen, onClose, onConfirm }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-100 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm animate-in fade-in duration-300" 
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-sm glass border border-white/10 rounded-3xl p-8 shadow-2xl animate-in zoom-in-95 fade-in duration-300">
        <button 
          onClick={onClose}
          className="absolute right-4 top-4 p-2 text-slate-500 hover:text-white transition-colors"
        >
          <X size={20} />
        </button>

        <div className="text-center">
          <div className="w-16 h-16 bg-red-500/10 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <LogOut className="text-red-500 w-8 h-8" />
          </div>
          
          <h3 className="text-xl font-bold text-white mb-2">Sign Out</h3>
          <p className="text-slate-400 mb-8">
            Are you sure you want to sign out of your account? You will need to verify your OTP again to sign back in.
          </p>

          <div className="flex flex-col gap-3">
            <Button 
              variant="primary" 
              className="bg-red-500 hover:bg-red-600 shadow-red-500/20"
              onClick={onConfirm}
            >
              Confirm Sign Out
            </Button>
            <Button 
              variant="ghost" 
              onClick={onClose}
            >
              Cancel
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const roleColors: Record<string, string> = {
  admin: 'bg-red-900/60 text-red-300',
  developer: 'bg-blue-900/60 text-blue-300',
  viewer: 'bg-gray-700 text-gray-300',
};

export default function ProfileMenu() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  if (!user) return null;

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <div className="px-4 py-3 border-t border-gray-800">
      <div className="flex items-center gap-2 mb-2">
        <div className="flex-1 min-w-0">
          <p className="text-xs text-white font-medium truncate">{user.email}</p>
          <span className={`inline-block mt-0.5 text-[10px] px-1.5 py-0.5 rounded-full font-medium ${roleColors[user.role] ?? roleColors.viewer}`}>
            {user.role}
          </span>
        </div>
      </div>
      <button
        onClick={handleLogout}
        className="flex w-full items-center gap-2 text-xs text-gray-500 hover:text-red-400 transition-colors"
      >
        <LogOut size={13} /> Sign out
      </button>
    </div>
  );
}

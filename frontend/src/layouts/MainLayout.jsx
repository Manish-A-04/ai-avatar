import React from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { LogOut, User } from "lucide-react";
import { Button } from "../components/ui/Button";

export const MainLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const isAuthPage = location.pathname === "/login" || location.pathname === "/register";

  return (
    <div className="min-h-screen flex flex-col bg-black text-white selection:bg-white selection:text-black">
      {!isAuthPage && (
        <header className="border-b border-[#333333] sticky top-0 bg-black/80 backdrop-blur-md z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2 font-semibold text-lg tracking-tight">
              <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center text-black">
                A
              </div>
              Avatar.ai
            </div>
            {user && (
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <User size={16} />
                  <span>{user.username}</span>
                </div>
                <Button variant="ghost" size="icon" onClick={handleLogout} title="Logout">
                  <LogOut size={18} />
                </Button>
              </div>
            )}
          </div>
        </header>
      )}

      <main className="flex-1 flex flex-col relative">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-96 bg-white/[0.02] blur-[120px] rounded-full pointer-events-none" />
        <div className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 z-10">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

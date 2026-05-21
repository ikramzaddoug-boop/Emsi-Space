import { Link } from "@tanstack/react-router";
import { FiLogIn, FiUserPlus } from "react-icons/fi";
import { EmsiLogo } from "./EmsiLogo";

export function LandingNavbar({ isDark }: { isDark: boolean }) {
  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 backdrop-blur-md border-b transition-all duration-700 ease-in-out ${isDark ? 'bg-gray-950/80 border-gray-900' : 'bg-gray-100/80 border-gray-300'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-3 group">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-xl blur-lg opacity-30 group-hover:opacity-50 transition-opacity duration-300 ease-in-out" />
              <EmsiLogo size={40} />
            </div>
            <span className={`text-2xl font-bold transition-colors duration-300 ease-in-out ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>EmsiSpace</span>
          </Link>

          {/* Boutons Login/Register */}
          <div className="flex items-center gap-3">
            <Link
              to="/login"
              className={`flex items-center gap-2 px-5 py-2.5 font-medium rounded-xl transition-all duration-300 ease-in-out ${isDark ? 'text-gray-200 hover:bg-gray-900/50 border border-transparent hover:border-gray-700' : 'text-gray-700 hover:bg-gray-200 border border-transparent hover:border-gray-400'}`}
            >
              <FiLogIn className="size-4" />
              Connexion
            </Link>
            <Link
              to="/register"
              className="flex items-center gap-2 px-5 py-2.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium rounded-xl hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 ease-in-out shadow-md shadow-purple-600/20"
            >
              <FiUserPlus className="size-4" />
              Inscription
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}

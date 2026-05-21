import { createFileRoute, Link } from "@tanstack/react-router";
import { LandingNavbar } from "../components/LandingNavbar";
import { FiArrowRight, FiHome, FiZap, FiUsers, FiShield, FiCalendar, FiTrendingUp } from "react-icons/fi";
import { useState, useEffect } from "react";
import { EmsiLogo } from "../components/EmsiLogo";

export const Route = createFileRoute("/")({
  component: LandingPage,
});

function LandingPage() {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDark(mediaQuery.matches);
    const handler = (e: MediaQueryListEvent) => setIsDark(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  return (
    <div className={`min-h-screen transition-all duration-700 ease-in-out ${isDark ? 'bg-gray-950' : 'bg-gray-100'}`}>
      <LandingNavbar isDark={isDark} />
      
      {/* Hero Section */}
      <div className="relative pt-20">
        <div className="max-w-6xl mx-auto px-6 py-20">
          <div className="max-w-3xl">
            {/* Logo */}
            <div className="flex items-center gap-3 mb-8">
              <EmsiLogo size={48} />
              <h1 className={`text-4xl font-black tracking-tight ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
                EmsiSpace
              </h1>
            </div>

            {/* Title */}
            <h2 className={`text-5xl md:text-6xl font-black leading-tight mb-6 ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
              Réservez vos salles
              <span className={`block ${isDark ? 'text-purple-300' : 'text-purple-700'}`}>
                & équipements
              </span>
            </h2>

            {/* Subtitle */}
            <p className={`text-xl mb-10 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Plateforme moderne de réservation pour établissements d'enseignement
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/register"
                className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 ease-in-out flex items-center justify-center gap-2 shadow-lg"
              >
                Commencer
                <FiArrowRight className="size-5" />
              </Link>
              <Link
                to="/login"
                className={`px-8 py-4 font-bold rounded-lg border-2 flex items-center justify-center gap-2 transition-all duration-300 ease-in-out ${isDark ? 'bg-gray-900/50 text-gray-200 border-gray-700 hover:bg-gray-900/70 hover:border-gray-600' : 'bg-gray-200 text-gray-800 border-gray-300 hover:bg-gray-300 hover:border-gray-400'}`}
              >
                Se connecter
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className={`py-20 px-6 transition-all duration-700 ease-in-out ${isDark ? 'bg-gray-900' : 'bg-gray-200'}`}>
        <div className="max-w-6xl mx-auto">
          <div className="mb-12">
            <h3 className={`text-3xl font-black mb-3 ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
              Fonctionnalités
            </h3>
            <p className={`text-lg ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
              Tout ce dont vous avez besoin
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: FiHome, title: 'Salles', desc: 'Réservez facilement vos salles' },
              { icon: FiZap, title: 'IA', desc: 'Détection automatique des conflits' },
              { icon: FiUsers, title: 'Multi-rôles', desc: 'Admin, prof, étudiant' },
              { icon: FiShield, title: 'Validation', desc: 'Validation en temps réel' },
              { icon: FiCalendar, title: 'Équipements', desc: 'Gestion du matériel' },
              { icon: FiTrendingUp, title: 'Analytics', desc: 'Statistiques avancées' }
            ].map((feature, i) => (
              <div key={i} className={`p-6 rounded-xl border transition-all duration-300 ease-in-out hover:scale-[1.02] ${isDark ? 'bg-gray-950/50 border-gray-800 hover:border-gray-700' : 'bg-gray-100 border-gray-300 hover:border-gray-400'}`}>
                <div className={`size-12 bg-gradient-to-br from-purple-600 to-indigo-600 rounded-lg flex items-center justify-center text-white mb-4 shadow-md`}>
                  <feature.icon className="size-6" />
                </div>
                <h4 className={`text-lg font-bold mb-2 ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
                  {feature.title}
                </h4>
                <p className={`text-sm ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {feature.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className={`py-20 px-6 transition-all duration-700 ease-in-out ${isDark ? 'bg-gray-950' : 'bg-gray-100'}`}>
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { value: '120+', label: 'Salles' },
              { value: '2.4k', label: 'Utilisateurs' },
              { value: '8k', label: 'Réservations' }
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className={`text-5xl font-black mb-2 ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>{stat.value}</div>
                <div className={`text-sm font-medium uppercase tracking-wider ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className={`py-20 px-6 transition-all duration-700 ease-in-out ${isDark ? 'bg-gray-900' : 'bg-gray-200'}`}>
        <div className="max-w-3xl mx-auto text-center">
          <h3 className={`text-3xl font-black mb-4 ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>
            Prêt à commencer ?
          </h3>
          <p className={`text-lg mb-8 ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
            Rejoignez des milliers d'utilisateurs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-bold rounded-lg hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 ease-in-out shadow-lg"
            >
              Créer un compte
            </Link>
            <Link
              to="/login"
              className={`px-8 py-4 font-bold rounded-lg border-2 transition-all duration-300 ease-in-out ${isDark ? 'bg-gray-900/50 text-gray-200 border-gray-700 hover:bg-gray-900/70 hover:border-gray-600' : 'bg-gray-200 text-gray-800 border-gray-300 hover:bg-gray-300 hover:border-gray-400'}`}
            >
              Se connecter
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className={`py-12 px-6 transition-all duration-700 ease-in-out ${isDark ? 'bg-gray-950 border-t border-gray-900' : 'bg-gray-100 border-t border-gray-300'}`}>
        <div className="max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <EmsiLogo size={32} />
            <span className={`text-xl font-black ${isDark ? 'text-gray-100' : 'text-gray-800'}`}>EmsiSpace</span>
          </div>
          <p className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-600'}`}>
            © 2026 EmsiSpace. Tous droits réservés.
          </p>
        </div>
      </div>
    </div>
  );
}

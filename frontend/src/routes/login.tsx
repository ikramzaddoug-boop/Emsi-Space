import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { EmsiLogo } from "../components/EmsiLogo";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/dashboard/Toast";
import { FiUser, FiLock, FiArrowRight } from "react-icons/fi";

export const Route = createFileRoute("/login")({ component: Login });

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(username, password);
      toast.push({ type: "success", msg: "Connexion réussie !" });
      
      // On laisse le AuthContext gérer l'utilisateur et on redirige selon son rôle réel
      if (user.role === "admin") navigate({ to: "/admin/dashboard" });
      else if (user.role === "professeur") navigate({ to: "/professor/dashboard" });
      else navigate({ to: "/student/dashboard" });
    } catch (err) {
      toast.push({ type: "error", msg: "Identifiants invalides" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex font-sans bg-white">
      {/* Design conservé - Panel Gauche */}
      <div className="hidden lg:flex w-1/2 bg-gradient-to-br from-[#6366f1] via-[#8b5cf6] to-[#a855f7] p-12 flex-col justify-between text-white relative overflow-hidden">
        <div className="absolute top-[-10%] right-[-10%] w-64 h-64 bg-white/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-[-5%] left-[-5%] w-96 h-96 bg-blue-400/20 rounded-full blur-3xl"></div>

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-16">
            <EmsiLogo size={40} />
            <span className="text-2xl font-extrabold tracking-tight">EmsiSpace</span>
          </div>
          <h1 className="text-5xl font-black leading-[1.1] mb-6 max-w-md">Réservez vos salles & équipements en quelques clics.</h1>
          <p className="text-white/80 text-lg max-w-md font-medium">Une plateforme moderne pour administrateurs, professeurs et étudiants.</p>
        </div>

        <div className="grid grid-cols-3 gap-4 relative z-10">
          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/20 shadow-xl">
            <div className="text-3xl font-black mb-1">120+</div>
            <div className="text-xs font-bold uppercase tracking-wider text-white/60">Salles</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/20 shadow-xl">
            <div className="text-3xl font-black mb-1">2.4k</div>
            <div className="text-xs font-bold uppercase tracking-wider text-white/60">Utilisateurs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md p-5 rounded-2xl border border-white/20 shadow-xl">
            <div className="text-3xl font-black mb-1">8k</div>
            <div className="text-xs font-bold uppercase tracking-wider text-white/60">Réservations/mois</div>
          </div>
        </div>

        <div className="text-white/40 text-xs font-medium relative z-10">© 2026 EmsiSpace. Tous droits réservés.</div>
      </div>

      {/* Formulaire - Logique Restaurée (Username) */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50/30">
        <div className="w-full max-w-md animate-fade-in">
          <div className="mb-10">
            <h2 className="text-4xl font-black text-gray-900 mb-2">Connexion</h2>
            <p className="text-gray-500 font-medium">Accédez à votre espace EmsiSpace.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Username</label>
              <div className="relative group">
                <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                <input 
                  type="text" 
                  className="w-full bg-gray-100/80 border-none rounded-xl py-4 pl-12 pr-4 font-medium text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none shadow-sm"
                  placeholder="Votre nom d'utilisateur"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-bold text-gray-700 uppercase tracking-wider">Mot de passe</label>
                <Link to="/forgot-password" className="text-xs font-bold text-indigo-600">Oublié ?</Link>
              </div>
              <div className="relative group">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                <input 
                  type="password" 
                  className="w-full bg-gray-100/80 border-none rounded-xl py-4 pl-12 pr-4 font-medium text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none shadow-sm"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-4 rounded-xl shadow-lg shadow-indigo-600/30 transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 mt-4 disabled:opacity-50">
              {loading ? "Chargement..." : "Se connecter"}
              <FiArrowRight />
            </button>
          </form>

          <div className="mt-12 text-center text-sm space-y-2">
            <span className="text-gray-500 font-medium">Pas de compte ? </span>
            <Link to="/register" className="font-bold text-indigo-600 hover:text-indigo-700">Créer un compte</Link>
            <div>
              <Link to="/" className="text-gray-400 hover:text-gray-600 font-medium">← Retour à l'accueil</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../components/dashboard/Toast";
import { FiMail, FiLock, FiUser, FiArrowRight } from "react-icons/fi";
import { EmsiLogo } from "../components/EmsiLogo";

export const Route = createFileRoute("/register")({ component: Register });

function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("etudiant");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(name, email, password, role);
      toast.push({ type: "success", msg: "Compte créé ! Connectez-vous." });
      navigate({ to: "/login" });
    } catch (err: any) {
      const data = err?.response?.data;
      let msg = "Erreur lors de l'inscription";
      if (data) {
        // Extract first error message from Django's response
        const firstKey = Object.keys(data)[0];
        if (firstKey && Array.isArray(data[firstKey])) {
          msg = `${firstKey}: ${data[firstKey][0]}`;
        } else if (typeof data === 'string') {
          msg = data;
        }
      }
      toast.push({ type: "error", msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex font-sans bg-white">
      {/* Design - Panel Gauche */}
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

      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50/30">
        <div className="w-full max-w-md animate-fade-in">
          <div className="mb-10">
            <h2 className="text-4xl font-black text-gray-900 mb-2">Créer un compte</h2>
            <p className="text-gray-500 font-medium">Rejoignez EmsiSpace en quelques secondes.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Nom complet</label>
              <div className="relative group">
                <FiUser className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                <input type="text" className="w-full bg-gray-100/80 border-none rounded-xl py-3.5 pl-12 pr-4 font-medium text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none shadow-sm" placeholder="Nom Complet" value={name} onChange={(e) => setName(e.target.value)} required />
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Email</label>
              <div className="relative group">
                <FiMail className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                <input type="email" className="w-full bg-gray-100/80 border-none rounded-xl py-3.5 pl-12 pr-4 font-medium text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none shadow-sm" placeholder="Nom@gmail.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
              </div>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Mot de passe</label>
              <div className="relative group">
                <FiLock className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                <input type="password" className="w-full bg-gray-100/80 border-none rounded-xl py-3.5 pl-12 pr-4 font-medium text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none shadow-sm" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} required />
              </div>
            </div>

            <div>
               <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wider">Rôle</label>
               <select className="w-full bg-gray-100/80 border-none rounded-xl py-3.5 px-4 font-medium text-gray-900 focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all outline-none shadow-sm" value={role} onChange={(e) => setRole(e.target.value)}>
                  <option value="etudiant">Étudiant</option>
                  <option value="professeur">Professeur</option>
               </select>
            </div>

            <button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-black py-4 rounded-xl shadow-lg shadow-indigo-600/30 transition-all transform active:scale-[0.98] flex items-center justify-center gap-2 mt-4 disabled:opacity-50">
              {loading ? "Création..." : "Créer mon compte"}
              <FiArrowRight />
            </button>
          </form>

          <div className="mt-10 text-center text-sm space-y-2">
            <span className="text-gray-500 font-medium">Déjà un compte ? </span>
            <Link to="/login" className="font-bold text-indigo-600 hover:text-indigo-700">Se connecter</Link>
            <div>
              <Link to="/" className="text-gray-400 hover:text-gray-600 font-medium">← Retour à l'accueil</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

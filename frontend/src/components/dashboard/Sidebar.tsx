import { Link, useLocation } from "@tanstack/react-router";
import { 
  FiHome, FiGrid, FiBox, FiCalendar, FiUsers, FiBarChart2, FiSettings, FiLogOut 
} from "react-icons/fi";
import { useAuth } from "@/context/AuthContext";
import type { Role } from "@/lib/mockData";
import { EmsiLogo } from "@/components/EmsiLogo";

const navByRole: Record<Role, { to: string; label: string; icon: any }[]> = {
  admin: [
    { to: "/admin/dashboard", label: "Tableau de bord", icon: FiHome },
    { to: "/admin/salles", label: "Salles", icon: FiGrid },
    { to: "/admin/equipment", label: "Équipements", icon: FiBox },
    { to: "/admin/reservations", label: "Réservations", icon: FiCalendar },
    { to: "/admin/users", label: "Utilisateurs", icon: FiUsers },
    { to: "/admin/analytics", label: "Analytique", icon: FiBarChart2 },
  ],
  professeur: [
    { to: "/professor/dashboard", label: "Tableau de bord", icon: FiHome },
    { to: "/professor/salles", label: "Salles", icon: FiGrid },
    { to: "/professor/equipment", label: "Matériel", icon: FiBox },
    { to: "/professor/reservations", label: "Mes Réservations", icon: FiCalendar },
  ],
  etudiant: [
    { to: "/student/dashboard", label: "Tableau de bord", icon: FiHome },
    { to: "/student/salles", label: "Salles", icon: FiGrid },
    { to: "/student/equipment", label: "Matériel", icon: FiBox },
    { to: "/student/reservations", label: "Mes Réservations", icon: FiCalendar },
  ],
};

export function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const nav = user ? navByRole[user.role] : [];

  return (
    <>
      {open && (
        <div className="fixed inset-0 z-40 bg-black/50 lg:hidden" onClick={onClose} />
      )}
      <aside className={`fixed top-0 left-0 z-50 h-full w-64 bg-[var(--sidebar-bg)] transition-transform duration-300 lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
        <div className="flex flex-col h-full py-6 px-4">
          <div className="flex items-center gap-3 px-4 mb-10">
            <EmsiLogo size={40} dark />
            <div>
              <h2 className="font-bold text-lg tracking-tight text-white">EmsiSpace</h2>
              <span className="text-[10px] uppercase tracking-widest text-gray-500 font-bold">{user?.role}</span>
            </div>
          </div>

          <nav className="flex-1 space-y-1">
            {nav.map((item) => {
              const active = location.pathname.startsWith(item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to as any}
                  onClick={onClose}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                    active ? "bg-[var(--sidebar-active-bg)] text-white" : "text-gray-400 hover:bg-[var(--sidebar-active-bg)] hover:text-white"
                  }`}
                >
                  <item.icon className="size-5" />
                  {item.label}
                </Link>
              );
            })}
          </nav>

          <div className="pt-6 border-t border-gray-800 space-y-1">
            {user?.role !== 'admin' && (
              <Link to={`/${user?.role === 'professeur' ? 'professor' : 'student'}/profile` as any} className="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-gray-400 hover:bg-[#1f2937] hover:text-white">
                <FiSettings className="size-5" /> Mon Profil
              </Link>
            )}
            <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-red-500 hover:bg-red-500/10">
              <FiLogOut className="size-5" /> Déconnexion
            </button>
          </div>
        </div>
      </aside>
    </>
  );
}

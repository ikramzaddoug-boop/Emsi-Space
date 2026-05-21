import type { ReactNode } from "react";
import { EmsiLogo } from "../EmsiLogo";

export function AuthShell({ title, subtitle, children, footer }: { title: string; subtitle?: string; children: ReactNode; footer?: ReactNode }) {
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

      {/* Formulaire - Panel Droit */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-gray-50/30">
        <div className="w-full max-w-md animate-fade-in">
          <div className="mb-10">
            <h2 className="text-4xl font-black text-gray-900 mb-2">{title}</h2>
            {subtitle && <p className="text-gray-500 font-medium">{subtitle}</p>}
          </div>

          <div className="space-y-6">
            {children}
          </div>

          {footer && <div className="mt-12 text-center text-sm">{footer}</div>}
        </div>
      </div>
    </div>
  );
}

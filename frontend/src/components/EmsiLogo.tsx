/**
 * EmsiLogo — replaces the plain "S" icon with the EMSI brand logo.
 * Renders as an SVG so it's crisp at any size and needs no image file.
 *
 * Props:
 *   size  — pixel size of the square container (default 40)
 *   dark  — use dark background variant (for sidebar), default false (transparent/white)
 */
interface EmsiLogoProps {
  size?: number;
  dark?: boolean;
}

export function EmsiLogo({ size = 40, dark = false }: EmsiLogoProps) {
  return (
    <div
      style={{ width: size, height: size, minWidth: size }}
      className={`rounded-xl flex items-center justify-center overflow-hidden shadow-lg ${
        dark ? "bg-[#1e1b4b]" : "bg-white/20 backdrop-blur-md border border-white/30"
      }`}
    >
      <svg
        viewBox="0 0 100 100"
        width={size * 0.82}
        height={size * 0.82}
        xmlns="http://www.w3.org/2000/svg"
        aria-label="EMSI logo"
      >
        {/* ── Purple silhouettes (4 people) ── */}
        {/* Person 1 – far left */}
        <ellipse cx="18" cy="22" rx="6" ry="7" fill="#7c3aed" />
        <path d="M10 58 Q12 38 18 36 Q24 38 26 58 Z" fill="#7c3aed" />
        <rect x="11" y="56" width="6" height="18" rx="3" fill="#7c3aed" />
        <rect x="19" y="56" width="6" height="18" rx="3" fill="#7c3aed" />

        {/* Person 2 */}
        <ellipse cx="34" cy="20" rx="6" ry="7" fill="#7c3aed" />
        <path d="M26 56 Q28 36 34 34 Q40 36 42 56 Z" fill="#7c3aed" />
        <rect x="27" y="54" width="6" height="20" rx="3" fill="#7c3aed" />
        <rect x="35" y="54" width="6" height="20" rx="3" fill="#7c3aed" />

        {/* Person 3 (slightly taller, center) */}
        <ellipse cx="52" cy="18" rx="7" ry="8" fill="#6d28d9" />
        <path d="M43 56 Q46 34 52 32 Q58 34 61 56 Z" fill="#6d28d9" />
        <rect x="44" y="54" width="7" height="20" rx="3" fill="#6d28d9" />
        <rect x="53" y="54" width="7" height="20" rx="3" fill="#6d28d9" />

        {/* Person 4 – far right, with bag */}
        <ellipse cx="70" cy="20" rx="6" ry="7" fill="#7c3aed" />
        <path d="M62 56 Q64 36 70 34 Q76 36 78 56 Z" fill="#7c3aed" />
        <rect x="63" y="54" width="6" height="20" rx="3" fill="#7c3aed" />
        <rect x="71" y="54" width="6" height="20" rx="3" fill="#7c3aed" />
        {/* bag */}
        <rect x="76" y="40" width="8" height="12" rx="2" fill="#5b21b6" />

        {/* ── Grey bar with EMSI text ── */}
        <rect x="0" y="74" width="100" height="26" rx="2" fill="#4b5563" />
        <text
          x="50"
          y="91"
          textAnchor="middle"
          fontSize="14"
          fontWeight="bold"
          fontFamily="serif"
          letterSpacing="4"
          fill="white"
        >
          EMSI
        </text>

        {/* ── Red diamond ── */}
        <polygon points="88,62 93,68 88,74 83,68" fill="#dc2626" />
      </svg>
    </div>
  );
}

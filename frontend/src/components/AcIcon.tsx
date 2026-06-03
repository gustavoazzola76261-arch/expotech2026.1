type Props = { on: boolean; size?: number };

/** Ícone de ar-condicionado; fica branco quando ligado. */
export function AcIcon({ on, size = 52 }: Props) {
  return (
    <svg
      className={`ac-unit-svg ${on ? "ac-unit-on" : "ac-unit-off"}`}
      viewBox="0 0 64 64"
      width={size}
      height={size}
      aria-hidden
    >
      <rect x="8" y="14" width="48" height="36" rx="4" className="ac-body" />
      <rect x="12" y="18" width="40" height="8" rx="1" className="ac-vent" />
      <path d="M20 32 H44 M20 38 H44 M20 44 H36" className="ac-lines" fill="none" strokeWidth="2" strokeLinecap="round" />
      <circle cx="48" cy="42" r="3" className="ac-led" />
      <path d="M32 8 V14" className="ac-lines" fill="none" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

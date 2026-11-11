/** Vida Fácil mark: a home inside a rounded violet tile. Decorative; the name is the text next to it. */
export default function Logo({ size = 34 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 34 34" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="vf-logo" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#7b6cf0" />
          <stop offset="1" stopColor="#4b3bbf" />
        </linearGradient>
      </defs>
      <rect width="34" height="34" rx="10" fill="url(#vf-logo)" />
      <path
        d="M9.5 16.2 17 10l7.5 6.2V24a1 1 0 0 1-1 1h-4.3v-4.6h-4.4V25h-4.3a1 1 0 0 1-1-1z"
        fill="none"
        stroke="#fff"
        strokeWidth="2.2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

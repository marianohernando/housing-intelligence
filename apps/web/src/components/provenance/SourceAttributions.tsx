"use client";

import { attributionsOrFallback } from "@/lib/provenance";

import { useDatasets } from "./useDatasets";

const NEW_TAB = " (se abre en una pestaña nueva)";

/** Every citation the licences ask for, as the source catalogue writes it (attribution_text of /datasets). */
export default function SourceAttributions({ className }: { className?: string }) {
  const { data } = useDatasets();
  return (
    <ul className={className}>
      {attributionsOrFallback(data?.datasets ?? null).map(({ text, href }) => (
        <li key={text}>
          {href ? (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {text}
              <span className="visually-hidden">{NEW_TAB}</span>
            </a>
          ) : (
            text
          )}
        </li>
      ))}
    </ul>
  );
}

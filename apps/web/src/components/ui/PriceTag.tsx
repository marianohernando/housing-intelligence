import type { ZonePrice } from "@/lib/fit";

import styles from "./PriceTag.module.css";

/**
 * The approximate price of a zone (D-234): «≈ 385.000 €» beside the % of a ranking row, or
 * «Comprar ≈ 385.000 €» in the zone card head, each with the m² it is for («por 68 m²»), the
 * person's or the usual for their household. Read aloud without «≈»; a figure that is not a
 * reliable one carries the card's words («Dato aproximado»), with their help as a tooltip. In the
 * card, a rent from the Ministry's reference also says where half its leases fall and, on the
 * next line, its source (D-242: «La mitad de los contratos, entre 510 y 820 €/mes» and
 * «Elaboración propia a partir del Ministerio de Vivienda (SERPAVI), 2024»). Under a rent in the card,
 * the 2024 notice (zona.precio.aviso_2024).
 */
export default function PriceTag({ price, variant }: { price: ZonePrice; variant: "row" | "card" }) {
  const range = variant === "card" ? price.range : null;
  // F5 of fit-0.9: a rent is the leases of 2024, said by the card's price (the rows say it once, over the list)
  const notice = variant === "card" ? price.notice : null;
  return (
    <span className={variant === "row" ? styles.row : styles.card} title={price.confidence?.help}>
      <span aria-hidden="true" className={styles.amount}>
        {variant === "row" ? price.short : price.long}
      </span>
      {price.area && (
        <small aria-hidden="true" className={styles.area}>
          {price.area}
        </small>
      )}
      <span className="visually-hidden">{price.aria}</span>
      {price.confidence && <small className={styles.mark}>{price.confidence.label}</small>}
      {range && (
        <small className={styles.range}>
          <span aria-hidden="true">{range.text}</span>
          <span aria-hidden="true" className={styles.source}>
            {range.source}
          </span>
          <span className="visually-hidden">{range.aria}</span>
        </small>
      )}
      {notice && <small className={styles.notice}>{notice}</small>}
    </span>
  );
}

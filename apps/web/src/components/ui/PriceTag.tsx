import type { ZonePrice } from "@/lib/fit";

import styles from "./PriceTag.module.css";

/**
 * The approximate price of a zone (D-234): «≈ 385.000 €» beside the % of a ranking row, or
 * «Comprar ≈ 385.000 €» in the zone card head. Read aloud without «≈»; a figure that is not a
 * reliable one carries the card's words («Dato aproximado»), with their help as a tooltip. In the
 * card, a rent from the Ministry's reference also says where half its leases fall and who
 * publishes it (D-242: «La mitad de los contratos, entre 510 y 820 €/mes · Ministerio de
 * Vivienda (SERPAVI), 2024»).
 */
export default function PriceTag({ price, variant }: { price: ZonePrice; variant: "row" | "card" }) {
  const range = variant === "card" ? price.range : null;
  return (
    <span className={variant === "row" ? styles.row : styles.card} title={price.confidence?.help}>
      <span aria-hidden="true" className={styles.amount}>
        {variant === "row" ? price.short : price.long}
      </span>
      <span className="visually-hidden">{price.aria}</span>
      {price.confidence && <small className={styles.mark}>{price.confidence.label}</small>}
      {range && (
        <small className={styles.range}>
          <span aria-hidden="true">
            {range.text} · <span className={styles.source}>{range.source}</span>
          </span>
          <span className="visually-hidden">{range.aria}</span>
        </small>
      )}
    </span>
  );
}

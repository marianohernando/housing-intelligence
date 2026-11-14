import type { ZonePrice } from "@/lib/fit";

import styles from "./PriceTag.module.css";

/**
 * The approximate price of a zone (D-234): «≈ 385.000 €» beside the % of a ranking row, or
 * «Comprar ≈ 385.000 €» in the zone card head. Read aloud without «≈»; a figure that is not a
 * reliable one carries the card's words («Dato aproximado»), with their help as a tooltip.
 */
export default function PriceTag({ price, variant }: { price: ZonePrice; variant: "row" | "card" }) {
  return (
    <span className={variant === "row" ? styles.row : styles.card} title={price.confidence?.help}>
      <span aria-hidden="true" className={styles.amount}>
        {variant === "row" ? price.short : price.long}
      </span>
      <span className="visually-hidden">{price.aria}</span>
      {price.confidence && <small className={styles.mark}>{price.confidence.label}</small>}
    </span>
  );
}

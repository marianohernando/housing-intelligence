import { PRICE_HINT, type ZonePrice } from "@/lib/fit";

import styles from "./PriceTag.module.css";

/**
 * The approximate price of a zone (D-234), in three places (second delivery of the UX mobile audit):
 * - `row`, in a row of the list: «Unos 1.129 € al mes», nothing else (the m² and the confidence
 *   words wait in the card);
 * - `essential`, the first of the card's essentials: the same words and «Precio orientativo»;
 * - `card`, behind «Ver más» of the card: «Alquiler: unos 1.129 € al mes por 77 m²», with the
 *   confidence words when it is not a reliable figure («Dato aproximado», explained with the card's
 *   facts, never in a tooltip), where half the leases fall and who publishes it (D-242: «Lo normal:
 *   entre 510 y 820 € al mes», «Ministerio de Vivienda (SERPAVI), 2024») and, renting, why it is
 *   orientative (zona.precio.aviso_2024).
 */
export default function PriceTag({ price, variant }: { price: ZonePrice; variant: "row" | "essential" | "card" }) {
  if (variant === "row") return <span className={styles.row}>{price.short}</span>;
  if (variant === "essential") {
    return (
      <span className={styles.essential}>
        <span className={styles.amount}>{price.short}</span>
        <small>{PRICE_HINT}</small>
      </span>
    );
  }
  return (
    <span className={styles.card}>
      <span aria-hidden="true" className={styles.amount}>
        {price.long}
      </span>
      {price.area && (
        <small aria-hidden="true" className={styles.area}>
          {price.area}
        </small>
      )}
      <span className="visually-hidden">{price.aria}</span>
      {price.confidence && <small className={styles.mark}>{price.confidence.label}</small>}
      {price.range && (
        <small className={styles.range}>
          <span aria-hidden="true">{price.range.text}</span>
          <span aria-hidden="true" className={styles.source}>
            {price.range.source}
          </span>
          <span className="visually-hidden">{price.range.aria}</span>
        </small>
      )}
      {price.notice && <small className={styles.notice}>{price.notice}</small>}
    </span>
  );
}

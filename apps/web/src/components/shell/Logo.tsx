import Image from "next/image";

import styles from "./SiteHeader.module.css";

/** Vida Fácil logo: the "V" and the name in one image, so the alt is the brand link's accessible name. */
export default function Logo() {
  return (
    <Image
      src="/brand/vida-facil.png"
      alt="Vida Fácil"
      width={437}
      height={96}
      priority
      unoptimized
      className={styles.logo}
    />
  );
}

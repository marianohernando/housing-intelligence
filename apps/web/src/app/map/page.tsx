import { redirect } from "next/navigation";

/**
 * The first map of the platform (before Vida Fácil) is not part of the demo: it loaded whole layers
 * and kept the old name in its title. Its address now opens the home page.
 */
export default function MapPage() {
  redirect("/");
}

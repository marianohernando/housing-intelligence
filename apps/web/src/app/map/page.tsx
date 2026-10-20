import type { Metadata } from "next";

import AdminMap from "@/components/AdminMap";

export const metadata: Metadata = { title: "Mapa — Housing Intelligence" };

export default function MapPage() {
  return <AdminMap />;
}

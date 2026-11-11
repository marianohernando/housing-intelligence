"use client";

import { Sparkles } from "lucide-react";

import Button from "@/components/ui/Button";

import styles from "./Results.module.css";
import { useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (portada.ejemplo.*)
const TEXT = {
  button: "Ver un ejemplo: pareja con 2 hijos que trabaja en la Castellana",
  help: "Rellenamos la búsqueda por ti para que veas cómo funciona. Luego puedes cambiar lo que quieras.",
};

/** The demo case with one tap from the portada: fills «Tu búsqueda» and runs it. Hidden while the search is off. */
export default function ExampleButton() {
  const { available, loadExample, status } = useScenario();
  if (!available) return null;
  return (
    <div className={styles.example}>
      <Button variant="secondary" onClick={loadExample} disabled={status === "loading"} className={styles.exampleButton}>
        <Sparkles size={20} aria-hidden="true" />
        {TEXT.button}
      </Button>
      <p className={styles.muted}>{TEXT.help}</p>
    </div>
  );
}

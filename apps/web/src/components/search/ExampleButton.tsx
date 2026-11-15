"use client";

import { Sparkles } from "lucide-react";

import Button from "@/components/ui/Button";

import styles from "./Results.module.css";
import { type Example, useScenario } from "./ScenarioProvider";

// Copy from pitch/textos_web.md (portada.ejemplo.*)
const TEXT = {
  buttons: {
    family: "Ejemplo: pareja con 2 hijos que trabaja en la Castellana",
    // portada.ejemplo.mayores (D-244): the audit's case, a retired couple
    retired: "Ejemplo: pareja jubilada que quiere vivir cerca de su familia",
  } satisfies Record<Example, string>,
  help: "Rellenamos la búsqueda por ti. Luego puedes cambiar lo que quieras.",
};

/** The examples with one tap from the portada: each fills «Tu búsqueda» and runs it. Hidden while the search is off. */
export default function ExampleButton() {
  const { available, loadExample, status } = useScenario();
  if (!available) return null;
  return (
    <div className={styles.example}>
      {(Object.keys(TEXT.buttons) as Example[]).map((example) => (
        <Button key={example} variant="secondary" onClick={() => loadExample(example)} disabled={status === "loading"} className={styles.exampleButton}>
          <Sparkles size={20} aria-hidden="true" />
          {TEXT.buttons[example]}
        </Button>
      ))}
      <p className={styles.muted}>{TEXT.help}</p>
    </div>
  );
}

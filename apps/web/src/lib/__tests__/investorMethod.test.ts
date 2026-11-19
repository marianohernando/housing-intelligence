import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import InvestorMethod, { listed, n } from "@/components/method/InvestorMethod";
import { CALCULATOR_TEXT } from "@/lib/investors";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";
import { USE_TEXT } from "@/lib/parcels";

/** The section's text, without tags and with plain spaces. */
function text(): string {
  return renderToStaticMarkup(createElement(InvestorMethod))
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;| /g, " ")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, " ");
}

describe("«Cómo calculamos la ficha para inversores» (D-251)", () => {
  it("writes the figures in Spanish without trailing zeros", () => {
    expect(n(1.36)).toBe("1,36");
    expect(n(0.875)).toBe("0,875");
    expect(n(0.66)).toBe("0,66");
    expect(n(0.9)).toBe("0,9");
    expect(n(1.6)).toBe("1,6");
    expect(n(2)).toBe("2");
    expect(n(500)).toBe("500");
    expect(n(1109)).toBe("1.109");
    expect(listed([2, 3, 4, 6, 10, 11])).toBe("2, 3, 4, 6, 10 y 11");
    expect(listed(["5º"])).toBe("5º");
  });

  it("is reached at #inversores and says each figure from the code, none typed by hand", () => {
    const html = renderToStaticMarkup(createElement(InvestorMethod));
    expect(html).toContain('id="inversores"');
    const t = text();
    // D-252: the PEM of reference (CRG midpoint), with the permits as the low reference
    expect(t).toContain(`de ${n(M.costReferences.crg.defaultPem)} €/m², el punto medio del bloque abierto en Madrid`);
    expect(t).toContain(`Comunidad de Madrid (${M.pem.year}): ${n(M.pem.eurM2)} €/m²`);
    expect(n(M.costCoefficient)).toBe("1,3575");
    expect(t).toContain(`el ICIO de Madrid es del ${n(M.icioPct)} %: Ordenanza fiscal 7/2023, art. 25, tipo aprobado para 2024 y vigente en 2025`);
    expect(t).toContain(`margen mínimo del ${n(M.appraisalMinMarginPct)} % en vivienda de primera residencia`);
    expect(t).not.toContain("pero no una cifra de m²");
    // «Solar» only where it is defined by law, in the services section (D-253)
    expect(t.split("4. Servicios y suministros")[0]).not.toMatch(/\bsolar\b/);
    expect(t).toContain(`coeficiente de ${n(M.costCoefficient)}`);
    expect(t).toContain(`un ${n(M.salesCostsPct)} % de las ventas`);
    expect(t).toContain(`un ${n(M.targetMarginPct)} % de las ventas`);
    expect(t).toContain(`entre el ${n(M.adjustFloorPct)} % y el objetivo`);
    expect(t).toContain(`si el barrio de la parcela es uno de los ${M.pilotBarrios} del piloto`);
    expect(t).toContain(`(${n(M.vedaParcels)} parcelas, de vivienda y de otros usos)`);
    expect(t).toContain(`(${M.portalParcels} parcelas de Madrid capital)`);
    expect(t).toContain(`una vivienda tipo de ${n(M.homeM2)} m²`.replace("una", "Una"));
    expect(t).toContain(`frente al ${n(M.effortThresholdPct)} % de la renta media`);
    expect(t).toContain(`como mucho ${n(M.lookupBudgetS)} segundos`);
    for (const rule of M.zonalNorms) {
      expect(t).toContain(`Norma zonal ${rule.nz} (${rule.name}):`);
      for (const c of rule.coefficients) expect(t).toContain(`grado ${c.grado}º, ${n(c.value)}`);
      expect(html).toContain(`href="${rule.url.replace(/&/g, "&amp;")}"`);
    }
    for (const f of M.nz1.factors) expect(t).toContain(`grado ${f.grado}º, ${n(f.value)}`);
    const [, optimistic, pessimistic] = M.scenarios;
    expect(t).toContain(`un ${n(optimistic?.pricePct ?? 0)} % más de precio de venta y de alquiler`);
    expect(t).toContain(`un ${n(pessimistic?.costPct ?? 0)} % más de coste`);
    expect(t).toContain(`las normas zonales ${listed(M.withoutCoefficient)}, que no fijan una cifra`);
    const split = M.zonalNorms.find((r) => r.nz === M.split.nz)?.coefficients.find((c) => c.grado === M.split.grado);
    expect(t).toContain(`En el grado ${M.split.grado}º, ${n(split?.value ?? 0)} hasta ${n(M.split.limitM2)} m²`);
  });

  it("names the Catastro as the code does and never calls our data «información catastral»", () => {
    const t = text();
    expect(t).toContain("datos elaborados por Vida Fácil a partir de los de la Dirección General del Catastro");
    expect(t).toContain("sin valor jurídico");
    expect(t).toContain("«Sin dato» no es 0");
    expect(t.toLowerCase()).not.toMatch(/(información|ficha|cartografía) catastral/);
  });

  it("says what happens when a source fails, what is not editable and when there is a margin (review of #104)", () => {
    const t = text();
    expect(t).toContain("si el Catastro no responde, no podemos enseñarte la ficha, salvo la de las parcelas de ejemplo");
    expect(t).toContain("Si el Ayuntamiento no responde, te enseñamos la parcela sin el planeamiento");
    expect(t).toContain("(leer el barrio va aparte)");
    expect(t).toContain("El margen sobre ventas, solo si pones el precio del suelo");
    expect(t).toContain("si ni con el suelo gratis se llega al margen objetivo, no hay rentabilidad que dar");
    expect(t).toContain(`No se cambian el suelo del «Ajustar» (${n(M.adjustFloorPct)} %)`);
    expect(t).toContain("no hay franja de «Ajustar»");
    expect(t).not.toContain("todo editable");
    for (const word of ["PEM y PEC:", "ICIO:", "Seguro decenal:", "Ámbito:", "Dotacional:", "Valor residual del suelo:"]) {
      expect(t).toContain(word);
    }
  });

  it("explains each use, the figures by use and that the calculator is for housing (D-252)", () => {
    const t = text();
    for (const { label, plain } of Object.values(USE_TEXT)) expect(t).toContain(`${label}: ${plain.charAt(0).toLowerCase()}${plain.slice(1)}`);
    const veda = M.vedaByUse;
    expect(t).toContain(
      `de las ${n(M.vedaParcels)} de VEDA, ${n(veda.residencial)} de uso residencial, ${n(veda.terciario)} de uso terciario y ${n(veda.industrial)} de uso industrial;`,
    );
    expect(Object.values(veda).reduce((a, b) => a + b, 0)).toBe(M.vedaParcels);
    expect(Object.values(M.portalByUse).reduce((a, b) => a + b, 0)).toBe(M.portalParcels);
    expect(t).toContain(`${M.portalByUse.otro} de otros usos`);
    expect(t).toContain("nunca la repartimos entre usos");
    expect(t).toContain("La calculadora calcula solo vivienda,");
  });

  it("says what the cost includes and leaves out, and the break-even, as the calculator does (D-252)", () => {
    const t = text();
    expect(t).toContain(CALCULATOR_TEXT.costIncludes(M.costParts.map((p) => p.label.charAt(0).toLowerCase() + p.label.slice(1))));
    for (const line of CALCULATOR_TEXT.costExcludes) expect(t).toContain(line.replace(/&/g, "&amp;"));
    expect(t).toContain("Hasta cuánto puede costar la construcción (el punto de equilibrio)");
    expect(t).toContain("Punto de equilibrio:");
  });

  it("says the services and supplies and what a full study adds, with the code's figures (D-253)", () => {
    const t = text();
    expect(t).toContain("4. Servicios y suministros");
    expect(t).toContain("(Ley 9/2001 del Suelo de la Comunidad de Madrid, art. 14.1.a)");
    expect(t).toContain(`${n(M.supplies.kwPerHome)} kW por vivienda (electrificación básica)`);
    expect(t).toContain(`de ${n(M.supplies.simultaneityOne)} con una vivienda a ${n(M.supplies.simultaneityMax)} con ${M.supplies.tableHomes}`);
    expect(t).toContain("(RD 1048/2013, art. 26.1)");
    expect(t).toContain("Solo enlazamos su mapa: no copiamos sus cifras.");
    expect(t).toContain("arts. 4.3.4 y 4.3.7");
    expect(t).toContain("Esto es un primer filtro de minutos, gratis y con fuentes.");
    expect(t).toContain("(Real Decreto 9/2005)");
    for (const word of ["CUPS:", "Acometida:", "Derechos de acometida:", "Quién paga la red:", "Centro de transformación:", "Plazos de la norma:"]) {
      expect(t).toContain(word);
    }
  });
});

import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import InvestorMethod, { listed, n } from "@/components/method/InvestorMethod";
import { INVESTOR_METHOD as M } from "@/lib/investorMethod";

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
    expect(t).toContain(`${n(M.pem.eurM2)} €/m², ${M.pem.year}`);
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
    const [, optimistic] = M.scenarios;
    expect(t).toContain(`un ${n(optimistic?.pricePct ?? 0)} % más de precio de venta y de alquiler`);
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
});

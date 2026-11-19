import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import InvestorMethod, { n } from "@/components/method/InvestorMethod";
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
    expect(t).toContain(`los ${M.pilotBarrios} barrios del piloto`);
    expect(t).toContain(`(${n(M.vedaParcels)} parcelas)`);
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
    for (const s of M.scenarios.slice(1)) expect(t).toContain(`${s.key} (`);
  });

  it("names the Catastro as the code does and never calls our data «información catastral»", () => {
    const t = text();
    expect(t).toContain("datos elaborados por Vida Fácil a partir de los de la Dirección General del Catastro");
    expect(t).toContain("sin valor jurídico");
    expect(t).toContain("«Sin dato» no es 0");
    expect(t.toLowerCase()).not.toMatch(/(información|ficha|cartografía) catastral/);
  });
});

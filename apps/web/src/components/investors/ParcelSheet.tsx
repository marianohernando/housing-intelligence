"use client";

import { ExternalLink, Info, Printer } from "lucide-react";
import Link from "next/link";
import { type ReactNode, useEffect, useMemo } from "react";

import type { ParcelSheet as Sheet } from "@/contracts/parcel_sheet_response";
import Button from "@/components/ui/Button";
import GlassCard from "@/components/ui/GlassCard";
import { SLOW_TEXT, useSlow } from "@/components/ui/useSlow";
import { errorMessage } from "@/lib/errors";
import { INVESTOR_TEXT, isoInWords, SHEET_TEXT as BARRIO_TEXT, today, uniqueDatasets } from "@/lib/investors";
import {
  ambitText,
  areaText,
  buildabilityMark,
  buildableText,
  byUseSource,
  byUseText,
  dayMonthYear,
  degradedLines,
  divisionText,
  instrumentText,
  LOOKUP_ERROR,
  planUseSource,
  planUseText,
  publicLandText,
  qualificationText,
  sentence,
  SHEET_TEXT as TEXT,
  landUseNote,
  vacantText,
} from "@/lib/parcels";

import Calculator, { type ParcelStart } from "./Calculator";
import { MarkTag } from "./Figures";
import MethodLink from "./MethodLink";
import { Demand, Gaps, Land, Prices, Section } from "./InvestorSheet";
import styles from "./Investors.module.css";
import own from "./Parcels.module.css";
import { useParcel } from "./useInvestors";

const NEW_TAB = " (se abre en una pestaña nueva)";
const RETRY_CODES = new Set(["SOURCE_DEGRADED", "RATE_LIMITED", "TIMEOUT", "NETWORK", "HTTP_502", "HTTP_503", "HTTP_504"]);

function Fact({ label, children, note }: { label: string; children: ReactNode; note?: string | null }) {
  return (
    <div className={styles.figure}>
      <dt>{label}</dt>
      <dd>
        <span className={styles.value}>{children}</span>
        {note && <span className={styles.note}>{note}</span>}
      </dd>
    </div>
  );
}

function External({ href, children, label }: { href: string; children: ReactNode; label?: string }) {
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className={styles.external}>
      {children}
      <ExternalLink size={16} aria-hidden="true" />
      <span className="visually-hidden">
        {label ? `: ${label}` : ""}
        {NEW_TAB}
      </span>
    </a>
  );
}

function sourceOf(sheet: Sheet, id: string): string | null {
  return sheet.sources.find((s) => s.source_id === id)?.attribution ?? null;
}

function ParcelData({ sheet }: { sheet: Sheet }) {
  const p = sheet.parcel;
  const attribution = sourceOf(sheet, "catastro_ovc");
  return (
    <Section id="parcela" title={TEXT.sections.parcel}>
      <dl className={styles.figures}>
        <Fact label={TEXT.area}>{areaText(p.area_m2)}</Fact>
        <Fact label={TEXT.use}>{p.current_use ?? "Sin dato"}</Fact>
        <Fact label={TEXT.built} note={TEXT.builtNote}>
          {areaText(p.built_m2)}
        </Fact>
        <Fact label={TEXT.year}>{p.year_built ?? "Sin dato"}</Fact>
        <Fact label={TEXT.vacant}>{vacantText(p)}</Fact>
        <Fact label={TEXT.division}>{divisionText(p)}</Fact>
      </dl>
      {p.official_url && <External href={p.official_url}>{TEXT.catastroLink}</External>}
      {attribution && <p className={styles.source}>{attribution}</p>}
    </Section>
  );
}

function Planning({ sheet, retry }: { sheet: Sheet; retry: () => void }) {
  const planning = sheet.planning;
  if (!planning) {
    const down = sheet.degraded?.includes("planning");
    return (
      <Section id="planeamiento" title={TEXT.sections.planning}>
        <p role={down ? "alert" : undefined}>{down ? TEXT.planningDown : TEXT.planningNone}</p>
        {down && (
          <Button variant="secondary" onClick={retry}>
            {TEXT.retry}
          </Button>
        )}
      </Section>
    );
  }
  const instrument = instrumentText(planning);
  const attribution = sourceOf(sheet, "ayuntamiento_madrid_urbanismo_sigma");
  return (
    <Section id="planeamiento" title={TEXT.sections.planning}>
      <dl className={styles.figures}>
        <Fact label={TEXT.qualification} note={planning.norma_zonal?.name ?? null}>
          {qualificationText(planning)}
        </Fact>
        <Fact label={TEXT.planningUse} note={landUseNote(planning)}>
          {sentence(planning.use) ?? "Sin dato"}
        </Fact>
        {planning.urban_parcel && <Fact label={TEXT.urbanParcel}>{planning.urban_parcel}</Fact>}
        {instrument && <Fact label={TEXT.instrument}>{instrument}</Fact>}
        {planning.ambit && (
          <Fact label={TEXT.ambit} note={planning.ambit.tracked ? TEXT.ambitAsOf(planning.ambit.code, isoInWords(planning.ambit.as_of)) : null}>
            {ambitText(planning.ambit)}
          </Fact>
        )}
      </dl>
      <p className={own.links}>
        {planning.sheet_url && (
          <External href={planning.sheet_url}>
            {planning.instrument?.url ? TEXT.recordLink : TEXT.sheetLink(planning.sheet_label)}
          </External>
        )}
        <External href={planning.viewer_url}>{TEXT.viewer}</External>
      </p>
      <p className={styles.caution}>
        <Info size={18} aria-hidden="true" />
        <span>{planning.notice}</span>
      </p>
      {attribution && <p className={styles.source}>{attribution}</p>}
    </Section>
  );
}

/** D-252 (audit D3): what the plan allows by use on the urban parcel (tables 4 and 5 of USOS_SUELO). */
function PlanUses({ planning }: { planning: Sheet["planning"] }) {
  if (!planning || planning.plan_uses === null || planning.plan_uses === undefined) return null;
  const uses = planning.plan_uses;
  const source = TEXT.planUsesSource(dayMonthYear(planning.plan_uses_as_of));
  return (
    <>
      <h3 className={styles.subhead}>{TEXT.byUseTitle}</h3>
      {uses.length === 0 ? (
        <>
          <p className={styles.note}>{planning.plan_principal_without_figure ? TEXT.planUsesWithoutFigure : TEXT.planUsesNone}</p>
          <p className={styles.source}>{source}</p>
        </>
      ) : (
        <>
          <p>{TEXT.planUsesTitle(planning.urban_parcel)}</p>
          <ul className={styles.landList}>
            {uses.map((u) => (
              <li key={`${u.principal}-${u.use}`}>
                <strong>{planUseText(u, planning.urban_parcel_area_m2)}</strong>
                <span className={styles.note}>{planUseSource(u)}</span>
              </li>
            ))}
          </ul>
          <p className={styles.note}>{TEXT.planUsesCaveats}</p>
          <p className={styles.source}>{source}</p>
        </>
      )}
    </>
  );
}

/** Each source's figure with the use it gives (D-252): never split, never added up. */
function ByUse({ figures }: { figures: Sheet["buildability"]["by_use"] }) {
  if (!figures || figures.length === 0) return <p className={styles.note}>{TEXT.byUseNone}</p>;
  return (
    <>
      <h3 className={styles.subhead}>{TEXT.officialTitle}</h3>
      <ul className={styles.landList}>
        {figures.map((f) => (
          <li key={`${f.dataset_id}-${f.use}`}>
            <strong>{byUseText(f)}</strong>
            <span className={styles.note}>{byUseSource(f)}</span>
            {!f.residential && <span className={styles.note}>{TEXT.notHousing}</span>}
          </li>
        ))}
      </ul>
      <p className={styles.note}>{TEXT.byUseNote}</p>
    </>
  );
}

function BuildabilitySection({ sheet }: { sheet: Sheet }) {
  const b = sheet.buildability;
  const built = sheet.parcel.built_m2;
  return (
    <Section id="edificabilidad" title={TEXT.sections.buildability}>
      <dl className={styles.figures}>
        <div className={styles.figure}>
          <dt>{TEXT.buildable}</dt>
          <dd>
            <span className={styles.value}>{buildableText(b)}</span>
            <MarkTag mark={buildabilityMark(b.kind)} />
            {b.formula && <span className={styles.note}>{b.formula}</span>}
            <span className={styles.source}>{b.source}</span>
            {b.note && <span className={styles.note}>{b.note}</span>}
          </dd>
        </div>
        {built !== null && built !== undefined && (
          <Fact label={TEXT.built} note={TEXT.builtNote}>
            {areaText(built)}
          </Fact>
        )}
      </dl>
      {b.article && b.article_url && <External href={b.article_url}>{TEXT.article(b.article)}</External>}
      <PlanUses planning={sheet.planning} />
      <ByUse figures={b.by_use} />
      {sheet.public_land && (
        <p className={styles.caution}>
          <Info size={18} aria-hidden="true" />
          <span>{publicLandText(sheet.public_land)}</span>
        </p>
      )}
      <p className={styles.note}>
        {TEXT.housingOnly} {TEXT.buildableEditable}
      </p>
      <MethodLink />
    </Section>
  );
}

function Context({ sheet }: { sheet: Sheet }) {
  const context = sheet.context;
  if (!context) {
    const down = sheet.degraded?.includes("context");
    return (
      <GlassCard role={down ? "alert" : "status"} className={styles.card}>
        <p>{down ? TEXT.contextDown : TEXT.noBarrio}</p>
      </GlassCard>
    );
  }
  const district = !context.in_pilot;
  return (
    <>
      {context.note && (
        <p className={styles.caution}>
          <Info size={18} aria-hidden="true" />
          <span>{context.note}</span>
        </p>
      )}
      <Demand sheet={context.sheet} title={TEXT.sections.demand(district)} />
      <Prices sheet={context.sheet} title={TEXT.sections.prices(district)} />
      <Gaps sheet={context.sheet} title={TEXT.sections.gaps} />
      <Land sheet={context.sheet} title={TEXT.sections.land(district)} />
    </>
  );
}

function Sources({ sheet, version }: { sheet: Sheet; version: string | null }) {
  const datasets = sheet.context ? uniqueDatasets(sheet.context.sheet.datasets) : [];
  return (
    <Section id="fuentes" title={TEXT.sections.sources}>
      <ul className={styles.notices}>
        {sheet.notices.map((notice) => (
          <li key={notice}>{notice}</li>
        ))}
      </ul>
      {version && <p className={styles.note}>{BARRIO_TEXT.version(version)}</p>}
      <h3 className={styles.subhead}>{TEXT.sourcesTitle(sheet.sources.length)}</h3>
      <ul className={styles.datasets}>
        {sheet.sources.map((s) => (
          <li key={`${s.source_id}-${s.name}`}>
            {s.publisher}: {s.name}. {s.attribution} Licencia: {s.license}.
            {s.url && (
              <>
                {" "}
                <a href={s.url} target="_blank" rel="noopener noreferrer">
                  {TEXT.open}
                  <span className="visually-hidden">
                    : {s.name}
                    {NEW_TAB}
                  </span>
                </a>
                <span className={styles.printOnly}>{s.url}</span>
              </>
            )}
          </li>
        ))}
      </ul>
      {datasets.length > 0 && (
        <details className={styles.parts} open>
          <summary>{TEXT.barrioDatasets(datasets.length)}</summary>
          <ul className={styles.datasets}>
            {datasets.map((d) => (
              <li key={d.dataset_id}>
                {d.publisher}: {d.name}
                {d.version ? ` (versión ${d.version})` : ""}
                {d.url && (
                  <>
                    {" · "}
                    <a href={d.url} target="_blank" rel="noopener noreferrer">
                      {TEXT.open}
                      <span className="visually-hidden">
                        : {d.name}
                        {NEW_TAB}
                      </span>
                    </a>
                    <span className={styles.printOnly}>{d.url}</span>
                  </>
                )}
              </li>
            ))}
          </ul>
        </details>
      )}
    </Section>
  );
}

/** A parcel of Madrid capital for whoever builds (D-250): /inversores/parcela/{rc14}. */
export default function ParcelSheetView({ rc14 }: { rc14: string }) {
  const result = useParcel(rc14);
  const slow = useSlow(result.loading);
  const data = result.data?.data ?? null;
  const start = useMemo<ParcelStart | undefined>(() => {
    if (!data) return undefined;
    const cautions = (data.cautions ?? []).filter((c) => c.key === "vivienda_protegida" || c.key === "unifamiliar").map((c) => c.text);
    if (data.public_land) cautions.push(publicLandText(data.public_land));
    return {
      m2: data.buildability.value_m2 ?? null,
      mark: buildabilityMark(data.buildability.kind),
      help: TEXT.calculatorFrom(data.buildability.kind),
      cautions,
      protectedHousing: (data.cautions ?? []).some((c) => c.key === "vivienda_protegida"),
    };
  }, [data]);

  useEffect(() => {
    const unfold = () => document.querySelectorAll("[data-print-page] details").forEach((d) => d.setAttribute("open", ""));
    window.addEventListener("beforeprint", unfold);
    return () => window.removeEventListener("beforeprint", unfold);
  }, []);

  if (result.loading) {
    return (
      <GlassCard role="status" className={styles.card}>
        <p>
          {TEXT.loading}
          {slow && ` ${SLOW_TEXT}`}
        </p>
      </GlassCard>
    );
  }
  if (result.error || !data || !result.data) {
    const code = result.error?.code ?? "";
    return (
      <GlassCard role="alert" className={styles.card}>
        <p>{LOOKUP_ERROR[code] ?? (result.error ? errorMessage(result.error) : TEXT.loading)}</p>
        <div className={styles.actions}>
          {RETRY_CODES.has(code) && (
            <Button variant="secondary" onClick={result.retry}>
              {TEXT.retry}
            </Button>
          )}
          <Button href="/inversores">{TEXT.back}</Button>
        </div>
      </GlassCard>
    );
  }

  const sheet = data;
  const version = result.data.meta?.data_version ?? null;
  const notes = degradedLines(sheet);
  return (
    <div className={styles.sheet} data-print-page data-investors>
      <header className={styles.header}>
        <p className={`${styles.backLink} no-print`}>
          <Link href="/inversores">{TEXT.back}</Link>
        </p>
        <p className={styles.plan}>{INVESTOR_TEXT.plan}</p>
        <p className={styles.eyebrow}>{TEXT.eyebrow(sheet.barrio?.name ?? null, sheet.district?.name ?? null)}</p>
        <h1 className={styles.title}>{sheet.parcel.address ?? TEXT.rcLine(sheet.parcel.rc14)}</h1>
        <p className={styles.lead}>{TEXT.rcLine(sheet.parcel.rc14)}</p>
        <p className={styles.printOnly}>{INVESTOR_TEXT.generated(today(), version)}</p>
        <div className={`${styles.actions} no-print`}>
          <Button variant="secondary" onClick={() => window.print()}>
            <Printer size={18} aria-hidden="true" />
            {INVESTOR_TEXT.print}
          </Button>
          <span className={styles.note}>{INVESTOR_TEXT.printHelp}</span>
        </div>
        {notes.map((line) => (
          <p key={line} className={styles.caution} role="status">
            <Info size={18} aria-hidden="true" />
            <span>{line}</span>
          </p>
        ))}
        {(sheet.cautions ?? []).map((c) => (
          <p key={c.key} className={styles.caution} data-caution={c.key}>
            <Info size={18} aria-hidden="true" />
            <span>{c.text}</span>
          </p>
        ))}
      </header>
      <ParcelData sheet={sheet} />
      <Planning sheet={sheet} retry={result.retry} />
      <BuildabilitySection sheet={sheet} />
      <Context sheet={sheet} />
      <Section id="viabilidad" title={TEXT.sections.viability}>
        <Calculator defaults={sheet.defaults} parcels={[]} remaining={[]} parcel={start} methodLink={false} />
      </Section>
      <Sources sheet={sheet} version={version} />
      <p className={styles.printOnly}>{`Datos de la parcela consultados el ${isoInWords(sheet.parcel.observed_at)}.`}</p>
    </div>
  );
}

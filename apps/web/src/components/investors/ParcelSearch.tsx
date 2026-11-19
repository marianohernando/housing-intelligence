"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { type FormEvent, useCallback, useEffect, useId, useRef, useState } from "react";

import type { ParcelCandidates } from "@/contracts/parcel_candidates_response";
import GlassCard from "@/components/ui/GlassCard";
import { ApiError, createApi } from "@/lib/api";
import { errorMessage } from "@/lib/errors";
import { formatNumber } from "@/lib/format";
import { DEMO_PARCELS, LOOKUP_ERROR, type NearbyParcel, parcelHref, parcelRc, SEARCH_TEXT as TEXT } from "@/lib/parcels";

import ParcelMap from "./ParcelMap";
import styles from "./Parcels.module.css";

const DEBOUNCE_MS = 300;
const MIN_LETTERS = 4;

function lookupMessage(error: ApiError): string {
  return LOOKUP_ERROR[error.code] ?? errorMessage(error);
}

/** «Por referencia catastral»: the reference typed, checked here as the API reads it. */
function ByReference() {
  const router = useRouter();
  const id = useId();
  const [value, setValue] = useState("");
  const [invalid, setInvalid] = useState(false);
  const submit = (event: FormEvent) => {
    event.preventDefault();
    const rc = parcelRc(value);
    setInvalid(rc === null);
    if (rc) router.push(parcelHref(rc));
  };
  return (
    <section aria-labelledby={`${id}-title`} className={styles.way}>
      <h2 id={`${id}-title`}>{TEXT.rcTitle}</h2>
      <form onSubmit={submit} className={styles.form} noValidate>
        <label htmlFor={`${id}-rc`}>{TEXT.rcLabel}</label>
        <span className={styles.inputRow}>
          <input
            id={`${id}-rc`}
            name="rc"
            type="text"
            autoComplete="off"
            autoCapitalize="characters"
            spellCheck={false}
            value={value}
            onChange={(event) => {
              setValue(event.target.value);
              setInvalid(false);
            }}
            aria-invalid={invalid || undefined}
            aria-describedby={`${id}-help${invalid ? ` ${id}-error` : ""}`}
          />
          <button type="submit" className={styles.submit}>
            {TEXT.rcButton}
          </button>
        </span>
        {invalid && (
          <span id={`${id}-error`} className={styles.fieldError} role="alert">
            {TEXT.rcInvalid}
          </span>
        )}
        <span id={`${id}-help`} className={styles.help}>
          {TEXT.rcHelp}
        </span>
      </form>
    </section>
  );
}

type Found = { query: string; body: ParcelCandidates } | { query: string; error: ApiError };

/** «Por dirección»: CartoCiudad's portals as the person types; the person picks one (never us). */
function ByAddress() {
  const id = useId();
  const [value, setValue] = useState("");
  const [found, setFound] = useState<Found | null>(null);
  const query = value.trim();
  const ready = query.length >= MIN_LETTERS;

  useEffect(() => {
    if (!ready) return;
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      createApi()
        .parcelCandidates(query, { signal: controller.signal })
        .then((response) => setFound({ query, body: response.data }))
        .catch((exc: unknown) => {
          if (controller.signal.aborted) return;
          setFound({ query, error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
        });
    }, DEBOUNCE_MS);
    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [query, ready]);

  const current = ready && found?.query === query ? found : null;
  const body = current && "body" in current ? current.body : null;
  const error = current && "error" in current ? current.error : null;
  let status = "";
  if (!ready) status = query.length > 0 ? TEXT.addressShort : "";
  else if (!current) status = TEXT.addressSearching;
  else if (error) status = error.code === "SOURCE_DEGRADED" ? TEXT.addressDown : lookupMessage(error);
  else if (body && body.candidates.length > 0) status = TEXT.addressCount(body.candidates.length);
  else if (body?.needs_number) status = TEXT.addressNeedsNumber;
  else if (body) status = TEXT.addressNone;

  return (
    <section aria-labelledby={`${id}-title`} className={styles.way}>
      <h2 id={`${id}-title`}>{TEXT.addressTitle}</h2>
      <div className={styles.form}>
        <label htmlFor={`${id}-address`}>{TEXT.addressLabel}</label>
        <span className={styles.inputRow}>
          <input
            id={`${id}-address`}
            name="direccion"
            type="search"
            autoComplete="off"
            value={value}
            onChange={(event) => setValue(event.target.value)}
            aria-describedby={`${id}-help ${id}-status`}
          />
        </span>
        <span id={`${id}-help`} className={styles.help}>
          {TEXT.addressHelp}
        </span>
        <span id={`${id}-status`} className={styles.status} role="status" aria-live="polite">
          {status}
        </span>
        {body && body.candidates.length > 0 && (
          <>
            <ul className={styles.candidates} aria-label={TEXT.addressList}>
              {body.candidates.map((c) => (
                <li key={`${c.rc14}-${c.address}`}>
                  <Link href={parcelHref(c.rc14)} className={styles.candidate}>
                    <span>{c.address}</span>
                    <span className={styles.candidateNote}>{[c.postal_code, `Referencia ${c.rc14}`].filter(Boolean).join(" · ")}</span>
                  </Link>
                </li>
              ))}
            </ul>
            <p className={styles.help}>{body.sources.map((s) => s.attribution).join(" ")}</p>
          </>
        )}
      </div>
    </section>
  );
}

type Picked = { state: "finding" } | { state: "error"; message: string; nearest: NearbyParcel[] };

/** «En el mapa»: the parcel of the point the person clicks, or the nearest ones if it is the street. */
function ByMap() {
  const id = useId();
  const router = useRouter();
  const [picked, setPicked] = useState<Picked | null>(null);
  // One lookup at a time: a new click cancels the previous one, and only the last one navigates
  const inFlight = useRef<AbortController | null>(null);
  useEffect(() => () => inFlight.current?.abort(), []);
  const pick = useCallback(
    (lat: number, lon: number) => {
      inFlight.current?.abort();
      const controller = new AbortController();
      inFlight.current = controller;
      setPicked({ state: "finding" });
      createApi()
        .parcel({ lat, lon }, { timeoutMs: 30_000, signal: controller.signal })
        .then((response) => {
          if (!controller.signal.aborted) router.push(parcelHref(response.data.parcel.rc14));
        })
        .catch((exc: unknown) => {
          if (controller.signal.aborted) return;
          const error = exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc));
          const nearest = (error.details.nearest as NearbyParcel[] | undefined) ?? [];
          const message =
            error.code === "NOT_FOUND"
              ? nearest.length > 0
                ? TEXT.mapStreet
                : TEXT.mapNone
              : error.code === "OUT_OF_COVERAGE"
                ? TEXT.mapOut
                : lookupMessage(error);
          setPicked({ state: "error", message, nearest });
        });
    },
    [router],
  );
  return (
    <section aria-labelledby={`${id}-title`} className={`${styles.way} ${styles.wayMap}`}>
      <h2 id={`${id}-title`}>{TEXT.mapTitle}</h2>
      <p className={styles.help}>{TEXT.mapHelp}</p>
      <ParcelMap onPick={pick} />
      <div role="status" aria-live="polite" className={styles.status}>
        {picked?.state === "finding" && TEXT.mapFinding}
        {picked?.state === "error" && picked.message}
      </div>
      {picked?.state === "error" && picked.nearest.length > 0 && (
        <ul className={styles.candidates}>
          {picked.nearest.map((n) => (
            <li key={n.rc14}>
              <Link href={parcelHref(n.rc14)} className={styles.candidate}>
                <span>{n.address ?? `Referencia ${n.rc14}`}</span>
                {n.distance_m !== null && n.distance_m !== undefined && (
                  <span className={styles.candidateNote}>A {formatNumber(n.distance_m, 0)} m</span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

/** «Busca tu parcela» (D-250): three ways in and the four demo parcels. */
export default function ParcelSearch() {
  return (
    <GlassCard as="section" aria-label={TEXT.title} className={styles.search}>
      <div className={styles.ways}>
        <ByReference />
        <ByAddress />
      </div>
      <ByMap />
      <section aria-labelledby="parcelas-demo" className={styles.way}>
        <h2 id="parcelas-demo">{TEXT.demosTitle}</h2>
        <ul className={styles.demos}>
          {DEMO_PARCELS.map((demo) => (
            <li key={demo.rc14}>
              <Link href={parcelHref(demo.rc14)} className={styles.demo}>
                <strong>{demo.label}</strong>
                <span>{demo.why}</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </GlassCard>
  );
}

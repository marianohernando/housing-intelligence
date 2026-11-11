"use client";

import { useEffect, useState } from "react";

import type { DatasetList } from "@/contracts/dataset_list_response";
import { ApiError, createApi } from "@/lib/api";

// One request per visit, shared by the footer counter and the list of sources.
let request: Promise<DatasetList> | null = null;

function load(): Promise<DatasetList> {
  if (!request) {
    request = createApi()
      .datasets()
      .then((body) => body.data);
    request.catch(() => {
      request = null;
    });
  }
  return request;
}

type Result = { data: DatasetList } | { error: ApiError };

/** GET /api/v1/datasets: every dataset behind the product, with the CM portal count. */
export function useDatasets() {
  const [result, setResult] = useState<Result | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    load()
      .then((data) => {
        if (!cancelled) setResult({ data });
      })
      .catch((exc: unknown) => {
        if (!cancelled) setResult({ error: exc instanceof ApiError ? exc : new ApiError(0, "NETWORK", String(exc)) });
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  return {
    loading: result === null,
    data: result && "data" in result ? result.data : null,
    error: result && "error" in result ? result.error : null,
    retry: () => {
      setResult(null);
      setAttempt((n) => n + 1);
    },
  };
}

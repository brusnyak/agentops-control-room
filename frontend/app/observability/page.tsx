"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api, type ObservabilityStats } from "@/lib/api";

export default function ObservabilityPage() {
  const [stats, setStats] = useState<ObservabilityStats | null>(null);

  useEffect(() => {
    api.observability.stats().then(setStats).catch(() => {});
  }, []);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Observability</h1>
        <p className="text-muted-foreground">Every LLM call logged — tokens, latency, attempts, success.</p>
      </div>

      {!stats && <Skeleton className="h-40 w-full" />}

      {stats && stats.total_calls === 0 && (
        <Card>
          <CardContent className="text-muted-foreground py-8 text-center">
            No LLM calls logged yet — trigger a run to see data here.
          </CardContent>
        </Card>
      )}

      {stats && stats.total_calls > 0 && (
        <>
          <div className="grid gap-4 sm:grid-cols-4">
            <MetricCard label="Total calls" value={stats.total_calls} />
            <MetricCard label="Success rate" value={`${((stats.success_rate ?? 0) * 100).toFixed(0)}%`} />
            <MetricCard label="Avg latency" value={`${stats.avg_latency_ms?.toFixed(0)}ms`} />
            <MetricCard label="Avg attempts" value={stats.avg_attempts?.toFixed(2) ?? "—"} />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Token usage</CardTitle>
              <CardDescription>Free-tier OpenRouter models: $0 spend, tracked for the day this swaps to paid.</CardDescription>
            </CardHeader>
            <CardContent className="flex gap-8">
              <div>
                <p className="text-muted-foreground text-sm">Prompt tokens</p>
                <p className="text-2xl font-semibold">{stats.total_prompt_tokens.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-sm">Completion tokens</p>
                <p className="text-2xl font-semibold">{stats.total_completion_tokens.toLocaleString()}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Calls by purpose</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-2">
              {Object.entries(stats.by_purpose).map(([purpose, count]) => (
                <div key={purpose} className="flex items-center justify-between border-b py-1 last:border-0">
                  <span className="text-sm">{purpose}</span>
                  <span className="text-muted-foreground text-sm">{count}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{label}</CardDescription>
        <CardTitle className="text-2xl">{value}</CardTitle>
      </CardHeader>
    </Card>
  );
}

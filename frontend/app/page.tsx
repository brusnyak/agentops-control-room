"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api, type ObservabilityStats } from "@/lib/api";

export default function Home() {
  const [contactCount, setContactCount] = useState<number | null>(null);
  const [templateCount, setTemplateCount] = useState<number | null>(null);
  const [campaignCount, setCampaignCount] = useState<number | null>(null);
  const [stats, setStats] = useState<ObservabilityStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.contacts.list(),
      api.workflowTemplates.list(),
      api.campaigns.list(),
      api.observability.stats(),
    ])
      .then(([contacts, templates, campaigns, observability]) => {
        setContactCount(contacts.length);
        setTemplateCount(templates.length);
        setCampaignCount(campaigns.length);
        setStats(observability);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load"));
  }, []);

  if (error) {
    return (
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle>Can&apos;t reach the backend</CardTitle>
          <CardDescription>{error} — is it running at NEXT_PUBLIC_API_URL?</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Configurable AI outbound workflows, run harness, evaluation, and observability.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-4">
        <StatCard title="Contacts" value={contactCount} href="/contacts" cta="View contacts" />
        <StatCard title="Templates" value={templateCount} href="/templates" cta="View templates" />
        <StatCard title="Campaigns" value={campaignCount} href="/campaigns" cta="View campaigns" />
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>LLM calls logged</CardDescription>
            <CardTitle className="text-3xl">
              {stats ? stats.total_calls : <Skeleton className="h-8 w-16" />}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Link href="/observability" className="text-sm text-primary hover:underline">
              View observability →
            </Link>
          </CardContent>
        </Card>
      </div>

      {stats && stats.total_calls > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>LLM observability summary</CardTitle>
            <CardDescription>
              Success rate {((stats.success_rate ?? 0) * 100).toFixed(0)}% · avg latency{" "}
              {stats.avg_latency_ms?.toFixed(0)}ms · {stats.total_prompt_tokens + stats.total_completion_tokens}{" "}
              tokens total
            </CardDescription>
          </CardHeader>
        </Card>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
  href,
  cta,
}: {
  title: string;
  value: number | null;
  href: string;
  cta: string;
}) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardDescription>{title}</CardDescription>
        <CardTitle className="text-3xl">{value === null ? <Skeleton className="h-8 w-12" /> : value}</CardTitle>
      </CardHeader>
      <CardContent>
        <Link href={href} className="text-sm text-primary hover:underline">
          {cta} →
        </Link>
      </CardContent>
    </Card>
  );
}

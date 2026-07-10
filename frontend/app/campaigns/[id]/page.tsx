"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import {
  api,
  ApiError,
  type CampaignRead,
  type ContactRead,
  type DashboardStats,
  type ExportResult,
  type RunRead,
} from "@/lib/api";

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<CampaignRead | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [runs, setRuns] = useState<RunRead[]>([]);
  const [contacts, setContacts] = useState<ContactRead[]>([]);
  const [contactId, setContactId] = useState("");
  const [running, setRunning] = useState(false);
  const [runError, setRunError] = useState<string | null>(null);
  const [webhookUrl, setWebhookUrl] = useState("");
  const [exportResult, setExportResult] = useState<ExportResult | null>(null);
  const [exporting, setExporting] = useState(false);

  function refresh() {
    api.campaigns.get(id).then(setCampaign).catch(() => {});
    api.dashboard.get(id).then(setStats).catch(() => {});
    api.runs.list(id).then(setRuns).catch(() => {});
  }

  useEffect(() => {
    refresh();
    api.contacts.list().then((c) => {
      setContacts(c);
      if (c.length > 0) setContactId(c[0].id);
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function triggerRun() {
    if (!contactId) return;
    setRunning(true);
    setRunError(null);
    try {
      await api.runs.create({ campaign_id: id, contact_id: contactId });
      refresh();
    } catch (err) {
      setRunError(err instanceof ApiError ? err.detail : "Run failed");
    } finally {
      setRunning(false);
    }
  }

  async function runExport() {
    if (!webhookUrl.trim()) return;
    setExporting(true);
    try {
      setExportResult(await api.campaigns.export(id, webhookUrl));
    } catch (err) {
      setExportResult({
        delivered: false, run_count: 0, status_code: null,
        error: err instanceof ApiError ? err.detail : "Export failed",
      });
    } finally {
      setExporting(false);
    }
  }

  if (!campaign) return <Skeleton className="h-40 w-full" />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{campaign.name}</h1>
        <p className="text-muted-foreground">Status: {campaign.status}</p>
      </div>

      {stats && (
        <div className="grid gap-4 sm:grid-cols-4">
          <MetricCard label="Total runs" value={stats.total_runs} />
          <MetricCard label="Completed" value={stats.completed} />
          <MetricCard label="Failed" value={stats.failed} />
          <MetricCard label="Avg latency" value={stats.avg_latency_ms ? `${stats.avg_latency_ms.toFixed(0)}ms` : "—"} />
        </div>
      )}

      {stats && Object.keys(stats.outcome_counts).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Outcomes</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2">
            {Object.entries(stats.outcome_counts).map(([outcome, count]) => (
              <Badge key={outcome} variant="secondary">
                {outcome}: {count}
              </Badge>
            ))}
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Trigger a run</CardTitle>
          <CardDescription>
            Simulated channels return instantly-ish; the real email channel needs a configured
            RESEND_API_KEY and a real recipient address.
          </CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex gap-3">
            <Select value={contactId} onValueChange={(v) => setContactId(v ?? "")}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Choose a contact">
                  {() => contacts.find((c) => c.id === contactId)?.name ?? "Choose a contact"}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {contacts.map((c) => (
                  <SelectItem key={c.id} value={c.id}>
                    {c.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={triggerRun} disabled={running || !contactId}>
              {running ? "Running… (~5-30s)" : "Trigger run"}
            </Button>
          </div>
          {runError && <p className="text-destructive text-sm">{runError}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>{runs.length} run(s)</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Channel</TableHead>
                <TableHead>State</TableHead>
                <TableHead>Outcome</TableHead>
                <TableHead>Latency</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {runs.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{r.channel}</TableCell>
                  <TableCell>
                    <Badge variant={r.state === "completed" ? "default" : r.state === "failed" ? "destructive" : "outline"}>
                      {r.state}
                    </Badge>
                  </TableCell>
                  <TableCell>{r.outcome || r.error_reason || "—"}</TableCell>
                  <TableCell>{r.latency_ms ? `${r.latency_ms.toFixed(0)}ms` : "—"}</TableCell>
                  <TableCell>
                    <Link href={`/runs/${r.id}`} className="text-primary text-sm hover:underline">
                      View →
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
              {runs.length === 0 && (
                <TableRow>
                  <TableCell colSpan={5} className="text-muted-foreground text-center">
                    No runs yet.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Export to webhook</CardTitle>
          <CardDescription>Push run summaries to an external system (CRM, Zapier, etc.).</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="flex gap-3">
            <Input
              placeholder="https://your-webhook-url"
              value={webhookUrl}
              onChange={(e) => setWebhookUrl(e.target.value)}
            />
            <Button onClick={runExport} disabled={exporting || !webhookUrl.trim()}>
              {exporting ? "Exporting…" : "Export"}
            </Button>
          </div>
          {exportResult && (
            <p className={exportResult.delivered ? "text-sm text-green-600" : "text-destructive text-sm"}>
              {exportResult.delivered
                ? `Delivered ${exportResult.run_count} run(s) (HTTP ${exportResult.status_code})`
                : `Failed: ${exportResult.error}`}
            </p>
          )}
        </CardContent>
      </Card>
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

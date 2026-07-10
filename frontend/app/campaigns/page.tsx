"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { api, ApiError, type CampaignRead, type WorkflowTemplateRead } from "@/lib/api";

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<CampaignRead[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplateRead[]>([]);
  const [templateId, setTemplateId] = useState<string>("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    api.campaigns.list().then(setCampaigns).catch(() => {});
    api.workflowTemplates.list().then((t) => {
      setTemplates(t);
      if (t.length > 0 && !templateId) setTemplateId(t[0].id);
    });
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function submit() {
    if (!name.trim() || !templateId) return;
    setLoading(true);
    setError(null);
    try {
      await api.campaigns.create({ workflow_template_id: templateId, name });
      setName("");
      load();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to create campaign");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Campaigns</h1>
        <p className="text-muted-foreground">A campaign runs one workflow template against contacts.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New campaign</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <Input placeholder="Campaign name" value={name} onChange={(e) => setName(e.target.value)} />
            <Select value={templateId} onValueChange={(v) => setTemplateId(v ?? "")}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a template">
                  {() => {
                    const t = templates.find((t) => t.id === templateId);
                    return t ? `${t.name} (v${t.version}, ${t.channel})` : "Choose a template";
                  }}
                </SelectValue>
              </SelectTrigger>
              <SelectContent>
                {templates.map((t) => (
                  <SelectItem key={t.id} value={t.id}>
                    {t.name} (v{t.version}, {t.channel})
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div>
            <Button onClick={submit} disabled={loading || !templateId}>
              {loading ? "Creating…" : "Create campaign"}
            </Button>
          </div>
          {error && <p className="text-destructive text-sm">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>{campaigns.length} campaign(s)</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {campaigns.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-medium">{c.name}</TableCell>
                  <TableCell>{c.status}</TableCell>
                  <TableCell>
                    <Link href={`/campaigns/${c.id}`} className="text-primary text-sm hover:underline">
                      View →
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
              {campaigns.length === 0 && (
                <TableRow>
                  <TableCell colSpan={3} className="text-muted-foreground text-center">
                    No campaigns yet.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

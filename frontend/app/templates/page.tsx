"use client";

import { useEffect, useState } from "react";
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
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Textarea } from "@/components/ui/textarea";
import { api, ApiError, type RegressionReport, type WorkflowTemplateRead } from "@/lib/api";

const CHANNELS = ["email", "voice_simulated", "sms_simulated"] as const;

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<WorkflowTemplateRead[]>([]);
  const [name, setName] = useState("");
  const [channel, setChannel] = useState<string>("voice_simulated");
  const [goalPrompt, setGoalPrompt] = useState("");
  const [evalRubric, setEvalRubric] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [regression, setRegression] = useState<RegressionReport | null>(null);

  const load = () => api.workflowTemplates.list().then(setTemplates).catch(() => {});

  useEffect(() => {
    load();
  }, []);

  async function submit() {
    if (!name.trim() || !goalPrompt.trim() || !evalRubric.trim()) return;
    setLoading(true);
    setError(null);
    try {
      await api.workflowTemplates.create({ name, channel, goal_prompt: goalPrompt, eval_rubric: evalRubric });
      setName("");
      setGoalPrompt("");
      setEvalRubric("");
      await load();
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to create template");
    } finally {
      setLoading(false);
    }
  }

  async function checkRegression(templateName: string) {
    setRegression(await api.workflowTemplates.regression(templateName));
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Workflow templates</h1>
        <p className="text-muted-foreground">
          A goal + eval rubric per channel. Same name + higher version = a new revision of the same family,
          comparable via regression.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>New template</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div className="grid gap-3 sm:grid-cols-2">
            <Input placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} />
            <Select value={channel} onValueChange={(v) => setChannel(v ?? "")}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CHANNELS.map((c) => (
                  <SelectItem key={c} value={c}>
                    {c}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Textarea
            placeholder="Goal prompt — what should the outreach achieve?"
            value={goalPrompt}
            onChange={(e) => setGoalPrompt(e.target.value)}
            rows={2}
          />
          <Textarea
            placeholder="Eval rubric — how should a run be judged?"
            value={evalRubric}
            onChange={(e) => setEvalRubric(e.target.value)}
            rows={2}
          />
          <div>
            <Button onClick={submit} disabled={loading}>
              {loading ? "Creating…" : "Create template"}
            </Button>
          </div>
          {error && <p className="text-destructive text-sm">{error}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardDescription>{templates.length} template(s)</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Version</TableHead>
                <TableHead>Channel</TableHead>
                <TableHead />
              </TableRow>
            </TableHeader>
            <TableBody>
              {templates.map((t) => (
                <TableRow key={t.id}>
                  <TableCell className="font-medium">{t.name}</TableCell>
                  <TableCell>
                    <Badge variant="outline">v{t.version}</Badge>
                  </TableCell>
                  <TableCell>{t.channel}</TableCell>
                  <TableCell>
                    <button
                      className="text-primary text-sm hover:underline"
                      onClick={() => checkRegression(t.name)}
                    >
                      Regression →
                    </button>
                  </TableCell>
                </TableRow>
              ))}
              {templates.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} className="text-muted-foreground text-center">
                    No templates yet.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {regression && (
        <Card>
          <CardHeader>
            <CardTitle>Regression — {regression.name}</CardTitle>
            <CardDescription>Eval scores compared across versions of this template family.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Version</TableHead>
                  <TableHead>Runs</TableHead>
                  <TableHead>Avg rule score</TableHead>
                  <TableHead>Avg LLM score</TableHead>
                  <TableHead>Pass rate</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {regression.points.map((p) => (
                  <TableRow key={p.template_id}>
                    <TableCell>v{p.version}</TableCell>
                    <TableCell>{p.run_count}</TableCell>
                    <TableCell>{p.avg_rule_score ?? "—"}</TableCell>
                    <TableCell>{p.avg_llm_score ?? "—"}</TableCell>
                    <TableCell>{p.pass_rate !== null ? `${(p.pass_rate * 100).toFixed(0)}%` : "—"}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

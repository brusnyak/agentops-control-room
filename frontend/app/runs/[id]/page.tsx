"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { api, ApiError, type EvaluationRead, type RunDetailRead } from "@/lib/api";

export default function RunDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<RunDetailRead | null>(null);
  const [evaluations, setEvaluations] = useState<EvaluationRead[]>([]);
  const [evaluating, setEvaluating] = useState(false);
  const [evalError, setEvalError] = useState<string | null>(null);

  function refresh() {
    api.runs.get(id).then(setRun).catch(() => {});
    api.evals.list(id).then(setEvaluations).catch(() => {});
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function runEvaluation() {
    setEvaluating(true);
    setEvalError(null);
    try {
      await api.evals.create(id);
      refresh();
    } catch (err) {
      setEvalError(err instanceof ApiError ? err.detail : "Evaluation failed");
    } finally {
      setEvaluating(false);
    }
  }

  if (!run) return <Skeleton className="h-40 w-full" />;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Run — {run.channel}</h1>
        <div className="mt-1 flex items-center gap-2">
          <Badge variant={run.state === "completed" ? "default" : run.state === "failed" ? "destructive" : "outline"}>
            {run.state}
          </Badge>
          {run.outcome && <Badge variant="secondary">{run.outcome}</Badge>}
          {run.latency_ms && <span className="text-muted-foreground text-sm">{run.latency_ms.toFixed(0)}ms</span>}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Transcript</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {run.messages.map((m) => (
            <div key={m.id} className={`rounded-md border p-3 ${m.direction === "outbound" ? "bg-muted/40" : ""}`}>
              <p className="text-muted-foreground text-xs uppercase">
                {m.direction} · {m.provider}
              </p>
              <p className="text-sm">{m.content}</p>
            </div>
          ))}
          {run.messages.length === 0 && <p className="text-muted-foreground text-sm">No messages logged.</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Tool calls</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-2">
          {run.tool_calls.map((tc) => (
            <div key={tc.id} className="rounded-md border p-3 text-sm">
              <p className="font-medium">
                {tc.tool_name} — <Badge variant={tc.success ? "default" : "destructive"}>{tc.success ? "success" : "failed"}</Badge>
              </p>
              <pre className="text-muted-foreground mt-1 overflow-x-auto text-xs">
                {JSON.stringify(tc.output, null, 2)}
              </pre>
            </div>
          ))}
          {run.tool_calls.length === 0 && <p className="text-muted-foreground text-sm">No tool calls logged.</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Evaluation</CardTitle>
          <CardDescription>Rule checks + LLM-as-judge against the workflow&apos;s rubric.</CardDescription>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <div>
            <Button onClick={runEvaluation} disabled={evaluating}>
              {evaluating ? "Evaluating…" : "Run evaluation"}
            </Button>
          </div>
          {evalError && <p className="text-destructive text-sm">{evalError}</p>}
          {evaluations.map((e) => (
            <div key={e.id} className="rounded-md border p-3">
              <div className="flex items-center gap-2">
                <Badge variant={e.passed ? "default" : "destructive"}>{e.passed ? "passed" : "failed"}</Badge>
                <span className="text-sm">rule: {(e.rule_score * 100).toFixed(0)}%</span>
                {e.llm_score !== null && <span className="text-sm">llm: {e.llm_score}/100</span>}
              </div>
              {e.notes && <p className="mt-1 text-sm">{e.notes}</p>}
              {e.failure_tags && e.failure_tags.length > 0 && (
                <div className="mt-1 flex flex-wrap gap-1">
                  {e.failure_tags.map((tag) => (
                    <Badge key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

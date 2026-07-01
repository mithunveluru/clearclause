"use client";
import {
  AlertTriangle, BookOpen, Calendar, DollarSign, Eye,
  HelpCircle, Map, MessageSquare, RotateCcw, Shield, Sparkles,
} from "lucide-react";
import { bandMeta, severityMeta } from "@/lib/ui";
import type { ExplorerDoc, ExplorerSection } from "@/lib/api";
import type { ReadingMode } from "./ClauseCard";

const SECTION_ICONS: Record<string, React.ElementType> = {
  DollarSign, AlertTriangle, Eye, Shield, RotateCcw,
};

const NAV_ITEMS = [
  { id: "overview",     label: "Overview",        Icon: Map },
  { id: "financial",    label: "Financial Impact", Icon: DollarSign },
  { id: "timeline",     label: "Timeline",         Icon: Calendar },
  { id: "questions",    label: "Questions",        Icon: HelpCircle },
  { id: "qa",           label: "Ask Anything",     Icon: MessageSquare },
  { id: "strengths",    label: "What's Good",      Icon: Sparkles },
];

const MODE_OPTIONS: { id: ReadingMode; label: string; Icon: React.ElementType }[] = [
  { id: "consumer",     label: "Consumer",     Icon: BookOpen },
  { id: "professional", label: "Professional", Icon: Eye },
  { id: "negotiation",  label: "Negotiation",  Icon: MessageSquare },
  { id: "financial",    label: "Financial",    Icon: DollarSign },
];

export function ExplorerNav({
  explorer,
  active,
  onSelect,
  mode,
  onMode,
  onWalkthrough,
}: {
  explorer: ExplorerDoc;
  active: string;
  onSelect: (id: string) => void;
  mode: ReadingMode;
  onMode: (m: ReadingMode) => void;
  onWalkthrough: () => void;
}) {
  const band = explorer.risk_band;
  const bm = band ? bandMeta(band) : null;

  return (
    <nav className="flex flex-col gap-1 py-6">
      {bm && band && (
        <div
          className="mb-5 rounded-2xl px-4 py-3.5"
          style={{ backgroundColor: bm.tint, border: `1px solid ${bm.color}26` }}
        >
          <p className="text-[0.6875rem] font-semibold uppercase tracking-[0.08em]" style={{ color: bm.color }}>
            {bm.tone}
          </p>
          {explorer.risk_score != null && (
            <p className="mt-0.5 text-[1.5rem] font-bold tracking-tight leading-none" style={{ color: bm.color }}>
              {explorer.risk_score}<span className="text-[0.875rem] font-normal ml-1 opacity-70">/100</span>
            </p>
          )}
        </div>
      )}

      {explorer.walkthrough.length > 0 && (
        <button
          onClick={onWalkthrough}
          className="mb-4 flex w-full items-center justify-center gap-2 rounded-xl border border-brand/20 bg-brand/5 px-4 py-2.5 text-[0.875rem] font-semibold text-brand transition hover:bg-brand/10"
        >
          <Sparkles className="h-4 w-4" strokeWidth={1.75} />
          Guided Walkthrough
        </button>
      )}

      <p className="mb-1.5 px-3 text-[0.6875rem] font-semibold uppercase tracking-[0.09em] text-ink-3">
        Reading Mode
      </p>
      <div className="mb-4 grid grid-cols-2 gap-1 rounded-xl bg-canvas p-1">
        {MODE_OPTIONS.map(({ id, label }) => (
          <button
            key={id}
            onClick={() => onMode(id)}
            className={`rounded-lg px-2 py-1.5 text-[0.75rem] font-medium transition ${
              mode === id
                ? "bg-surface shadow-xs text-ink font-semibold"
                : "text-ink-3 hover:text-ink"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {explorer.sections.length > 0 && (
        <>
          <p className="mb-1.5 px-3 text-[0.6875rem] font-semibold uppercase tracking-[0.09em] text-ink-3">
            Findings
          </p>
          {explorer.sections.map((s) => (
            <SectionNavItem
              key={s.id}
              section={s}
              active={active === s.id}
              onClick={() => onSelect(s.id)}
            />
          ))}
        </>
      )}

      <p className="mb-1.5 mt-4 px-3 text-[0.6875rem] font-semibold uppercase tracking-[0.09em] text-ink-3">
        Explore
      </p>
      {NAV_ITEMS.filter((n) => {
        if (n.id === "strengths" && !explorer.strengths?.length) return false;
        if (n.id === "timeline" && !explorer.timeline?.length) return false;
        return true;
      }).map(({ id, label, Icon }) => (
        <button
          key={id}
          onClick={() => onSelect(id)}
          className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-[0.875rem] transition text-left ${
            active === id
              ? "bg-brand/[0.08] font-semibold text-brand"
              : "text-ink-2 hover:bg-canvas hover:text-ink"
          }`}
        >
          <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
          {label}
        </button>
      ))}
    </nav>
  );
}

function SectionNavItem({
  section,
  active,
  onClick,
}: {
  section: ExplorerSection;
  active: boolean;
  onClick: () => void;
}) {
  const sev = severityMeta(section.risk_level);
  const Icon = SECTION_ICONS[section.icon] ?? AlertTriangle;

  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-[0.875rem] transition text-left ${
        active
          ? "bg-brand/[0.08] font-semibold text-brand"
          : "text-ink-2 hover:bg-canvas hover:text-ink"
      }`}
    >
      <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} />
      <span className="flex-1">{section.label}</span>
      <span
        className="h-2 w-2 rounded-full shrink-0"
        style={{ backgroundColor: sev.color }}
        title={`${sev.label} risk`}
      />
      <span className="text-[0.75rem] text-ink-3">{section.item_count}</span>
    </button>
  );
}

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";

type Msg = { role: "user" | "assistant"; content: string };

const SUGGESTIONS = [
  "¿Qué factor explica más el nivel de ventas?",
  "¿Los descuentos están destruyendo el beneficio?",
  "¿Qué región y segmento debería priorizar?",
  "¿Cómo es la distribución de Sales? ¿Por qué usar log?",
];

export function AnalystChat({
  pending,
  onConsumed,
  context,
}: {
  pending: string | null;
  onConsumed: () => void;
  context: string;
}) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (pending && !busy) {
      setOpen(true);
      void send(pending);
      onConsumed();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pending]);

  async function send(text: string) {
    const q = text.trim();
    if (!q || busy) return;
    setError(null);
    const history: Msg[] = [...messages, { role: "user", content: q }];
    setMessages([...history, { role: "assistant", content: "" }]);
    setInput("");
    setBusy(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: history, context }),
      });
      if (!res.ok || !res.body) {
        const j = await res.json().catch(() => ({}));
        throw new Error(j.error ?? "No se pudo obtener respuesta.");
      }
      const reader = res.body.getReader();
      const dec = new TextDecoder();
      let buf = "";
      let acc = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        const lines = buf.split("\n");
        buf = lines.pop() ?? "";
        for (const line of lines) {
          if (!line.startsWith("data:")) continue;
          const data = line.slice(5).trim();
          if (!data) continue;
          try {
            const ev = JSON.parse(data) as
              | { type: "delta"; text: string }
              | { type: "error"; message: string }
              | { type: "done" };
            if (ev.type === "delta") {
              acc += ev.text;
              setMessages((m) => [...m.slice(0, -1), { role: "assistant", content: acc }]);
            } else if (ev.type === "error") {
              throw new Error(ev.message);
            }
          } catch (e) {
            if (e instanceof Error && e.message !== "" && !(e instanceof SyntaxError)) throw e;
          }
        }
      }
      if (!acc) throw new Error("El asistente no devolvió respuesta.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error inesperado");
      setMessages((m) => (m[m.length - 1]?.content === "" ? m.slice(0, -1) : m));
    } finally {
      setBusy(false);
    }
  }

  if (!open)
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-5 right-5 z-50 flex items-center gap-2 rounded-2xl bg-primary px-4 py-3 font-mono text-sm font-semibold text-primary-foreground shadow-[var(--shadow-glass)] transition-transform hover:-translate-y-0.5"
      >
        <span className="grid size-6 place-items-center rounded-md bg-primary-foreground/20 text-[11px]">
          IA
        </span>
        Preguntar al analista
      </button>
    );

  return (
    <div className="glass fixed bottom-5 right-5 z-50 flex h-[min(560px,calc(100vh-2.5rem))] w-[min(400px,calc(100vw-2.5rem))] flex-col rounded-2xl bg-card p-4">
      <div className="flex items-center gap-3">
        <span className="grid size-9 place-items-center rounded-lg bg-primary font-mono text-sm font-semibold text-primary-foreground">
          IA
        </span>
        <div>
          <h2 className="font-mono text-sm font-semibold tracking-tight">Analista de negocio</h2>
          <p className="text-[11px] text-muted-foreground">Pregunta en lenguaje natural</p>
        </div>
        <span className="ml-auto inline-flex items-center gap-1.5 rounded-full bg-primary-soft px-2.5 py-1">
          <span className="size-1.5 animate-pulse rounded-full bg-primary" />
          <span className="font-mono text-[10px] text-primary">en línea</span>
        </span>
        <button
          onClick={() => setOpen(false)}
          aria-label="Cerrar"
          className="grid size-7 place-items-center rounded-md text-muted-foreground hover:bg-muted"
        >
          ✕
        </button>
      </div>

      <div ref={scrollRef} className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <div className="rounded-2xl border border-border bg-card p-4 text-[13px] leading-relaxed text-muted-foreground">
            Conozco las estadísticas de los datos cargados (con tus filtros): distribución de Sales,
            pedidos por categoría, región y segmento, y correlaciones con descuento, cantidad y
            beneficio. Pregúntame lo que necesites decidir.
          </div>
        )}
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div
              key={i}
              className="ml-auto max-w-[88%] rounded-2xl rounded-tr-sm bg-primary px-3.5 py-2.5 text-[13px] text-primary-foreground"
            >
              {m.content}
            </div>
          ) : (
            <div
              key={i}
              className="prose-chat max-w-[96%] text-[13px] leading-relaxed text-foreground"
            >
              {m.content ? (
                <ReactMarkdown>{m.content}</ReactMarkdown>
              ) : (
                <span className="font-mono text-xs text-muted-foreground">Analizando datos…</span>
              )}
            </div>
          ),
        )}
        {error && (
          <div className="rounded-xl bg-negative/10 px-3 py-2 text-xs text-negative">{error}</div>
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {messages.length === 0 &&
          SUGGESTIONS.map((s) => (
            <button
              key={s}
              disabled={busy}
              onClick={() => send(s)}
              className="rounded-full border border-border bg-card px-3 py-1.5 text-left text-[11px] font-medium transition-colors hover:border-primary/50 hover:bg-primary-soft disabled:opacity-50"
            >
              {s}
            </button>
          ))}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void send(input);
        }}
        className="mt-3 flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Escribe tu pregunta de negocio…"
          className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          aria-label="Enviar"
          className="grid size-8 place-items-center rounded-lg bg-primary text-primary-foreground transition-transform hover:-translate-y-0.5 disabled:opacity-40"
        >
          →
        </button>
      </form>
    </div>
  );
}

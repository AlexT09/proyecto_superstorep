import { createFileRoute } from "@tanstack/react-router";
import { z } from "zod";
import Anthropic from "@anthropic-ai/sdk";

const Body = z.object({
  messages: z
    .array(z.object({ role: z.enum(["user", "assistant"]), content: z.string().max(4000) }))
    .min(1)
    .max(40),
  context: z.string().min(2).max(30000),
});

const SYSTEM = `Eres "Analista", un consultor de inteligencia de negocio que responde en español.
Proyecto: determinar qué factores (Category, Region, Segment) explican el nivel de ventas (Sales) del dataset Sample Superstore, describir la distribución de Sales (y log(Sales)), la distribución de pedidos por variables categóricas y la relación de Sales con Discount, Quantity y Profit.
Usa EXCLUSIVAMENTE estas estadísticas precalculadas del dataset cargado actualmente (con los filtros activos):
{{CTX}}
Reglas: responde con un titular en negrita con el hallazgo clave, luego 2-4 viñetas con cifras concretas, y cierra con una recomendación de negocio breve. Interpreta eta² (proporción de varianza de log(Sales) explicada) y correlaciones con lenguaje claro. Si algo no se puede responder con estos datos, dilo. Sé conciso (máx. ~180 palabras). Usa markdown.`;

type ChatEvent =
  { type: "delta"; text: string } | { type: "error"; message: string } | { type: "done" };

export const Route = createFileRoute("/api/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const parsed = Body.safeParse(await request.json().catch(() => null));
        if (!parsed.success) return Response.json({ error: "Solicitud inválida" }, { status: 400 });
        const apiKey = process.env["ANTHROPIC_API_KEY"];
        if (!apiKey)
          return Response.json(
            { error: "Falta configurar ANTHROPIC_API_KEY en el servidor." },
            { status: 500 },
          );

        const client = new Anthropic({ apiKey });
        const encoder = new TextEncoder();
        const send = (controller: ReadableStreamDefaultController<Uint8Array>, ev: ChatEvent) => {
          controller.enqueue(encoder.encode(`data: ${JSON.stringify(ev)}\n\n`));
        };

        const body = new ReadableStream<Uint8Array>({
          async start(controller) {
            try {
              const stream = client.messages.stream({
                model: "claude-opus-5",
                max_tokens: 4096,
                system: SYSTEM.replace("{{CTX}}", parsed.data.context),
                messages: parsed.data.messages.map((m) => ({ role: m.role, content: m.content })),
              });
              for await (const event of stream) {
                if (request.signal.aborted) break;
                if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
                  send(controller, { type: "delta", text: event.delta.text });
                }
              }
              const final = await stream.finalMessage();
              if (final.stop_reason === "refusal") {
                send(controller, {
                  type: "error",
                  message: "El asistente no pudo responder a esta pregunta.",
                });
              } else {
                send(controller, { type: "done" });
              }
            } catch (e) {
              console.error("Anthropic chat error", e);
              const message =
                e instanceof Anthropic.RateLimitError
                  ? "Demasiadas solicitudes, intenta en un momento."
                  : e instanceof Anthropic.AuthenticationError
                    ? "La API key configurada no es válida."
                    : e instanceof Anthropic.APIError
                      ? "El asistente no está disponible ahora mismo."
                      : "Error inesperado del asistente.";
              send(controller, { type: "error", message });
            } finally {
              controller.close();
            }
          },
        });

        return new Response(body, {
          headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-store" },
        });
      },
    },
  },
});

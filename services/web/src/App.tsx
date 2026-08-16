import { useState } from "react";
import { ChatInput } from "./components/ChatInput";
import { ProductGrid } from "./components/ProductGrid";
import { sendChatQuery, fetchSearchPage } from "./api/client";
import type { ChatMessage } from "./api/types";
import "./App.css";

function newId(): string {
  return Math.random().toString(36).slice(2);
}

export default function App() {
  const [tenantId, setTenantId] = useState("demo");
  const [env, setEnv] = useState("dev");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend(query: string) {
    const userMessage: ChatMessage = { id: newId(), role: "user", text: query };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);
    setError(null);
    try {
      const response = await sendChatQuery(query, { tenantId, env });
      const assistantMessage: ChatMessage = {
        id: newId(),
        role: "assistant",
        text: response.answer,
        searchId: response.search_id,
        results: response.results,
        offset: response.offset,
        limit: response.limit,
        hasMore: response.has_more,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handlePage(messageId: string, direction: "next" | "prev") {
    const message = messages.find((m) => m.id === messageId);
    if (!message?.searchId || message.offset == null || message.limit == null) return;

    const newOffset =
      direction === "next"
        ? message.offset + message.limit
        : Math.max(0, message.offset - message.limit);

    setLoading(true);
    setError(null);
    try {
      const page = await fetchSearchPage(message.searchId, newOffset, message.limit);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === messageId
            ? { ...m, results: page.results, offset: page.offset, hasMore: page.has_more }
            : m,
        ),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Shopping Agent</h1>
        <div className="app__tenant-settings">
          <label>
            Tenant
            <input value={tenantId} onChange={(e) => setTenantId(e.target.value)} />
          </label>
          <label>
            Env
            <input value={env} onChange={(e) => setEnv(e.target.value)} />
          </label>
        </div>
      </header>

      <main className="app__thread">
        {messages.length === 0 && (
          <div className="app__empty">
            Ask for something, e.g. &ldquo;find me a red jacket for fall&rdquo;.
          </div>
        )}
        {messages.map((message) => (
          <div key={message.id} className={`message message--${message.role}`}>
            <div className="message__bubble">{message.text}</div>
            {message.role === "assistant" &&
              message.searchId &&
              message.results &&
              message.offset != null && (
                <ProductGrid
                  results={message.results}
                  offset={message.offset}
                  hasMore={message.hasMore ?? false}
                  loading={loading}
                  onPrev={() => handlePage(message.id, "prev")}
                  onNext={() => handlePage(message.id, "next")}
                />
              )}
          </div>
        ))}
        {loading && <div className="app__loading">Thinking…</div>}
        {error && <div className="app__error">{error}</div>}
      </main>

      <ChatInput disabled={loading} onSubmit={handleSend} />
    </div>
  );
}

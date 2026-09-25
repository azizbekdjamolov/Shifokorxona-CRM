import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  getConversations,
  getConversationMessages,
  sendMessage,
} from "../api/chatsApi";
import { useAuth } from "../context/AuthContext";

export default function ChatPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [conversations, setConversations] = useState([]);
  const [active, setActive] = useState(null);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(true);
  const bottomRef = useRef(null);

  useEffect(() => {
    getConversations()
      .then((res) => {
        const list = res.data.results || res.data;
        setConversations(list);
        const fromQuery = searchParams.get("chat");
        const initial = fromQuery
          ? list.find((c) => String(c.id) === fromQuery)
          : list[0];
        if (initial) setActive(initial);
      })
      .finally(() => setLoading(false));
  }, []);

  const openChat = (conv) => {
    setActive(conv);
    setSearchParams({ chat: String(conv.id) }, { replace: true });
  };

  useEffect(() => {
    if (!active) return;
    getConversationMessages(active.id)
      .then((res) => setMessages(res.data.results || res.data))
      .catch(() => setMessages([]));
  }, [active?.id]);

  useLayoutEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async (e) => {
    e.preventDefault();
    if (!text.trim() || !active) return;
    const value = text;
    setText("");
    try {
      await sendMessage(active.id, value);
      const res = await getConversationMessages(active.id);
      setMessages(res.data.results || res.data);
    } catch {
      setText(value);
    }
  };

  const isOwn = (m) => String(m.sender_id) === String(user?.id);
  const isPatient = user?.role === "patient";

  return (
    <div className="chat-page">
      <h1>💬 {t("chat.title")}</h1>
      <div className="chat-layout">
        <aside className="chat-list">
          {conversations.map((c) => (
            <button
              key={c.id}
              className={`chat-item ${active?.id === c.id ? "chat-item-active" : ""}`}
              onClick={() => openChat(c)}
            >
              <b>
                {isPatient ? c.doctor_name : c.patient_name} {c.unread_count > 0 && <span className="chat-badge">{c.unread_count}</span>}
              </b>
              <span className="hint">
                {isPatient ? c.specialty_name : c.patient_name} •{" "}
                {c.last_message?.text?.slice(0, 30) || t("chat.empty")}
              </span>
            </button>
          ))}
        </aside>

        <section className="chat-window">
          {!active ? (
            <p className="empty-state">{t("chat.select")}</p>
          ) : (
            <>
              <header className="chat-window-head">
                {isPatient
                  ? `Dr. ${active.doctor_name} (${active.specialty_name})`
                  : active.patient_name}
              </header>
              <div className="chat-messages">
                {messages.map((m) => (
                  <div key={m.id} className={`chat-bubble ${isOwn(m) ? "chat-bubble-own" : ""}`}>
                    <p>{m.text}</p>
                    <span className="hint">
                      {isOwn(m) ? "Siz" : m.sender_name} • {m.created_at?.slice(11, 16)}
                    </span>
                  </div>
                ))}
                <div ref={bottomRef} />
              </div>
              <form className="chat-input" onSubmit={send}>
                <input
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                  placeholder={t("chat.placeholder")}
                />
                <button className="btn btn-primary" type="submit">
                  {t("common.send")}
                </button>
              </form>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
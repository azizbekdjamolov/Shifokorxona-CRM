import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { getAiMessages, sendAiMessage } from "../api/aiApi";

const ACCEPTED = ["image/jpeg", "image/png", "image/webp"];
const MAX_SIZE = 10 * 1024 * 1024;

export default function AiChatPage() {
  const { t, i18n } = useTranslation();
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [pickedImage, setPickedImage] = useState(null);
  const [preview, setPreview] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);
  const fileInputRef = useRef(null);

  useEffect(() => {
    getAiMessages()
      .then((res) => {
        setMessages(Array.isArray(res.data) ? res.data : []);
      })
      .catch(() => {
        setError(t("ai.loadError"));
      })
      .finally(() => setHistoryLoaded(true));
  }, []);

  useLayoutEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const resetImage = () => {
    setPickedImage(null);
    setPreview("");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const pickFile = (file) => {
    setError("");
    if (!file) return;
    if (!ACCEPTED.includes(file.type)) {
      setError(t("ai.badFormat"));
      return;
    }
    if (file.size > MAX_SIZE) {
      setError(t("ai.tooLarge"));
      return;
    }
    setPickedImage(file);
    setPreview(URL.createObjectURL(file));
  };

  const onFileChange = (e) => pickFile(e.target.files?.[0]);

  const onDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    pickFile(e.dataTransfer?.files?.[0]);
  };

  const quickAction = (action) => {
    const question = t(`ai.quick.${action}`);
    setText(question);
    inputRef.current?.focus();
    if (action === "analyzeImage") {
      fileInputRef.current?.click();
      return;
    }
    submitWith(question);
  };

  const submit = (e) => {
    e.preventDefault();
    submitWith(text);
  };

  const submitWith = async (messageText) => {
    if (sending) return;
    const image = pickedImage;
    if (!messageText.trim() && !image) return;
    setSending(true);
    setError("");
    setText("");
    resetImage();
    try {
      const res = await sendAiMessage({
        message: messageText.trim(),
        image,
        language: i18n.language,
      });
      setMessages((prev) => [
        ...prev,
        res.data.user_message,
        ...(res.data.assistant_message ? [res.data.assistant_message] : []),
      ]);
    } catch (err) {
      setError(t("ai.sendError"));
      if (messageText) setText(messageText);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="ai-page">
      <header className="ai-header">
        <div>
          <h1>🧠 Shifoxona AI</h1>
          <p className="hint">{t("ai.tagline")}</p>
        </div>
      </header>

      <div
        className={`ai-chat ${dragActive ? "ai-chat-drag" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
      >
        {dragActive && (
          <div className="ai-drop-overlay">
            <p>{t("ai.dropHere")}</p>
          </div>
        )}

        <div className="ai-messages">
          {!historyLoaded && <div className="spinner" />}

          {(messages.length === 0 || !historyLoaded) && historyLoaded && (
            <div className="ai-greeting">
              <div className="ai-greeting-avatar">🧠</div>
              <h2>{t("ai.greeting")}</h2>
              <p>{t("ai.greetingText")}</p>
              <div className="ai-quick-actions">
                {["medicines", "doctors", "queue", "prescriptions", "clinic"].map(
                  (a) => (
                    <button
                      key={a}
                      className="btn btn-outline"
                      onClick={() => quickAction(a)}
                      disabled={sending}
                    >
                      {t(`ai.quick.${a}`)}
                    </button>
                  )
                )}
                <button
                  className="btn btn-outline"
                  onClick={() => quickAction("analyzeImage")}
                  disabled={sending}
                >
                  🖼️ {t("ai.analyzeImage")}
                </button>
              </div>
            </div>
          )}

          {messages.length > 0 && messages.map((m) => (
            <div
              key={m.id}
              className={`chat-bubble ${m.role === "user" ? "chat-bubble-own ai-bubble-user" : "ai-bubble-ai"}`}
            >
              {m.role === "user" ? (
                <>
                  {m.image && (
                    <img
                      className="ai-msg-image"
                      src={m.image_url || m.image}
                      alt="rasm"
                      loading="lazy"
                    />
                  )}
                  {m.text && <p>{m.text}</p>}
                </>
              ) : (
                <>
                  {m.image && (
                    <img
                      className="ai-msg-image"
                      src={m.image_url || m.image}
                      alt="rasm"
                      loading="lazy"
                    />
                  )}
                  {m.text && <p className="ai-reply-text">{m.text}</p>}
                </>
              )}
            </div>
          ))}

          {sending && (
            <div className="chat-bubble ai-bubble-ai ai-typing">
              <span />
              <span />
              <span />
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {error && <p className="error-text ai-error">{error}</p>}

        <form className="ai-input-row" onSubmit={submit}>
          {preview && (
            <div className="ai-preview">
              <img src={preview} alt="preview" />
              <button
                type="button"
                className="modal-close ai-preview-remove"
                onClick={resetImage}
                aria-label={t("ai.removeImage")}
              >
                ✕
              </button>
            </div>
          )}
          <div className="ai-input-bar">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/*"
              hidden
              onChange={onFileChange}
            />
            <button
              type="button"
              className="ai-attach"
              onClick={() => fileInputRef.current?.click()}
              aria-label={t("ai.uploadImage")}
              title={t("ai.uploadImage")}
            >
              🖼️
            </button>
            <input
              ref={inputRef}
              className="ai-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder={t("ai.placeholder")}
              disabled={sending}
            />
            <button className="btn btn-primary ai-send" type="submit" disabled={sending}>
              ➤
            </button>
          </div>
          <p className="hint ai-input-hint">
            {t("ai.supported")} • {t("ai.dragHint")}
          </p>
        </form>
      </div>
    </div>
  );
}
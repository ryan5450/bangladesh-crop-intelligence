"use client";

import React, { useState, useEffect, useRef } from "react";
import Image from "next/image";
import {
  Send,
  Sparkles,
  Bot,
  User,
  BookOpen,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  RotateCcw,
  Cpu,
  Layers,
  ChevronDown,
  ChevronUp,
  Mic,
  MicOff,
  Volume2,
  Globe,
  X
} from "lucide-react";
import {
  chatWithAssistant,
  streamChatWithAssistant,
  getAssistantHealth,
  AssistantChatResponse,
  SourceCitation,
  AssistantHealthResponse,
} from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  detected_language?: string;
  timestamp: string;
}

const SAMPLE_PROMPTS = [
  { label: "🌾 বোরো ধানের সার মাত্রা", query: "বোরো ধানের জন্য ইউরিয়া, টিএসপি ও পটাশ সারের অনুমোদিত মাত্রা কত?" },
  { label: "🍂 ধানের ব্লাস্ট রোগ দমন", query: "ধানের ব্লাস্ট রোগের লক্ষণ ও অনুমোদিত ছত্রাকনাশক প্রতিকার কী?" },
  { label: "💧 Salinity Tolerant Rice", query: "Which BRRI rice varieties are best suited for coastal saline zones?" },
  { label: "📊 BRRI dhan28 vs dhan29", query: "Compare the yield, duration, and disease susceptibility of BRRI dhan28 and dhan29" },
  { label: "🌾 গম ফসলের মরিচা রোগ", query: "গম ফসলের পাতা মরিচা (leaf rust) রোগ দমনে BARI-এর সুপারিশ কী?" },
];

const CATEGORIES = [
  { id: "", name: "All Topics" },
  { id: "cereals", name: "Cereals (ধান/গম)" },
  { id: "diseases", name: "Diseases (রোগবালাই)" },
  { id: "fertilizer_management", name: "Fertilizer (সার)" },
  { id: "soil_management", name: "Soil & Salinity (মাটি)" },
  { id: "climate_adaptation", name: "Climate & Drought (খরা)" },
];

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Welcome! I am the Bangladesh Crop Intelligence Assistant (বাংলাদেশ কৃষি বুদ্ধিমত্তা সহকারী).\n\nYou can ask any questions regarding crop varieties, seasonal schedules, fertilizer dosages, pest and disease treatments, and official research from BRRI, BARI, DAE, and FAO.\n\nBy default, I provide all answers in English. You are welcome to type or speak your questions in English, বাংলা, or Banglish (if you ever need an answer in Bangla, simply ask me to reply in Bangla!).",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [health, setHealth] = useState<AssistantHealthResponse | null>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  // Voice Speech-to-Text State (Default: English)
  const [isListening, setIsListening] = useState(false);
  const [speechLang, setSpeechLang] = useState<"bn-BD" | "en-US">("en-US");
  const [speechError, setSpeechError] = useState<string | null>(null);
  const recognitionRef = useRef<any>(null);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const restartTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const isUserIntendedListening = useRef(false);
  const accumulatedTranscriptRef = useRef("");
  const activeSessionTranscriptRef = useRef("");

  // Scroll Management
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const userScrolledUp = useRef(false);
  const isInitialMount = useRef(true);
  const [showScrollBottomBtn, setShowScrollBottomBtn] = useState(false);

  const handleScroll = () => {
    const el = messagesContainerRef.current;
    if (!el) return;
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 80;
    userScrolledUp.current = !isNearBottom;
    setShowScrollBottomBtn(!isNearBottom);
  };

  const scrollToBottom = (force = false) => {
    if (force || !userScrolledUp.current) {
      if (messagesContainerRef.current) {
        messagesContainerRef.current.scrollTo({
          top: messagesContainerRef.current.scrollHeight,
          behavior: force ? "smooth" : "auto",
        });
      }
    }
  };

  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      // Do NOT auto-scroll on initial load so the user sees the top banner & welcome header
      return;
    }
    scrollToBottom();
  }, [messages, loading]);

  useEffect(() => {
    getAssistantHealth()
      .then((data) => setHealth(data))
      .catch((err) => console.error("Health check error:", err));

    return () => {
      clearSilenceTimer();
      clearRestartTimer();
      if (recognitionRef.current) {
        try {
          recognitionRef.current.onend = null;
          recognitionRef.current.stop();
        } catch {
          // ignore
        }
      }
    };
  }, []);

  const clearSilenceTimer = () => {
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
  };

  const clearRestartTimer = () => {
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current);
      restartTimeoutRef.current = null;
    }
  };

  const stopListening = () => {
    isUserIntendedListening.current = false;
    clearSilenceTimer();
    clearRestartTimer();
    if (recognitionRef.current) {
      try {
        recognitionRef.current.onend = null;
        recognitionRef.current.stop();
      } catch {
        // ignore
      }
      recognitionRef.current = null;
    }
    setIsListening(false);
  };

  const resetSilenceTimer = () => {
    clearSilenceTimer();
    // Standard conversational silence threshold: 3.0 seconds after last word spoken
    silenceTimerRef.current = setTimeout(() => {
      stopListening();
    }, 3000);
  };

  const startRecognitionSession = (SpeechRecognitionClass: any) => {
    if (!isUserIntendedListening.current) return;

    try {
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = speechLang;

      const isBrave =
        typeof window !== "undefined" &&
        Boolean((navigator as any).brave && typeof (navigator as any).brave.isBrave === "function");

      recognition.onstart = () => {
        setIsListening(true);
        setSpeechError(null);
      };

      recognition.onresult = (event: any) => {
        let sessionFinal = "";
        let sessionInterim = "";

        for (let i = 0; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            sessionFinal += event.results[i][0].transcript + " ";
          } else {
            sessionInterim += event.results[i][0].transcript;
          }
        }

        activeSessionTranscriptRef.current = (sessionFinal + sessionInterim).trim();
        const combined = [accumulatedTranscriptRef.current, activeSessionTranscriptRef.current]
          .filter(Boolean)
          .join(" ")
          .trim();

        if (combined) {
          setInput(combined);
          // User spoke something, reset the 3-second silence timer
          resetSilenceTimer();
        }
      };

      recognition.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        if (event.error === "no-speech") {
          // Normal when user pauses or hasn't started speaking yet
          return;
        }

        if (event.error === "not-allowed") {
          stopListening();
          setSpeechError(
            "Microphone permission was blocked. Please click the lock or settings icon in your browser URL bar and allow microphone access."
          );
        } else if (event.error === "network") {
          stopListening();
          if (isBrave) {
            setSpeechError(
              "Brave Browser blocks Google speech recognition by default. To enable: Go to brave://settings/shields or Privacy & Security and turn ON 'Use Google services for speech recognition', or open CropIntel in Google Chrome / Microsoft Edge."
            );
          } else {
            setSpeechError(
              "Browser Speech Service Network Error: The browser's speech engine could not connect to its cloud server. Check internet connection, VPN, or ad-blocker."
            );
          }
        } else if (event.error === "audio-capture") {
          stopListening();
          setSpeechError(
            "Audio capture failed. Ensure your microphone is plugged in and not exclusively locked by another application."
          );
        }
      };

      recognition.onend = () => {
        // Commit current session's words to accumulated text
        if (activeSessionTranscriptRef.current) {
          accumulatedTranscriptRef.current = [
            accumulatedTranscriptRef.current,
            activeSessionTranscriptRef.current,
          ]
            .filter(Boolean)
            .join(" ")
            .trim();
          activeSessionTranscriptRef.current = "";
        }

        // If the user intended to keep speaking and the 3s silence timeout hasn't ended the session,
        // restart recognition safely after a 100ms pause to let Chrome's audio engine reset
        if (isUserIntendedListening.current) {
          clearRestartTimer();
          restartTimeoutRef.current = setTimeout(() => {
            if (isUserIntendedListening.current) {
              startRecognitionSession(SpeechRecognitionClass);
            }
          }, 100);
        } else {
          setIsListening(false);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      console.error("Failed to start speech recognition:", err);
      if (isUserIntendedListening.current) {
        clearRestartTimer();
        restartTimeoutRef.current = setTimeout(() => {
          if (isUserIntendedListening.current) {
            startRecognitionSession(SpeechRecognitionClass);
          }
        }, 200);
      } else {
        stopListening();
      }
    }
  };

  // Web Speech API Voice Recognition with Continuous Mode & Silence Debounce
  const toggleListening = async () => {
    if (isListening) {
      stopListening();
      return;
    }

    setSpeechError(null);
    clearSilenceTimer();
    clearRestartTimer();

    const SpeechRecognition =
      typeof window !== "undefined" &&
      ((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);

    if (!SpeechRecognition) {
      setSpeechError(
        "Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge."
      );
      return;
    }

    // Pre-flight check for microphone access & hardware presence
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const testStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        testStream.getTracks().forEach((track) => track.stop());
      }
    } catch (micErr: any) {
      console.warn("Microphone pre-check error:", micErr);
      if (micErr.name === "NotAllowedError" || micErr.name === "PermissionDeniedError") {
        setSpeechError(
          "Microphone permission was denied. Please click the permissions icon in your browser address bar (tune/lock icon next to the URL) and set Microphone to 'Allow'."
        );
        return;
      }
      if (micErr.name === "NotFoundError" || micErr.name === "DevicesNotFoundError") {
        setSpeechError(
          "No microphone detected on your system. Please connect a microphone or headset and try again."
        );
        return;
      }
    }

    // Initialize accumulator with whatever the user currently has in the input box
    accumulatedTranscriptRef.current = input.trim();
    activeSessionTranscriptRef.current = "";
    isUserIntendedListening.current = true;

    startRecognitionSession(SpeechRecognition);
  };

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    if (isListening) {
      stopListening();
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: textToSend.trim(),
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const assistantMsgId = (Date.now() + 1).toString();
    const placeholderAssistant: Message = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      sources: [],
      detected_language: "",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage, placeholderAssistant]);
    if (!queryText) setInput("");
    setLoading(true);

    // Reset user scroll so they see their new question and the streaming start
    userScrolledUp.current = false;
    setShowScrollBottomBtn(false);
    setTimeout(() => scrollToBottom(true), 50);

    // Build conversation history (excluding the first welcome message and current turn)
    const history = messages
      .filter((m) => m.id !== "welcome" && m.content)
      .map((m) => ({ role: m.role, content: m.content }));

    try {
      await streamChatWithAssistant(
        userMessage.content,
        selectedCategory || undefined,
        history,
        {
          onMetadata: (meta) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? { ...msg, sources: meta.sources, detected_language: meta.detected_language }
                  : msg
              )
            );
          },
          onDelta: (delta) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? { ...msg, content: msg.content + delta }
                  : msg
              )
            );
          },
          onDone: () => {
            setLoading(false);
          },
          onError: (err) => {
            console.error("Streaming error, falling back:", err);
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantMsgId
                  ? {
                      ...msg,
                      content:
                        msg.content ||
                        "দুঃখিত, উত্তর তৈরি করতে সমস্যা হয়েছে। স্থানীয় LLM সার্ভার (Ollama) বা ব্যাকএন্ড সক্রিয় আছে কিনা নিশ্চিত করুন।",
                    }
                  : msg
              )
            );
            setLoading(false);
          },
        }
      );
    } catch (error: any) {
      console.error("Streaming chat exception:", error);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantMsgId
            ? {
                ...msg,
                content:
                  msg.content ||
                  "দুঃখিত, উত্তর তৈরি করতে সমস্যা হয়েছে। স্থানীয় LLM সার্ভার (Ollama) সক্রিয় আছে কিনা নিশ্চিত করুন।",
              }
            : msg
        )
      );
    } finally {
      setLoading(false);
    }
  };

  const toggleSources = (msgId: string) => {
    setExpandedSources((prev) => ({
      ...prev,
      [msgId]: !prev[msgId],
    }));
  };

  const clearChat = () => {
    setMessages([
      {
        id: "welcome",
        role: "assistant",
        content:
          "Conversation cleared. How can I assist you with Bangladesh agriculture today? (Answers are in English by default; feel free to ask in English or Bangla).",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-[#040806] text-zinc-100 overflow-hidden relative">
      {/* Top Banner & Status Header - Always fixed at top */}
      <div className="flex-shrink-0 border-b border-white/[0.08] bg-[#070e0a]/90 backdrop-blur-md px-4 py-3 sm:px-6 z-10">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="relative flex h-8 w-8 items-center justify-center rounded-lg bg-emerald-950/40 border border-emerald-500/30 overflow-hidden p-0.5 shadow-sm">
                <Image
                  src="/logo.png"
                  alt="CropIntel Logo"
                  width={28}
                  height={28}
                  className="object-contain"
                />
              </div>
              <h1 className="text-lg font-bold text-white tracking-tight">
                Crop Intelligence AI Assistant
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono">
                Bilingual RAG
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-0.5">
              Powered by 24,178 BRRI, BARI, DAE, BAMIS & FAO Research Citations
            </p>
          </div>

          {/* Model Status Badges */}
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 text-xs text-zinc-300">
              <Cpu className="h-3.5 w-3.5 text-emerald-400" />
              <span className="font-mono text-[11px]">
                {health?.llm_service?.model || "qwen2.5:3b"}
              </span>
            </div>
            <div className="flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] px-2.5 py-1 text-xs text-zinc-300">
              <Layers className="h-3.5 w-3.5 text-lime-400" />
              <span className="font-mono text-[11px]">
                {health?.vector_store?.total_vectors ? `${health.vector_store.total_vectors.toLocaleString()} Vectors` : "ChromaDB Ready"}
              </span>
            </div>
            <button
              onClick={clearChat}
              title="Reset conversation"
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/[0.06] transition-colors"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Container with Fixed Height and Scrollable Messages */}
      <div className="flex-1 overflow-hidden max-w-5xl w-full mx-auto p-4 sm:p-6 flex flex-col relative min-h-0">
        {/* Messages Thread - Independent Scrollable Container */}
        <div
          ref={messagesContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto space-y-4 pb-4 pr-1 min-h-0 scrollbar-thin scrollbar-thumb-zinc-800"
        >
          {messages.map((msg, idx) => {
            const isUser = msg.role === "user";
            const isExpanded = expandedSources[msg.id];

            return (
              <div
                key={msg.id}
                className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}
              >
                {!isUser && (
                  <div className="flex-shrink-0 h-8 w-8 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center">
                    <Bot className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={`max-w-2xl rounded-2xl p-4 shadow-sm text-sm ${
                    isUser
                      ? "bg-emerald-600 text-white rounded-tr-none ml-10"
                      : "bg-[#0b140f] border border-white/[0.08] text-zinc-200 rounded-tl-none mr-10"
                  }`}
                >
                  {/* Content body */}
                  <div className="whitespace-pre-wrap leading-relaxed">
                    {msg.content ? (
                      <>
                        {msg.content}
                        {!isUser && loading && idx === messages.length - 1 && (
                          <span className="inline-block w-1.5 h-4 ml-1 bg-emerald-400 animate-pulse align-middle" />
                        )}
                      </>
                    ) : (
                      !isUser && loading && (
                        <div className="flex items-center gap-2 text-zinc-400 py-1">
                          <Sparkles className="h-4 w-4 text-emerald-400 animate-spin" />
                          <span>তথ্য যাচাই ও উত্তর প্রস্তুত করা হচ্ছে...</span>
                        </div>
                      )
                    )}
                  </div>

                  {/* Assistant Source Citations Widget */}
                  {!isUser && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-white/[0.08]">
                      <button
                        onClick={() => toggleSources(msg.id)}
                        className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
                      >
                        <BookOpen className="h-3.5 w-3.5" />
                        <span>
                          {msg.sources.length} Official Knowledge Sources Used
                        </span>
                        {isExpanded ? (
                          <ChevronUp className="h-3.5 w-3.5" />
                        ) : (
                          <ChevronDown className="h-3.5 w-3.5" />
                        )}
                      </button>

                      {isExpanded && (
                        <div className="mt-2 space-y-2">
                          {msg.sources.map((src, sIdx) => (
                            <div
                              key={sIdx}
                              className="rounded-lg bg-black/40 border border-white/[0.06] p-2.5 text-xs"
                            >
                              <div className="flex items-center justify-between gap-2">
                                <span className="font-semibold text-emerald-300">
                                  {src.citation_text}
                                </span>
                                <span className="text-[10px] text-zinc-400 font-mono">
                                  Match: {(src.relevance_score * 100).toFixed(0)}%
                                </span>
                              </div>
                              <div className="text-[11px] text-zinc-400 mt-1 flex gap-3">
                                <span>Institute: <b className="text-zinc-300">{src.source}</b></span>
                                <span>Category: <b className="text-zinc-300">{src.category}</b></span>
                                {src.page_number > 0 && (
                                  <span>Page: <b className="text-zinc-300">{src.page_number}</b></span>
                                )}
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Timestamp */}
                  <div className="text-[10px] text-zinc-400/80 mt-1 text-right">
                    {msg.timestamp}
                  </div>
                </div>

                {isUser && (
                  <div className="flex-shrink-0 h-8 w-8 rounded-xl bg-zinc-800 text-zinc-300 border border-zinc-700 flex items-center justify-center">
                    <User className="h-4 w-4" />
                  </div>
                )}
              </div>
            );
          })}

          <div ref={messagesEndRef} />
        </div>

        {/* Floating Scroll to Bottom Button */}
        {showScrollBottomBtn && (
          <button
            type="button"
            onClick={() => {
              userScrolledUp.current = false;
              setShowScrollBottomBtn(false);
              scrollToBottom(true);
            }}
            className="absolute bottom-32 right-6 sm:right-10 z-30 flex items-center gap-1.5 rounded-full bg-emerald-600/95 hover:bg-emerald-500 text-white px-3.5 py-1.5 text-xs font-semibold shadow-xl backdrop-blur-md transition-all hover:scale-105 border border-emerald-400/30"
          >
            <span>↓ Scroll to latest</span>
          </button>
        )}

        {/* Input Bar & Controls - Fixed at Bottom */}
        <div className="flex-shrink-0 mt-2 pt-2 border-t border-white/[0.08] space-y-2.5">
          {/* Active Voice Listening Banner with Smooth Pause Indicator */}
          {isListening && (
            <div className="flex items-center justify-between gap-3 bg-red-950/50 border border-red-500/40 rounded-xl px-4 py-2.5 text-sm shadow-lg">
              <div className="flex items-center gap-2.5 text-red-200">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
                <span className="font-medium text-xs sm:text-sm">
                  {speechLang === "bn-BD"
                    ? "🎤 শুনছি... স্বাভাবিক বিরতি দিয়ে বলুন (কথা শেষে ২.৮ সেকেন্ড পর স্বয়ংক্রিয়ভাবে বন্ধ হবে বা 'Done' চাপুন)..."
                    : "🎤 Listening... speak naturally with pauses (auto-finishes after 2.8s silence, or click 'Done')..."}
                </span>
              </div>
              <button
                type="button"
                onClick={stopListening}
                className="text-xs bg-red-500 hover:bg-red-400 text-black px-3.5 py-1 rounded-md transition-all font-bold flex-shrink-0"
              >
                Done
              </button>
            </div>
          )}

          {/* Voice Error Notification Banner */}
          {speechError && (
            <div className="flex items-start justify-between gap-3 bg-amber-950/60 border border-amber-500/40 rounded-xl p-3 text-xs text-amber-200 shadow-md">
              <div className="flex items-start gap-2.5">
                <AlertCircle className="h-4 w-4 flex-shrink-0 text-amber-400 mt-0.5" />
                <div className="space-y-1">
                  <div className="font-semibold text-amber-300">Voice Input Notice</div>
                  <div className="text-amber-200/90 leading-relaxed text-[11px] sm:text-xs">{speechError}</div>
                  <div className="flex flex-wrap items-center gap-2 pt-1">
                    <button
                      type="button"
                      onClick={() => {
                        const newLang = speechLang === "bn-BD" ? "en-US" : "bn-BD";
                        setSpeechLang(newLang);
                        setSpeechError(null);
                      }}
                      className="text-[11px] underline text-emerald-400 hover:text-emerald-300 font-medium"
                    >
                      {speechLang === "bn-BD"
                        ? "Switch voice input to English (en-US) & test"
                        : "Switch voice input to বাংলা (bn-BD) & test"}
                    </button>
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSpeechError(null)}
                className="text-amber-400 hover:text-amber-200 p-0.5 rounded transition-colors flex-shrink-0"
                title="Dismiss"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Suggested Prompts Pills */}
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
            {SAMPLE_PROMPTS.map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(sample.query)}
                disabled={loading}
                className="whitespace-nowrap rounded-full border border-white/[0.08] bg-white/[0.02] hover:bg-emerald-500/10 hover:border-emerald-500/30 px-3 py-1.5 text-xs text-zinc-300 hover:text-emerald-300 transition-all flex-shrink-0"
              >
                {sample.label}
              </button>
            ))}
          </div>

          {/* Category Filter Pill Selector */}
          <div className="flex items-center gap-2 overflow-x-auto pb-1">
            <span className="text-xs text-zinc-400 flex-shrink-0">Topic:</span>
            {CATEGORIES.map((cat) => (
              <button
                key={cat.id}
                onClick={() => setSelectedCategory(cat.id)}
                className={`text-xs px-2.5 py-0.5 rounded-md transition-all flex-shrink-0 ${
                  selectedCategory === cat.id
                    ? "bg-emerald-500 text-black font-semibold"
                    : "bg-white/[0.04] text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {cat.name}
              </button>
            ))}
          </div>

          {/* Text & Voice Input Form */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2 rounded-xl border border-white/[0.12] bg-[#070e0a] p-2 focus-within:border-emerald-500/60 focus-within:ring-1 focus-within:ring-emerald-500/40 transition-all shadow-lg"
          >
            {/* Input Text Box */}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask in English, বাংলা, or Banglish (e.g. কি সিজন চলছে? What crops to grow?)..."
              disabled={loading}
              className="flex-1 bg-transparent px-3 py-2 text-sm text-white placeholder-zinc-500 focus:outline-none disabled:opacity-50"
            />

            {/* Voice Input Controls: Language Switcher & Mic Button */}
            <div className="flex items-center gap-1.5 bg-white/[0.03] border border-white/[0.08] rounded-lg p-1 flex-shrink-0" title="Microphone Voice Input (Chat understands both English & Bangla freely)">
              {/* Mic Language Selector */}
              <div className="flex items-center text-xs">
                <button
                  type="button"
                  onClick={() => setSpeechLang("bn-BD")}
                  title="Microphone speech language: বাংলা (Voice input only)"
                  className={`px-1.5 py-1 rounded text-[11px] font-medium transition-all ${
                    speechLang === "bn-BD"
                      ? "bg-emerald-500/25 text-emerald-300 font-semibold"
                      : "text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  🇧🇩
                </button>
                <button
                  type="button"
                  onClick={() => setSpeechLang("en-US")}
                  title="Microphone speech language: English (Voice input only)"
                  className={`px-1.5 py-1 rounded text-[11px] font-medium transition-all ${
                    speechLang === "en-US"
                      ? "bg-emerald-500/25 text-emerald-300 font-semibold"
                      : "text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  🇬🇧
                </button>
              </div>

              {/* Microphone Toggle Button */}
              <button
                type="button"
                onClick={toggleListening}
                title={
                  isListening
                    ? "রেকর্ডিং বন্ধ করুন (Stop Listening)"
                    : `ভয়েস ইনপুট শুরু করুন (${speechLang === "bn-BD" ? "বাংলা" : "English"})`
                }
                className={`p-1.5 rounded-md transition-all flex items-center justify-center ${
                  isListening
                    ? "bg-red-500 text-white animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.6)]"
                    : "bg-white/[0.06] hover:bg-emerald-500/20 text-zinc-300 hover:text-emerald-300"
                }`}
              >
                {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
              </button>
            </div>

            {/* Submit / Ask Button */}
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="flex items-center gap-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-400 px-4 py-2.5 text-sm font-semibold text-black transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-glow flex-shrink-0"
            >
              <Send className="h-4 w-4" />
              <span className="hidden sm:inline">Ask</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

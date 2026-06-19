"use client";

import { useCallback, useRef, useState } from "react";
import { Mic, MicOff, Phone, Play, Square } from "lucide-react";
import { api, apiUpload } from "@/lib/api";
import { OrderStagePipeline } from "@/components/OrderStagePipeline";
import { ValidationDetails, ValidationDetailsData } from "@/components/ValidationDetails";

const DEMO_PHONES = [
  { phone: "+919876543210", label: "Rajesh (Hindi)" },
  { phone: "+919123456789", label: "Priya (English)" },
  { phone: "+919988776655", label: "Murugan (Tamil)" },
];

const DEMO_ORDERS = [
  "10 kg basmati chawal, 5 kg atta, 2 ltr tel",
  "5 kg rice, 3 ltr sunflower oil, 2 kg sugar",
  "15 kg arisi, 10 kg vengayam, 5 kg urulai",
];

interface StageItem {
  stage: string;
  at?: string;
}

export function CallSimulator() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("idle");
  const [log, setLog] = useState<string[]>([]);
  const [selectedPhone, setSelectedPhone] = useState(DEMO_PHONES[0].phone);
  const [recording, setRecording] = useState(false);
  const [processingVoice, setProcessingVoice] = useState(false);
  const [currentStage, setCurrentStage] = useState("call_started");
  const [stages, setStages] = useState<StageItem[]>([]);
  const [validationDetails, setValidationDetails] = useState<ValidationDetailsData | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const addLog = (msg: string) => setLog((l) => [msg, ...l].slice(0, 10));

  const applyResult = (res: Record<string, unknown>) => {
    setStatus(String(res.state || "processing"));
    if (res.stage) setCurrentStage(String(res.stage));
    if (Array.isArray(res.stages)) setStages(res.stages as StageItem[]);
    if (res.validation_details) setValidationDetails(res.validation_details as ValidationDetailsData);
    if (res.confirmation_text) addLog(`Confirm: ${res.confirmation_text}`);
    if (res.clarification_needed) addLog(`Clarification needed (attempt ${res.attempt})`);
    if (res.transcript) addLog(`Voice transcript: ${res.transcript}`);
  };

  const confirmIfReady = async (sid: string, res: Record<string, unknown>) => {
    if (res.state === "confirming") {
      const confirm = await api<Record<string, unknown>>(`/calls/${sid}/confirm?confirmed=true`, {
        method: "POST",
      });
      applyResult(confirm);
      if (confirm.order_id) {
        addLog(`Order confirmed: ${confirm.order_id}`);
        setStatus("completed");
        setCurrentStage("order_created");
      }
    }
  };

  const startCall = async () => {
    try {
      const res = await api<{
        session_id: string;
        customer_name: string | null;
        state: string;
        stage?: string;
        stages?: StageItem[];
      }>("/calls/start", { method: "POST", body: JSON.stringify({ phone: selectedPhone, language: "en" }) });
      setSessionId(res.session_id);
      setStatus(res.state);
      setCurrentStage(res.stage || "call_started");
      setStages(res.stages || []);
      setValidationDetails(null);
      addLog(`Call started — ${res.customer_name || "Unknown"}`);
    } catch {
      addLog("Failed to start call — is backend running?");
    }
  };

  const submitOrder = async (text: string) => {
    if (!sessionId) return;
    addLog(`Transcript: ${text}`);
    try {
      const res = await api<Record<string, unknown>>("/calls/transcript", {
        method: "POST",
        body: JSON.stringify({ session_id: sessionId, text, is_final: true }),
      });
      applyResult(res);
      await confirmIfReady(sessionId, res);
    } catch {
      addLog("Processing failed");
    }
  };

  const startRecording = async () => {
    if (!sessionId) {
      addLog("Start a call first");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "audio/mp4" });
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: recorder.mimeType });
        await uploadVoice(blob);
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setRecording(true);
      addLog("Recording… speak your order");
    } catch {
      addLog("Microphone access denied");
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const uploadVoice = async (blob: Blob) => {
    if (!sessionId) return;
    setProcessingVoice(true);
    addLog("Transcribing with faster-whisper…");
    try {
      const form = new FormData();
      form.append("audio", blob, "recording.webm");
      form.append("language", "auto");
      const res = await apiUpload<Record<string, unknown>>(`/calls/${sessionId}/voice`, form);
      applyResult(res);
      await confirmIfReady(sessionId, res);
    } catch (e) {
      addLog(`Voice failed: ${e instanceof Error ? e.message : "error"}`);
    } finally {
      setProcessingVoice(false);
    }
  };

  const resetCall = () => {
    setSessionId(null);
    setStatus("idle");
    setCurrentStage("call_started");
    setStages([]);
    setValidationDetails(null);
  };

  return (
    <div className="glass card-hover rounded-2xl border p-6">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-accent/10 p-2">
          <Phone className="h-5 w-5 text-accent" />
        </div>
        <div>
          <h3 className="font-display font-semibold text-white">Voice Call Simulator</h3>
          <p className="text-xs text-gray-500">Voice or text order input</p>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        <select
          value={selectedPhone}
          onChange={(e) => setSelectedPhone(e.target.value)}
          className="w-full rounded-xl border border-surface-border bg-surface-card px-4 py-2.5 text-sm text-gray-200"
        >
          {DEMO_PHONES.map((p) => (
            <option key={p.phone} value={p.phone}>{p.label}</option>
          ))}
        </select>

        <div className="flex gap-2">
          <button
            onClick={startCall}
            disabled={!!sessionId && status !== "completed"}
            className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-accent/20 px-4 py-2.5 text-sm font-medium text-accent ring-1 ring-accent/30 hover:bg-accent/30 disabled:opacity-40"
          >
            <Play className="h-4 w-4" /> Start Call
          </button>
          <button
            onClick={resetCall}
            className="rounded-xl border border-surface-border px-4 py-2.5 text-sm text-gray-400 hover:text-white"
          >
            <Square className="h-4 w-4" />
          </button>
        </div>

        {sessionId && (
          <button
            onClick={recording ? stopRecording : startRecording}
            disabled={processingVoice || status === "completed"}
            className={`flex w-full items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-medium ring-1 disabled:opacity-40 ${
              recording
                ? "bg-danger/20 text-danger ring-danger/30 animate-pulse"
                : "bg-emerald-500/10 text-success ring-success/30 hover:bg-emerald-500/20"
            }`}
          >
            {recording ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
            {processingVoice ? "Processing…" : recording ? "Stop Recording" : "Record Voice"}
          </button>
        )}

        {sessionId && status !== "idle" && (
          <div className="rounded-xl border border-surface-border bg-surface-card/30 p-3">
            <p className="mb-2 text-[10px] uppercase tracking-wider text-gray-500">Processing Pipeline</p>
            <OrderStagePipeline currentStage={currentStage} stages={stages} compact />
          </div>
        )}

        {validationDetails && (
          <div className="rounded-xl border border-surface-border bg-surface-card/30 p-3">
            <p className="mb-2 text-[10px] uppercase tracking-wider text-gray-500">Validation Details</p>
            <ValidationDetails details={validationDetails} compact />
          </div>
        )}

        <div className="space-y-2">
          <p className="text-xs text-gray-500">Quick text orders (fallback):</p>
          {DEMO_ORDERS.map((order, i) => (
            <button
              key={i}
              onClick={() => submitOrder(order)}
              disabled={!sessionId || status === "completed"}
              className="flex w-full items-center gap-2 rounded-lg border border-surface-border bg-surface-card/50 px-3 py-2 text-left text-xs text-gray-300 hover:border-accent/30 disabled:opacity-40"
            >
              <Mic className="h-3 w-3 shrink-0 text-accent" />
              {order}
            </button>
          ))}
        </div>

        {status !== "idle" && (
          <div className="rounded-xl bg-surface-card px-3 py-2 text-xs">
            Status: <span className="text-accent">{status}</span>
          </div>
        )}

        <div className="max-h-32 space-y-1 overflow-y-auto text-[11px] text-gray-500">
          {log.map((l, i) => (
            <div key={i}>{l}</div>
          ))}
        </div>
      </div>
    </div>
  );
}

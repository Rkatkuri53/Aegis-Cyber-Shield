"use client";

import { useEffect, useRef } from "react";

interface AudioPlayerProps {
  audioChunk: string | null; // Base64 PCM 16-bit 24kHz
  isMuted: boolean;
}

export default function AudioPlayer({ audioChunk, isMuted }: AudioPlayerProps) {
  const audioContextRef = useRef<AudioContext | null>(null);
  const nextStartTimeRef = useRef<number>(0);

  useEffect(() => {
    // Lazy init AudioContext on first chunk
    return () => {
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    if (!audioChunk || isMuted) return;

    const playChunk = async () => {
      try {
        if (!audioContextRef.current) {
          audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
            sampleRate: 24000,
          });
        }

        const ctx = audioContextRef.current;
        if (ctx.state === "suspended") {
          await ctx.resume();
        }

        // 1. Decode Base64 to ArrayBuffer
        const binaryString = window.atob(audioChunk);
        const bytes = new Uint8Array(binaryString.length);
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i);
        }

        // 2. Convert PCM 16-bit Little Endian to Float32
        const pcm16 = new Int16Array(bytes.buffer);
        const float32 = new Float32Array(pcm16.length);
        for (let i = 0; i < pcm16.length; i++) {
          float32[i] = pcm16[i] / 32768.0;
        }

        // 3. Create and schedule AudioBuffer
        const audioBuffer = ctx.createBuffer(1, float32.length, 24000);
        audioBuffer.getChannelData(0).set(float32);

        const source = ctx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(ctx.destination);

        // Gapless scheduling
        const now = ctx.currentTime;
        if (nextStartTimeRef.current < now) {
          nextStartTimeRef.current = now + 0.05; // Small buffer for initial chunk
        }

        source.start(nextStartTimeRef.current);
        nextStartTimeRef.current += audioBuffer.duration;
      } catch (err) {
        console.error("[AEGIS-AUDIO-ERR]", err);
      }
    };

    playChunk();
  }, [audioChunk, isMuted]);

  return null;
}

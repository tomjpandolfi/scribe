"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const Header: React.FC = () => (
  <header className="bg-background border-b">
    <div className="flex justify-between container mx-auto px-4 py-3">
      <a className="text-xl font-semibold" href="/">
        Scribe
      </a>
      <p>Video transcription tool for LLMs</p>
    </div>
  </header>
);

const MainContent: React.FC = () => {
  const [url, setUrl] = useState("");
  const [transcription, setTranscription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleTranscribe = async () => {
    setLoading(true);
    setError("");
    setTranscription("");

    try {
      const response = await fetch(
        "https://scribe-backend.herokuapp.com/api/transcribe",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ url }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch transcription");
      }

      const data = await response.json();
      setTranscription(data.transcription);
    } catch (err) {
      setError("Failed to fetch transcription. Please try again.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex-grow flex items-center justify-center bg-background">
      <div className="text-center">
        <Input
          className="min-w-80 min-h-12 m-5"
          type="url"
          placeholder="Paste a social media link here..."
        />
        <Button onClick={handleTranscribe} disabled={loading}>
          {loading ? "Transcribing..." : "Transcribe"}
        </Button>
        {error && <p className="text-red-600 m-4">{error}</p>}
        {transcription && (
          <div className="mt-8 w-full max-w-2xl px-4">
            <h2 className="text-2xl font-semibold mb-2">Transcription:</h2>
            <p className="whitespace-pre-wrap text-left">{transcription}</p>
          </div>
        )}
      </div>
    </main>
  );
};

const Footer: React.FC = () => (
  <footer className="bg-background border-t py-4">
    <div className="flex container mx-auto justify-between">
      <p className="text-muted-foregroun">
        Made with 💛 by{" "}
        <a className="hover:underline" href="https://x.com/tomjpandolfi">
          Tom Pandolfi
        </a>
      </p>
      <a
        className="hover:underline"
        href="https://github.com/tomjpandolfi/scribe"
      >
        View source code
      </a>
    </div>
  </footer>
);

const Page: React.FC = () => (
  <div className="min-h-screen flex flex-col">
    <Header />
    <MainContent />
    <Footer />
  </div>
);

export default Page;

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pytube import YouTube
import pyktok as pyk
from openai import OpenAI
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscriptionRequest(BaseModel):
    url: str

class Transcription:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.download_dir = os.path.join(os.getcwd(), "downloads")
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def download_and_transcribe(self, url):
        if "youtu" in url:
            return self._handle_youtube(url)
        elif "tik" in url:
            return self._handle_tiktok(url)
        else:
            raise ValueError("This API only supports youtube and tiktok URLs... ")

    def _handle_youtube(self, url):
        video_path = self._download_youtube(url)
        if video_path:
            return self._transcribe_audio(video_path)
        else:
            raise ValueError(f"Video path error")

    def _handle_tiktok(self, url):
        video_path = self._download_tiktok(url)
        if video_path:
            return self._transcribe_audio(video_path)
        else:
            raise ValueError(f"Video path error")

    def _download_youtube(self, url):
        try:
            yt = YouTube(url)
            print(f"Selected youtube video: {yt.title}")
            streams = yt.streams

            print("Available streams:")
            for stream in streams:
                if stream.type == "video":
                    print(
                        f"itag: {stream.itag}, type: {stream.type}, resolution: {stream.resolution}, codec: {stream.codecs}"
                    )
                elif stream.type == "audio":
                    print(
                        f"itag: {stream.itag}, type: {stream.type}, abr: {stream.abr}, codec: {stream.codecs}"
                    )
                else:
                    print(f"{stream}")

            audio_stream = streams.filter(only_audio=True).first()

            if audio_stream is None:
                print("Audio stream not found. Trying progressive stream.")
                audio_stream = streams.filter(progressive=True).first()

            if audio_stream:
                print(
                    f"Selected stream: itag: {audio_stream.itag}, type: {audio_stream.type}"
                )
                video_path = audio_stream.download(output_path=self.download_dir)
                print(f"Downloaded to: {video_path}")
                return video_path
            else:
                print("No suitable stream found.")
                return None

        except Exception as e:
            raise ValueError(f"Failed to download youtube content: {str(e)}")

    def _download_tiktok(self, url):
        try:
            pyk.specify_browser("chrome")
            pyk.save_tiktok(
                url, True, os.path.join(self.download_dir, "video_data.csv"), "chrome"
            )

            video_path = os.path.join(self.download_dir, "tiktok_video.mp4")
            if os.path.exists(video_path):
                return video_path
            else:
                raise ValueError("TikTok video not found after download")
        except Exception as e:
            raise ValueError(f"Failed to download tiktok content: {str(e)}")

    def _transcribe_audio(self, video_path):
        if not video_path or not os.path.exists(video_path):
            raise ValueError("Invalid video path")

        try:
            with open(video_path, "rb") as audio_file:
                transcription = self.client.audio.transcriptions.create(
                    model="whisper-1", file=audio_file
                )
            return transcription.text
        except Exception as e:
            raise ValueError(f"Failed to transcribe audio with Whisper: {str(e)}")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)


transcribe = Transcription()

@app.post("/api/transcribe")
async def transcribe_url(request: TranscriptionRequest):
    try:
        transcription = transcribe.download_and_transcribe(request.url)
        return {"transcription": transcription}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # main()

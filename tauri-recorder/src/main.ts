import { invoke } from "@tauri-apps/api/core";

const startBtn = document.getElementById("startBtn") as HTMLButtonElement;
const stopBtn = document.getElementById("stopBtn") as HTMLButtonElement;
const statusDiv = document.getElementById("status") as HTMLDivElement;

let isRecording = false;

interface RecordingResult {
  success: boolean;
  message?: string;
  file_path?: string;
  error?: string;
}

startBtn.addEventListener("click", async () => {
  if (isRecording) return;

  try {
    // Call Tauri command to start recording
    statusDiv.textContent = "⏺ Starting recording...";
    statusDiv.classList.add("recording");

    const result = await invoke<RecordingResult>("start_recording");

    if (result.success) {
      isRecording = true;
      startBtn.style.display = "none";
      stopBtn.style.display = "inline-block";
      statusDiv.textContent = "⏺ Recording in progress...";
    } else {
      statusDiv.textContent = `❌ Error: ${result.error || "Failed to start recording"}`;
      statusDiv.classList.remove("recording");
    }
  } catch (error) {
    statusDiv.textContent = `❌ Error: ${error}`;
    statusDiv.classList.remove("recording");
  }
});

stopBtn.addEventListener("click", async () => {
  if (!isRecording) return;

  try {
    // Call Tauri command to stop recording
    statusDiv.textContent = "⏹ Stopping recording...";

    const result = await invoke<RecordingResult>("stop_recording");

    if (result.success) {
      isRecording = false;
      stopBtn.style.display = "none";
      startBtn.style.display = "inline-block";
      statusDiv.classList.remove("recording");

      if (result.file_path) {
        statusDiv.textContent = `✅ Saved: ${result.file_path}`;
      } else {
        statusDiv.textContent = `✅ Recording saved!`;
      }

      // Reset status after 5 seconds
      setTimeout(() => {
        if (!isRecording) {
          statusDiv.textContent = "Ready to record";
        }
      }, 5000);
    } else {
      statusDiv.textContent = `❌ Error: ${result.error || "Failed to stop recording"}`;
    }
  } catch (error) {
    statusDiv.textContent = `❌ Error: ${error}`;
    isRecording = false;
    stopBtn.style.display = "none";
    startBtn.style.display = "inline-block";
    statusDiv.classList.remove("recording");
  }
});

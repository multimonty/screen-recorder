use std::process::Command;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct RecordingResult {
    success: bool,
    #[serde(skip_serializing_if = "Option::is_none")]
    message: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    file_path: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    error: Option<String>,
}

#[tauri::command]
fn start_recording() -> RecordingResult {
    // Use system Python
    let python_path = "/usr/bin/python3";

    // Get absolute path to recording script
    let script_path = std::env::current_dir()
        .unwrap()
        .join("src-tauri")
        .join("screen_recorder.py");

    // Execute Python script with "start" command
    let output = Command::new(python_path)
        .arg(&script_path)
        .arg("start")
        .output();

    match output {
        Ok(result) => {
            if result.status.success() {
                let stdout = String::from_utf8_lossy(&result.stdout);
                match serde_json::from_str::<RecordingResult>(&stdout) {
                    Ok(recording_result) => recording_result,
                    Err(e) => RecordingResult {
                        success: false,
                        message: None,
                        file_path: None,
                        error: Some(format!("JSON parse error: {} | Output: {}", e, stdout)),
                    }
                }
            } else {
                let stderr = String::from_utf8_lossy(&result.stderr);
                RecordingResult {
                    success: false,
                    message: None,
                    file_path: None,
                    error: Some(format!("Python error: {}", stderr)),
                }
            }
        },
        Err(e) => RecordingResult {
            success: false,
            message: None,
            file_path: None,
            error: Some(format!("Failed to execute: {}", e)),
        }
    }
}

#[tauri::command]
fn stop_recording() -> RecordingResult {
    // Use system Python
    let python_path = "/usr/bin/python3";

    // Get absolute path to recording script
    let script_path = std::env::current_dir()
        .unwrap()
        .join("src-tauri")
        .join("screen_recorder.py");

    // Execute Python script with "stop" command
    let output = Command::new(python_path)
        .arg(&script_path)
        .arg("stop")
        .output();

    match output {
        Ok(result) => {
            if result.status.success() {
                let stdout = String::from_utf8_lossy(&result.stdout);
                match serde_json::from_str::<RecordingResult>(&stdout) {
                    Ok(recording_result) => recording_result,
                    Err(e) => RecordingResult {
                        success: false,
                        message: None,
                        file_path: None,
                        error: Some(format!("JSON parse error: {} | Output: {}", e, stdout)),
                    }
                }
            } else {
                let stderr = String::from_utf8_lossy(&result.stderr);
                RecordingResult {
                    success: false,
                    message: None,
                    file_path: None,
                    error: Some(format!("Python error: {}", stderr)),
                }
            }
        },
        Err(e) => RecordingResult {
            success: false,
            message: None,
            file_path: None,
            error: Some(format!("Failed to execute: {}", e)),
        }
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![start_recording, stop_recording])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

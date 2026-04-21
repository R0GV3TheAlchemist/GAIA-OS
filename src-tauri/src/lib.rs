use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    Manager,
};
use tauri_plugin_shell::ShellExt;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from GAIA!", name)
}

#[tauri::command]
fn get_backend_status() -> String {
    "online".to_string()
}

/// Spawn the Python sidecar and poll /health until it responds.
/// Runs on a background thread so it never blocks the UI.
fn start_python_sidecar(app: &tauri::App) {
    let shell = app.shell();
    let sidecar_cmd = shell
        .sidecar("gaia-backend")
        .expect("gaia-backend sidecar not found — run PyInstaller first");

    // Spawn and ignore stdout/stderr (they go to the OS log)
    tauri::async_runtime::spawn(async move {
        let (_rx, _child) = sidecar_cmd
            .spawn()
            .expect("failed to spawn gaia-backend sidecar");

        // Poll /health until the backend is ready (max 30 s)
        let client = reqwest::Client::new();
        for _ in 0..60 {
            tokio::time::sleep(std::time::Duration::from_millis(500)).await;
            if let Ok(resp) = client
                .get("http://127.0.0.1:8008/health")
                .send()
                .await
            {
                if resp.status().is_success() {
                    println!("[GAIA] Python backend is ready ✓");
                    return;
                }
            }
        }
        eprintln!("[GAIA] WARNING: backend did not become ready within 30 s");
    });
}

pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_process::init())
        .plugin(tauri_plugin_notification::init())
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(window) = app.get_webview_window("main") {
                let _ = window.show();
                let _ = window.set_focus();
            }
        }))
        .plugin(tauri_plugin_updater::Builder::new().build())
        .setup(|app| {
            // ── Sidecar ───────────────────────────────────────────────────
            start_python_sidecar(app);

            // ── Tray ──────────────────────────────────────────────────────
            let open = MenuItem::with_id(app, "open", "Open GAIA", true, None::<&str>)?;
            let check_updates = MenuItem::with_id(app, "updates", "Check for Updates", true, None::<&str>)?;
            let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let menu = Menu::with_items(app, &[&open, &check_updates, &quit])?;

            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .tooltip("GAIA - Your Sovereign AI")
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "open" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    "quit" => {
                        app.exit(0);
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click {
                        button: MouseButton::Left,
                        button_state: MouseButtonState::Up,
                        ..
                    } = event
                    {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet, get_backend_status])
        .run(tauri::generate_context!())
        .expect("error while running GAIA");
}

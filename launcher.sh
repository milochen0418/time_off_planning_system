#!/bin/bash
#
# launcher.sh — Time-Off Planning System GUI Launcher (macOS AppleScript)
# -----------------------------------------------------------------------
# Provides a native macOS dialog to:
#   1. See whether the web app (ports 3000/8000) is running
#   2. Start / Stop the web app
#   3. Launch the Flet app on an Android emulator
#   4. Launch the Flet app on an iOS simulator
#
# Usage:  ./launcher.sh   (or:  bash launcher.sh)

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ─── Helpers ──────────────────────────────────────────────────────────────

check_web_app_status() {
    local pids
    pids=$(lsof -ti:3000,8000 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        echo "running"
    else
        echo "stopped"
    fi
}

check_android_emulator() {
    if command -v adb &>/dev/null; then
        local devices
        devices=$(adb devices 2>/dev/null | grep -c 'emulator.*device$' || true)
        if (( devices > 0 )); then
            echo "running"
        else
            echo "stopped"
        fi
    else
        echo "no_adb"
    fi
}

check_ios_simulator() {
    if command -v xcrun &>/dev/null; then
        local booted
        booted=$(xcrun simctl list devices booted 2>/dev/null | grep -c 'Booted' || true)
        if (( booted > 0 )); then
            echo "running"
        else
            echo "stopped"
        fi
    else
        echo "no_xcrun"
    fi
}

# Return the name of the first available AVD
first_avd_name() {
    if command -v avdmanager &>/dev/null; then
        avdmanager list avd -c 2>/dev/null | head -1
    elif command -v emulator &>/dev/null; then
        emulator -list-avds 2>/dev/null | head -1
    fi
}

# Return the UDID of the first available (not booted) iPhone simulator
first_iphone_udid() {
    xcrun simctl list devices available 2>/dev/null \
        | grep 'iPhone' \
        | head -1 \
        | sed -E 's/.*\(([A-F0-9-]+)\).*/\1/'
}

notify() {
    osascript -e "display notification \"$1\" with title \"Time-Off Launcher\""
}

alert() {
    osascript -e "display dialog \"$1\" with title \"Time-Off Launcher\" buttons {\"OK\"} default button \"OK\" with icon caution"
}

# ─── Actions ──────────────────────────────────────────────────────────────

# Source user profile in Terminal.app so ANDROID_HOME, JAVA_HOME etc. are set
terminal_prefix() {
    echo "source ~/.zshrc 2>/dev/null; cd '${SCRIPT_DIR}'"
}

# Kill any orphaned flet dev-server on common ports (8550-8560)
kill_stale_flet() {
    local pids
    pids=$(lsof -ti:8550-8560 2>/dev/null || true)
    if [[ -n "$pids" ]]; then
        kill -9 $pids 2>/dev/null || true
        sleep 1
    fi
}

do_start_web() {
    local status
    status=$(check_web_app_status)
    if [[ "$status" == "running" ]]; then
        alert "Web app is already running on ports 3000 / 8000."
        return
    fi
    notify "Starting web app …"
    local cmd
    cmd="$(terminal_prefix) && poetry run ./reflex_rerun.sh"
    osascript <<EOF
tell application "Terminal"
    activate
    do script "${cmd}"
end tell
EOF
    notify "Web app start command issued. Check Terminal."
}

do_stop_web() {
    local pids
    pids=$(lsof -ti:3000,8000 2>/dev/null || true)
    if [[ -z "$pids" ]]; then
        alert "Web app is not running."
        return
    fi
    kill -9 $pids 2>/dev/null || true
    notify "Web app stopped (killed PIDs: ${pids//$'\n'/, })."
}

do_android() {
    # Pre-checks
    if ! command -v adb &>/dev/null; then
        alert "adb not found. Please install Android SDK and configure PATH.\n\nSee flet_app/HOW_TO_RUN.md for details."
        return
    fi

    local emu_status
    emu_status=$(check_android_emulator)

    if [[ "$emu_status" == "stopped" ]]; then
        local avd
        avd=$(first_avd_name)
        if [[ -z "$avd" ]]; then
            alert "No Android AVD found. Create one first:\n\navdmanager create avd -n pixel7 -k \"system-images;android-34;google_apis;arm64-v8a\" -d \"pixel_7\""
            return
        fi
        notify "Starting Android emulator ($avd) …"
        nohup emulator -avd "$avd" &>/dev/null &
        # Wait for the emulator to boot (max ~90 s)
        local waited=0
        while (( waited < 90 )); do
            if adb shell getprop sys.boot_completed 2>/dev/null | grep -q '1'; then
                break
            fi
            sleep 3
            waited=$((waited + 3))
        done
        if ! adb shell getprop sys.boot_completed 2>/dev/null | grep -q '1'; then
            alert "Android emulator did not finish booting within 90 seconds. Please wait and retry."
            return
        fi
        notify "Emulator booted."
    fi

    local apk_path="${SCRIPT_DIR}/flet_app/build/apk/flet_app.apk"

    # Ask: use existing APK or rebuild?
    local build_choice="Build"
    if [[ -f "$apk_path" ]]; then
        build_choice=$(osascript <<EOF
set theResult to button returned of (display dialog "Found existing APK:\n${apk_path}\n\nUse existing or rebuild?" ¬
    with title "Android APK" ¬
    buttons {"Cancel", "Use Existing", "Rebuild"} ¬
    default button "Use Existing")
return theResult
EOF
        ) || return
    fi

    if [[ "$build_choice" == "Rebuild" || "$build_choice" == "Build" ]]; then
        notify "Building APK (this may take a while) …"
        cd "$SCRIPT_DIR"
        if ! poetry run flet build apk flet_app --yes 2>&1; then
            alert "APK build failed. Check terminal output for details."
            return
        fi
        if [[ ! -f "$apk_path" ]]; then
            alert "APK build completed but file not found at:\n${apk_path}"
            return
        fi
        notify "APK build successful."
    fi

    # Install APK on emulator
    notify "Installing APK on emulator …"
    if ! adb install -r "$apk_path" 2>&1; then
        alert "Failed to install APK on emulator."
        return
    fi

    # Launch the app on the emulator using am start (more reliable than monkey)
    local package_name
    package_name=$(adb shell pm list packages 2>/dev/null | grep -i 'flet' | head -1 | sed 's/package://')
    if [[ -n "$package_name" ]]; then
        # Resolve the main activity
        local activity
        activity=$(adb shell cmd package resolve-activity --brief "$package_name" 2>/dev/null | tail -1)
        notify "Launching ${activity} on emulator …"
        adb shell am start -n "$activity" 2>/dev/null
        notify "App launched on Android emulator."
    else
        alert "APK installed, but could not detect the package name to launch.\nPlease open the app manually on the emulator."
    fi
}

do_ios() {
    if ! command -v xcrun &>/dev/null; then
        alert "Xcode command-line tools not found. Please install Xcode first."
        return
    fi

    local sim_status
    sim_status=$(check_ios_simulator)

    if [[ "$sim_status" == "stopped" ]]; then
        local udid
        udid=$(first_iphone_udid)
        if [[ -z "$udid" ]]; then
            alert "No available iPhone simulator found. Open Xcode → Settings → Platforms to download a simulator runtime."
            return
        fi
        notify "Booting iOS Simulator …"
        xcrun simctl boot "$udid" 2>/dev/null || true
        open -a Simulator
        # Give the simulator a moment to appear
        sleep 5
    fi

    local app_dir="${SCRIPT_DIR}/flet_app/build/ios-simulator/flet_app.app"

    # Ask: use existing build or rebuild?
    local build_choice="Build"
    if [[ -d "$app_dir" ]]; then
        build_choice=$(osascript <<EOF
set theResult to button returned of (display dialog "Found existing iOS Simulator build:\n${app_dir}\n\nUse existing or rebuild?" ¬
    with title "iOS Simulator App" ¬
    buttons {"Cancel", "Use Existing", "Rebuild"} ¬
    default button "Use Existing")
return theResult
EOF
        ) || return
    fi

    if [[ "$build_choice" == "Rebuild" || "$build_choice" == "Build" ]]; then
        notify "Building iOS Simulator app (this may take a while) …"
        cd "$SCRIPT_DIR"
        if ! poetry run flet build ios-simulator flet_app --yes 2>&1; then
            alert "iOS Simulator build failed. Check terminal output for details."
            return
        fi
        if [[ ! -d "$app_dir" ]]; then
            alert "Build completed but .app not found at:\n${app_dir}"
            return
        fi
        notify "iOS Simulator build successful."
    fi

    # Get a booted simulator UDID
    local booted_udid
    booted_udid=$(xcrun simctl list devices booted 2>/dev/null \
        | grep -E '\(.*\) \(Booted\)' \
        | head -1 \
        | sed -E 's/.*\(([A-F0-9-]+)\) \(Booted\).*/\1/')

    if [[ -z "$booted_udid" ]]; then
        alert "No booted simulator found. Please boot a simulator first."
        return
    fi

    # Install and launch on iOS Simulator
    notify "Installing app on iOS Simulator …"
    if ! xcrun simctl install "$booted_udid" "$app_dir" 2>&1; then
        alert "Failed to install app on iOS Simulator."
        return
    fi

    # Get the bundle ID from Info.plist
    local bundle_id
    bundle_id=$(/usr/libexec/PlistBuddy -c "Print :CFBundleIdentifier" "${app_dir}/Info.plist" 2>/dev/null || echo "")
    if [[ -n "$bundle_id" ]]; then
        notify "Launching ${bundle_id} on iOS Simulator …"
        xcrun simctl launch "$booted_udid" "$bundle_id" 2>/dev/null
        notify "App launched on iOS Simulator."
    else
        alert "App installed, but could not detect bundle ID to launch.\nPlease open the app manually on the simulator."
    fi
}

# ─── Main dialog loop ─────────────────────────────────────────────────────

main() {
    while true; do
        # Gather current status
        local web_status emu_status sim_status
        web_status=$(check_web_app_status)
        emu_status=$(check_android_emulator)
        sim_status=$(check_ios_simulator)

        # Build status lines
        local web_label emu_label sim_label
        if [[ "$web_status" == "running" ]]; then
            web_label="✅ Web App (ports 3000/8000): RUNNING"
        else
            web_label="⛔ Web App (ports 3000/8000): STOPPED"
        fi

        case "$emu_status" in
            running)  emu_label="✅ Android Emulator: RUNNING" ;;
            stopped)  emu_label="⛔ Android Emulator: NOT RUNNING" ;;
            no_adb)   emu_label="⚠️  Android SDK (adb): NOT INSTALLED" ;;
        esac

        case "$sim_status" in
            running)  sim_label="✅ iOS Simulator: BOOTED" ;;
            stopped)  sim_label="⛔ iOS Simulator: NOT BOOTED" ;;
            no_xcrun) sim_label="⚠️  Xcode CLI tools: NOT INSTALLED" ;;
        esac

        # Build option list based on web state
        local web_action
        if [[ "$web_status" == "running" ]]; then
            web_action="🛑 Stop Web App"
        else
            web_action="🚀 Start Web App"
        fi

        local choice
        choice=$(osascript <<EOF
set statusText to "─── Current Status ───" & return & return ¬
    & "${web_label}" & return ¬
    & "${emu_label}" & return ¬
    & "${sim_label}"

set actionList to {"${web_action}", "📱 Run on Android Emulator", "🍎 Run on iOS Simulator", "🔄 Refresh Status", "❌ Quit"}

set picked to choose from list actionList ¬
    with title "Time-Off Planning System Launcher" ¬
    with prompt statusText ¬
    default items {"🔄 Refresh Status"}

if picked is false then return "Quit"
return item 1 of picked
EOF
        ) || break   # User pressed Esc / closed dialog

        case "$choice" in
            *"Start Web App"*)  do_start_web ;;
            *"Stop Web App"*)   do_stop_web  ;;
            *"Run on Android"*) do_android   ;;
            *"Run on iOS"*)     do_ios       ;;
            *"Refresh"*)        continue     ;;
            *"Quit"*|"")        break        ;;
        esac
    done
}

main

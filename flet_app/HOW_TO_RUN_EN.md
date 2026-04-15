# Flet App — Environment Setup & Launch Guide

This document explains how to install all the necessary tools from scratch and run this Flet mobile application on an **Android emulator** or **iOS simulator**.

> The steps below are primarily for **macOS (Apple Silicon)**.

---

## Table of Contents

1. [System Requirements](#1-system-requirements)
2. [Install Python 3.11 + Poetry](#2-install-python-311--poetry)
3. [Install Flutter SDK](#3-install-flutter-sdk)
4. [Install JDK 17](#4-install-jdk-17)
5. [Install Android Studio](#5-install-android-studio)
6. [Install Android SDK Components](#6-install-android-sdk-components)
7. [Set Environment Variables](#7-set-environment-variables)
8. [Accept Android SDK Licenses](#8-accept-android-sdk-licenses)
9. [Create an Android Emulator (AVD)](#9-create-an-android-emulator-avd)
9.5. [iOS Simulator Setup](#95-ios-simulator-setup)
10. [Verify Environment — flutter doctor](#10-verify-environment--flutter-doctor)
11. [Install Python Dependencies](#11-install-python-dependencies)
12. [Launch the Application](#12-launch-the-application)
13. [API Base URL Reference](#13-api-base-url-reference)
14. [Default Accounts](#14-default-accounts)
15. [FAQ / Troubleshooting](#15-faq--troubleshooting)

---

## 1. System Requirements

| Item | Version |
|------|---------|
| macOS | 13+ (Ventura or later) |
| Python | 3.11 |
| Poetry | 1.x / 2.x |
| Flutter | 3.x (stable channel) |
| JDK | 17 |
| Android SDK | 36 (with Build Tools) |
| Homebrew | Latest |
| Xcode | 16+ (only required for iOS simulator) |
| CocoaPods | 1.x (only required for iOS simulator) |

---

## 2. Install Python 3.11 + Poetry

If not already installed:

```bash
brew install python@3.11
```

Install Poetry:

```bash
curl -sSL https://install.python-poetry.org | python3.11 -
```

Verify:

```bash
python3.11 --version   # Python 3.11.x
poetry --version        # Poetry 1.x.x or 2.x.x
```

---

## 3. Install Flutter SDK

```bash
brew install --cask flutter
```

Verify after installation:

```bash
flutter --version
```

Should display Flutter 3.x and Dart 3.x.

---

## 4. Install JDK 17

The Android SDK tools (sdkmanager, avdmanager, etc.) require JDK 17:

```bash
brew install openjdk@17
```

---

## 5. Install Android Studio

```bash
brew install --cask android-studio
```

> Android Studio itself is about 1.4 GB. After installation, you **don't need to open** the Android Studio UI — all steps below are done via the command line.

---

## 6. Install Android SDK Components

### 6.1 Download Command-Line Tools

If the `sdkmanager` command is not available, manually download the command-line tools:

```bash
mkdir -p ~/Library/Android/sdk/cmdline-tools
cd ~/Library/Android/sdk/cmdline-tools

# Download the latest command-line tools (check https://developer.android.com/studio#command-tools for the latest link)
curl -fSL -o cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-mac-13114758_latest.zip"

unzip -qo cmdline-tools.zip
mv cmdline-tools latest
rm cmdline-tools.zip
```

### 6.2 Install SDK Platforms and Tools

```bash
sdkmanager "platform-tools" \
           "emulator" \
           "platforms;android-36" \
           "build-tools;36.0.0" \
           "platforms;android-34" \
           "build-tools;34.0.0" \
           "system-images;android-34;google_apis;arm64-v8a"
```

> - `platform-tools`: includes `adb` and other tools
> - `emulator`: the Android emulator
> - `platforms;android-36` + `build-tools;36.0.0`: required by Flutter 3.41+
> - `system-images;android-34;google_apis;arm64-v8a`: system image for the emulator (API 34, ARM64)

---

## 7. Set Environment Variables

Add the following to `~/.zshrc` (or `~/.bash_profile`):

```bash
# Android SDK
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# JDK 17 for Android SDK
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
```

Apply changes:

```bash
source ~/.zshrc
```

Verify:

```bash
which sdkmanager   # Should show ~/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager
which adb          # Should show ~/Library/Android/sdk/platform-tools/adb
java --version     # Should show openjdk 17.x
echo $ANDROID_HOME # Should show /Users/<your-username>/Library/Android/sdk
```

---

## 8. Accept Android SDK Licenses

```bash
yes | sdkmanager --licenses
```

After accepting all licenses, you should see `All SDK package licenses accepted` at the end.

---

## 9. Create an Android Emulator (AVD)

Create a Pixel 7 emulator (API 34):

```bash
echo "no" | avdmanager create avd \
  -n pixel7 \
  -k "system-images;android-34;google_apis;arm64-v8a" \
  -d "pixel_7" \
  --force
```

Verify the AVD was created:

```bash
avdmanager list avd
```

Should display `Name: pixel7`.

---

## 9.5. iOS Simulator Setup

If you need to run the app on an iOS simulator, the following additional setup is required.

### 9.5.1 Install Xcode

Install Xcode 16+ from the Mac App Store, or use an existing installation.

Confirm Xcode command line tools:

```bash
xcode-select --install   # If not already installed
xcodebuild -version      # Should show Xcode 16.x
```

### 9.5.2 Install CocoaPods

```bash
brew install cocoapods
```

Verify:

```bash
pod --version   # Should show 1.x
```

### 9.5.3 Download iOS Simulator Runtime

```bash
xcodebuild -downloadPlatform iOS
```

> The download is about 8–9 GB and may take some time. Once complete, verify with:

```bash
xcrun simctl list runtimes
# Should show iOS 18.x
```

### 9.5.4 Create an iOS Simulator

Xcode usually comes with default simulators. Check available simulators:

```bash
xcrun simctl list devices available | grep iPhone
```

If none are available, create one manually:

```bash
xcrun simctl create "iPhone 16" "com.apple.CoreSimulator.SimDeviceType.iPhone-16" "com.apple.CoreSimulator.SimRuntime.iOS-18-6"
```

---

## 10. Verify Environment — flutter doctor

```bash
flutter doctor
```

Make sure the following items show ✓:

```
[✓] Flutter (Channel stable, 3.x)
[✓] Android toolchain - develop for Android devices (Android SDK version 36.0.0)
```

> Xcode-related warnings can be ignored if you only plan to target Android.

---

## 11. Install Python Dependencies

In the project root directory:

```bash
cd /path/to/time_off_planning_system
poetry env use python3.11
poetry install
```

This will install `flet`, `httpx`, `reflex`, and all other dependencies.

---

## 12. Launch the Application

You will need **two terminals**:

### Terminal A — Start the Backend API Server

```bash
cd /path/to/time_off_planning_system
poetry run ./reflex_rerun.sh
```

Wait for the server to be ready (frontend on port 3000, backend on port 8000).

### Terminal B — Start the Android Emulator + Flet App

**Step 1: Launch the emulator**

```bash
emulator -avd pixel7 &
```

Wait for the emulator to fully boot (you should see the phone home screen). Confirm the device is ready:

```bash
adb devices
# Should show: emulator-5554  device
```

**Step 2: Run the Flet App (on the emulator)**

```bash
cd /path/to/time_off_planning_system
poetry run flet run flet_app/main.py --android
```

> Flet will automatically package and install the APK onto the emulator. The first run will be slow (the Flutter project needs to compile).

### Terminal C (Alternative) — Start the iOS Simulator + Flet App

**Step 1: Launch the iOS simulator**

```bash
open -a Simulator
```

Or specify a particular simulator:

```bash
xcrun simctl boot "iPhone 16"
open -a Simulator
```

Wait for the simulator to fully boot. Confirm the device is ready:

```bash
xcrun simctl list devices booted
# Should show one Booted iPhone
```

**Step 2: Run the Flet App (on the iOS simulator)**

```bash
cd /path/to/time_off_planning_system
poetry run flet run flet_app/main.py --ios
```

> Flet will automatically compile and install the app onto the iOS simulator. The first run takes longer (CocoaPods install + Flutter compilation).

### Other Launch Modes

**Desktop mode (no emulator required):**

```bash
cd /path/to/time_off_planning_system
API_BASE_URL="http://127.0.0.1:8000" poetry run python flet_app/main.py
```

**Web mode (runs in a browser):**

```bash
cd /path/to/time_off_planning_system
API_BASE_URL="http://127.0.0.1:8000" poetry run flet run flet_app/main.py --web --port 8550
```

Then open `http://localhost:8550` in your browser. You can also access it from a phone on the same WiFi network via `http://<Mac's IP>:8550`.

---

## 13. API Base URL Reference

The `DEFAULT_BASE` in `flet_app/api_client.py` defaults to `http://10.0.2.2:8000`.

| Environment | API Base URL | Notes |
|-------------|-------------|-------|
| Android emulator | `http://10.0.2.2:8000` | `10.0.2.2` is a special IP the Android emulator uses to reach the host machine |
| iOS simulator | `http://127.0.0.1:8000` | iOS simulator shares the host's network, so localhost works directly |
| Desktop / Web | `http://127.0.0.1:8000` | Connects to localhost directly |
| Physical device (same WiFi) | `http://<Mac's IP>:8000` | e.g. `http://192.168.1.100:8000` |

> **Note**: `api_client.py` automatically detects the platform and selects the correct Base URL. When `ANDROID_ROOT` is detected (Android environment), it uses `10.0.2.2`; all other platforms default to `127.0.0.1`. You can also manually override it via the `API_BASE_URL` environment variable.

Override example:

```bash
API_BASE_URL="http://127.0.0.1:8000" poetry run python flet_app/main.py
```

---

## 14. Default Accounts

| Role | Username | Password |
|------|----------|----------|
| Regular user | admin | admin123 |
| Super admin | admin | admin |

---

## 15. FAQ / Troubleshooting

### Q: `sdkmanager` shows "This tool requires JDK 17 or later"

Confirm `JAVA_HOME` points to JDK 17:

```bash
echo $JAVA_HOME
java --version  # Should be 17.x
```

### Q: `flutter doctor` shows "Flutter requires Android SDK 36"

Install SDK 36:

```bash
sdkmanager "platforms;android-36" "build-tools;36.0.0"
```

### Q: App on the emulator cannot connect to the backend

1. Make sure the backend is running (`poetry run ./reflex_rerun.sh`).
2. Confirm the API Base URL is `http://10.0.2.2:8000` (special address for Android emulator).
3. Confirm the backend is bound to `0.0.0.0:8000` and not only `127.0.0.1:8000`.

### Q: First `flet run --android` is very slow

This is normal. The first run needs to download Gradle dependencies and compile the Flutter project. Subsequent runs will be much faster.

### Q: Android emulator won't start on macOS

Make sure your Mac is Apple Silicon and you installed the `arm64-v8a` system image (not `x86_64`).

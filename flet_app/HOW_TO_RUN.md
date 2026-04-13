# Flet App — 環境安裝與啟動指南

本文件說明如何從零開始安裝所有必要工具，並在 **Android 模擬器** 或 **iOS 模擬器** 上執行此 Flet 行動應用程式。

> 以下步驟以 **macOS (Apple Silicon)** 為主。

---

## 目錄

1. [系統需求](#1-系統需求)
2. [安裝 Python 3.11 + Poetry](#2-安裝-python-311--poetry)
3. [安裝 Flutter SDK](#3-安裝-flutter-sdk)
4. [安裝 JDK 17](#4-安裝-jdk-17)
5. [安裝 Android Studio](#5-安裝-android-studio)
6. [安裝 Android SDK 元件](#6-安裝-android-sdk-元件)
7. [設定環境變數](#7-設定環境變數)
8. [接受 Android SDK Licenses](#8-接受-android-sdk-licenses)
9. [建立 Android 模擬器 (AVD)](#9-建立-android-模擬器-avd)
9.5. [iOS 模擬器設定](#95-ios-模擬器設定)
10. [驗證環境 — flutter doctor](#10-驗證環境--flutter-doctor)
11. [安裝 Python 依賴](#11-安裝-python-依賴)
12. [啟動應用程式](#12-啟動應用程式)
13. [API Base URL 說明](#13-api-base-url-說明)
14. [預設帳號](#14-預設帳號)
15. [常見問題](#15-常見問題)

---

## 1. 系統需求

| 項目 | 版本 |
|------|------|
| macOS | 13+ (Ventura 以上) |
| Python | 3.11 |
| Poetry | 1.x / 2.x |
| Flutter | 3.x (stable channel) |
| JDK | 17 |
| Android SDK | 36 (含 Build Tools) |
| Homebrew | 最新版 |
| Xcode | 16+ (僅 iOS 模擬器需要) |
| CocoaPods | 1.x (僅 iOS 模擬器需要) |

---

## 2. 安裝 Python 3.11 + Poetry

如果尚未安裝：

```bash
brew install python@3.11
```

安裝 Poetry：

```bash
curl -sSL https://install.python-poetry.org | python3.11 -
```

確認版本：

```bash
python3.11 --version   # Python 3.11.x
poetry --version        # Poetry 1.x.x 或 2.x.x
```

---

## 3. 安裝 Flutter SDK

```bash
brew install --cask flutter
```

安裝完成後確認：

```bash
flutter --version
```

應顯示 Flutter 3.x、Dart 3.x。

---

## 4. 安裝 JDK 17

Android SDK 工具（sdkmanager、avdmanager 等）需要 JDK 17：

```bash
brew install openjdk@17
```

---

## 5. 安裝 Android Studio

```bash
brew install --cask android-studio
```

> Android Studio 本身約 1.4GB。安裝完成後 **不需要打開** Android Studio UI，以下全部透過命令列完成。

---

## 6. 安裝 Android SDK 元件

### 6.1 下載 Command-Line Tools

如果 `sdkmanager` 指令不存在，手動下載 command-line tools：

```bash
mkdir -p ~/Library/Android/sdk/cmdline-tools
cd ~/Library/Android/sdk/cmdline-tools

# 下載最新版 command-line tools (檢查 https://developer.android.com/studio#command-tools 取得最新連結)
curl -fSL -o cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-mac-13114758_latest.zip"

unzip -qo cmdline-tools.zip
mv cmdline-tools latest
rm cmdline-tools.zip
```

### 6.2 安裝 SDK 平台與工具

```bash
sdkmanager "platform-tools" \
           "emulator" \
           "platforms;android-36" \
           "build-tools;36.0.0" \
           "platforms;android-34" \
           "build-tools;34.0.0" \
           "system-images;android-34;google_apis;arm64-v8a"
```

> - `platform-tools`：包含 `adb` 等工具
> - `emulator`：Android 模擬器
> - `platforms;android-36` + `build-tools;36.0.0`：Flutter 3.41+ 要求 SDK 36
> - `system-images;android-34;google_apis;arm64-v8a`：模擬器使用的系統映像（API 34, ARM64）

---

## 7. 設定環境變數

在 `~/.zshrc`（或 `~/.bash_profile`）加入以下內容：

```bash
# Android SDK
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# JDK 17 for Android SDK
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
export PATH="$JAVA_HOME/bin:$PATH"
```

套用變更：

```bash
source ~/.zshrc
```

驗證：

```bash
which sdkmanager   # 應顯示 ~/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager
which adb          # 應顯示 ~/Library/Android/sdk/platform-tools/adb
java --version     # 應顯示 openjdk 17.x
echo $ANDROID_HOME # 應顯示 /Users/<你的帳號>/Library/Android/sdk
```

---

## 8. 接受 Android SDK Licenses

```bash
yes | sdkmanager --licenses
```

全部接受後尾部會顯示 `All SDK package licenses accepted`。

---

## 9. 建立 Android 模擬器 (AVD)

建立一台 Pixel 7 模擬器（API 34）：

```bash
echo "no" | avdmanager create avd \
  -n pixel7 \
  -k "system-images;android-34;google_apis;arm64-v8a" \
  -d "pixel_7" \
  --force
```

確認建立成功：

```bash
avdmanager list avd
```

應顯示 `Name: pixel7`。

---

## 9.5. iOS 模擬器設定

如果需要在 iOS 模擬器上執行，還需要以下額外設定。

### 9.5.1 安裝 Xcode

從 Mac App Store 安裝 Xcode 16+，或使用已安裝的版本。

確認 Xcode command line tools：

```bash
xcode-select --install   # 如果尚未安裝
xcodebuild -version      # 應顯示 Xcode 16.x
```

### 9.5.2 安裝 CocoaPods

```bash
brew install cocoapods
```

確認：

```bash
pod --version   # 應顯示 1.x
```

### 9.5.3 下載 iOS Simulator Runtime

```bash
xcodebuild -downloadPlatform iOS
```

> 下載約 8–9 GB，需要一些時間。完成後可用以下指令確認：

```bash
xcrun simctl list runtimes
# 應顯示 iOS 18.x
```

### 9.5.4 建立 iOS 模擬器

Xcode 通常會自帶預設模擬器。確認可用的模擬器：

```bash
xcrun simctl list devices available | grep iPhone
```

如果沒有，手動建立一台：

```bash
xcrun simctl create "iPhone 16" "com.apple.CoreSimulator.SimDeviceType.iPhone-16" "com.apple.CoreSimulator.SimRuntime.iOS-18-6"
```

---

## 10. 驗證環境 — flutter doctor

```bash
flutter doctor
```

確保以下項目為 ✓：

```
[✓] Flutter (Channel stable, 3.x)
[✓] Android toolchain - develop for Android devices (Android SDK version 36.0.0)
```

> Xcode 相關的警告可以忽略（只影響 iOS，不影響 Android）。

---

## 11. 安裝 Python 依賴

在專案根目錄：

```bash
cd /path/to/time_off_planning_system
poetry env use python3.11
poetry install
```

這會安裝 `flet`、`httpx`、`reflex` 等所有依賴。

---

## 12. 啟動應用程式

需要 **兩個終端**：

### 終端 A — 啟動後端 API 伺服器

```bash
cd /path/to/time_off_planning_system
poetry run ./reflex_rerun.sh
```

等待看到伺服器就緒的訊息（前端 port 3000、後端 port 8000）。

### 終端 B — 啟動 Android 模擬器 + Flet App

**步驟 1：啟動模擬器**

```bash
emulator -avd pixel7 &
```

等待模擬器完全開機（看到手機桌面）。可用以下指令確認裝置就緒：

```bash
adb devices
# 應顯示 emulator-5554  device
```

**步驟 2：執行 Flet App（在模擬器上）**

```bash
cd /path/to/time_off_planning_system
poetry run flet run flet_app/main.py --android
```

> Flet 會自動打包並安裝 APK 到模擬器上。首次執行會比較慢（需要編譯 Flutter 專案）。

### 終端 C（替代）— 啟動 iOS 模擬器 + Flet App

**步驟 1：啟動 iOS 模擬器**

```bash
open -a Simulator
```

或指定特定模擬器：

```bash
xcrun simctl boot "iPhone 16"
open -a Simulator
```

等待模擬器完全開機。可用以下指令確認裝置就緒：

```bash
xcrun simctl list devices booted
# 應顯示一台 Booted 的 iPhone
```

**步驟 2：執行 Flet App（在 iOS 模擬器上）**

```bash
cd /path/to/time_off_planning_system
poetry run flet run flet_app/main.py --ios
```

> Flet 會自動編譯並安裝到 iOS 模擬器上。首次執行需要較長時間（CocoaPods 安裝 + Flutter 編譯）。

### 其他啟動模式

**桌面模式（不需要模擬器）：**

```bash
cd /path/to/time_off_planning_system
API_BASE_URL="http://127.0.0.1:8000" poetry run python flet_app/main.py
```

**Web 模式（在瀏覽器中執行）：**

```bash
cd /path/to/time_off_planning_system
API_BASE_URL="http://127.0.0.1:8000" poetry run flet run flet_app/main.py --web --port 8550
```

然後瀏覽器打開 `http://localhost:8550`。手機也可以連同一個 WiFi 後訪問 `http://<Mac 的 IP>:8550`。

---

## 13. API Base URL 說明

`flet_app/api_client.py` 中的 `DEFAULT_BASE` 預設為 `http://10.0.2.2:8000`。

| 執行環境 | API Base URL | 說明 |
|----------|-------------|------|
| Android 模擬器 | `http://10.0.2.2:8000` | `10.0.2.2` 是 Android 模擬器存取 host 的特殊 IP |
| iOS 模擬器 | `http://127.0.0.1:8000` | iOS 模擬器與 host 共用網路，直接連 localhost |
| 桌面 / Web | `http://127.0.0.1:8000` | 直接連本機 |
| 實體手機（同 WiFi） | `http://<Mac 的 IP>:8000` | 例如 `http://192.168.1.100:8000` |

> **注意**：`api_client.py` 會自動偵測平台並選擇正確的 Base URL。Android 環境偵測到 `ANDROID_ROOT` 時使用 `10.0.2.2`，其餘平台預設 `127.0.0.1`。也可透過環境變數 `API_BASE_URL` 手動覆蓋。

可透過環境變數 `API_BASE_URL` 覆蓋，例如：

```bash
API_BASE_URL="http://127.0.0.1:8000" poetry run python flet_app/main.py
```

---

## 14. 預設帳號

| 角色 | 帳號 | 密碼 |
|------|------|------|
| 一般使用者 | admin | admin123 |
| 超級管理者 | admin | admin |

---

## 15. 常見問題

### Q: `sdkmanager` 顯示 "This tool requires JDK 17 or later"

確認 `JAVA_HOME` 指向 JDK 17：

```bash
echo $JAVA_HOME
java --version  # 應為 17.x
```

### Q: `flutter doctor` 顯示 "Flutter requires Android SDK 36"

安裝 SDK 36：

```bash
sdkmanager "platforms;android-36" "build-tools;36.0.0"
```

### Q: 模擬器上 App 無法連線到後端

1. 確認後端已啟動（`poetry run ./reflex_rerun.sh`）
2. 確認 API Base URL 是 `http://10.0.2.2:8000`（Android 模擬器專用）
3. 確認後端綁定在 `0.0.0.0:8000` 而非只有 `127.0.0.1:8000`

### Q: 首次 `flet run --android` 非常慢

正常現象。首次需要下載 Gradle 依賴並編譯 Flutter 專案，後續執行會快很多。

### Q: macOS 上 Android 模擬器跑不起來

確認你的 Mac 是 Apple Silicon 且安裝了 `arm64-v8a` 的系統映像（非 `x86_64`）。

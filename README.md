# Time-Off Planning System

 by Python Reflex
> Important: Before working on this project, read [AGENTS.md](AGENTS.md) for required workflows and tooling expectations.

## Usage Guide

Once the app is running at `http://localhost:3000`, here's how to get started.

### For Admins

1. **Log in as Admin** — Go to the login page and click **"Admin Login"** at the bottom. The default admin credentials are:
   - **Username:** `admin`
   - **Password:** `admin`

2. **Admin Dashboard** — After logging in, you'll see the Admin Dashboard with two tabs:
   - **User Management** — Add, edit, or delete user accounts. You can create usernames and passwords for your team members here.
   - **Message Board** — View requests from users who need account setup or password resets. Check this board regularly and create/update accounts accordingly.

3. **Typical workflow:**
   - Share the app URL with your team.
   - Team members submit a request via the **Contact Admin** form (accessible from the login page).
   - You review requests on the **Message Board** tab, then go to **User Management** to create their accounts.
   - Once done, let them know their credentials so they can log in.

### For Users

1. **Get an account** — If you don't have an account yet:
   - Go to the login page and click **"Contact Admin"**.
   - Fill in your Employee ID, name, email, preferred contact method, and a message describing what you need (e.g., "Please create an account for me").
   - The admin will create your account and share your credentials with you.

2. **Self-register** — Alternatively, you can click **"Don't have an account?"** on the login page to register yourself directly.

3. **Log in** — Enter your username and password on the login page.

4. **My Leaves** — After logging in, you land on the **My Leaves** page where you can:
   - **Add** a new leave by clicking the "Add Leave" button.
   - Pick a date, set start/end times, and optionally add a note.
   - **Edit** or **Delete** existing leave records.
   - The system automatically detects time conflicts with your other bookings.

5. **Shared Calendar** — Click **"Shared Calendar"** in the navigation bar to see everyone's scheduled leaves in one view. Switch between **Month**, **Week**, and **Day** views to plan around your team's availability.

### Language

The app supports **English** and **Traditional Chinese (繁體中文)**. Use the language toggle in the navigation bar to switch.


## Getting Started

> Before making changes, read the project guidelines in [AGENTS.md](AGENTS.md).

This project is managed with [Poetry](https://python-poetry.org/).

### Prerequisites

Based on this project's dependencies, install the following system-level packages first via Homebrew (macOS):

```bash
brew install python@3.11  poetry
```

| Package | Reason |
|---------|--------|
| `python@3.11` | The project requires Python ~3.11 as specified in `pyproject.toml` |
| `poetry` | Python dependency manager used to manage this project |

After installing Playwright (via `poetry install`), you also need to download browser binaries:

```bash
poetry run playwright install
```


### Installation

1. (Recommended) Configure Poetry to store the virtual environment inside the project directory. This makes it easier for IDEs and AI agents to discover and analyze dependency source code:

```bash
poetry config virtualenvs.in-project true
```

> This is a global one-time setting. After this, every project will create its `.venv/` under the project root instead of a shared cache folder (`~/Library/Caches/pypoetry/virtualenvs/`). The `.venv/` directory is already in `.gitignore`.

2. Ensure Poetry uses Python 3.11:

```bash
poetry env use python3.11
poetry env info
```

3. Install dependencies:

```bash
poetry install
```

### Running the App

Start the development server:

```bash
poetry run ./reflex_rerun.sh
```

The application will be available at `http://localhost:3000`.

### Clean Rebuild & Run

To fully clean the environment, reinstall all dependencies, and start the app in one step:

```bash
./proj_reinstall.sh --with-rerun
```

This will remove existing Poetry virtual environments and Reflex artifacts, recreate the environment from scratch, and automatically launch the app afterwards.

### macOS GUI Launcher (`launcher.sh`)

`launcher.sh` is a **macOS-only** development/testing tool that provides a native AppleScript dialog for managing the app and mobile emulators. It is not required for normal use — it's a convenience wrapper for developers on macOS.

```bash
./launcher.sh
```

The launcher shows a status dashboard and lets you:

| Action | What it does |
|--------|-------------|
| **Start / Stop Web App** | Start or kill the Reflex dev server (ports 3000 & 8000) via `poetry run ./reflex_rerun.sh` |
| **Run on Android Emulator** | Build the Flet APK, boot an Android emulator, install & launch the app |
| **Run on iOS Simulator** | Build the Flet iOS app, boot an iPhone simulator, install & launch the app |

#### Dependencies per feature

If the launcher shows no response or an error for a specific action, you likely need to install the corresponding dependencies:

| Feature | Required tools | How to install |
|---------|---------------|----------------|
| **Web App** | `python3.11`, `poetry` | `brew install python@3.11 poetry` |
| **Android Emulator** | Android SDK (`adb`, `emulator`, `avdmanager`), Java | Install [Android Studio](https://developer.android.com/studio) and configure `ANDROID_HOME` in your shell profile. You also need at least one AVD (Android Virtual Device) created. |
| **iOS Simulator** | Xcode, Xcode Command Line Tools (`xcrun`, `simctl`) | Install Xcode from the App Store, then run `xcode-select --install`. At least one iPhone simulator runtime must be downloaded (Xcode → Settings → Platforms). |
| **Flet build (both mobile)** | `flet` CLI (included in Poetry deps) | Already installed via `poetry install` |

#### Troubleshooting

- **Dialog doesn't appear at all** — The script uses `osascript` (AppleScript), which is only available on macOS. It will not work on Linux or Windows.
- **"adb not found"** — Android SDK is not on your `PATH`. Make sure `ANDROID_HOME` is set in `~/.zshrc` and `$ANDROID_HOME/platform-tools` is in `PATH`.
- **"No Android AVD found"** — Create one first, e.g.:
  ```bash
  avdmanager create avd -n pixel7 -k "system-images;android-34;google_apis;arm64-v8a" -d "pixel_7"
  ```
- **"No available iPhone simulator found"** — Open Xcode → Settings → Platforms and download a simulator runtime (e.g. iOS 17).
- **Web app doesn't start** — Make sure ports 3000 and 8000 are free. Run `lsof -ti:3000,8000` to check for lingering processes.

---


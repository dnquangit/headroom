# HOW-TO-RUN

This guide walks you through running Claude Code through the Headroom proxy with a custom Anthropic-compatible provider.

## Installation

### 1. Clone the repository

```bash
git clone <source-url>
cd <source-directory>
```

### 2. Install in development mode

```bash
pip install -e .
```

## Usage from your project

If your project uses Claude Code with the z.AI wrapper (or any other Anthropic-compatible gateway), follow these steps:

## Prerequisites — Clear conflicting environment variables

> :warning: This is **not** a Headroom issue — it applies whenever you use Claude Code with multiple API providers. Shell-level environment variables take precedence over `~/.claude/settings.json` and `<project>/.claude/settings.local.json`. The usual symptom is `401 Unauthorized` even when your API key is valid.
>
> **Only follow this section if Step 1 below fails.**

Three variables can interfere:

| Variable               | Why it causes problems                                                 |
|------------------------|-----------------------------------------------------------------------|
| `ANTHROPIC_AUTH_TOKEN` | Overrides the token configured for your provider                      |
| `ANTHROPIC_API_KEY`    | Same — overrides provider auth                                         |
| `ANTHROPIC_BASE_URL`   | Overrides the URL Headroom writes into settings, bypassing the proxy  |

### Windows — PowerShell

```powershell
# 1. Permanently remove from Windows user-level environment
[Environment]::SetEnvironmentVariable('ANTHROPIC_AUTH_TOKEN', $null, 'User')
[Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY',   $null, 'User')
[Environment]::SetEnvironmentVariable('ANTHROPIC_BASE_URL',  $null, 'User')

# 2. Remove from the current PowerShell session (takes effect immediately)
Remove-Item Env:\ANTHROPIC_AUTH_TOKEN, Env:\ANTHROPIC_API_KEY, Env:\ANTHROPIC_BASE_URL -ErrorAction SilentlyContinue
```

### Windows — Command Prompt (cmd.exe)

```cmd
REM 1. Permanently remove from Windows user-level environment.
REM    Shells out to PowerShell for the actual deletion:
powershell -Command "[Environment]::SetEnvironmentVariable('ANTHROPIC_AUTH_TOKEN', $null, 'User'); [Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', $null, 'User'); [Environment]::SetEnvironmentVariable('ANTHROPIC_BASE_URL', $null, 'User')"

REM 2. Remove from the current cmd.exe session (takes effect immediately)
set ANTHROPIC_AUTH_TOKEN=
set ANTHROPIC_API_KEY=
set ANTHROPIC_BASE_URL=
```

### macOS / Linux (bash / zsh)

```bash
# 1. For the current shell session
unset ANTHROPIC_AUTH_TOKEN ANTHROPIC_API_KEY ANTHROPIC_BASE_URL

# 2. (Optional) Remove the exports from your shell rc file
#    Edit ~/.bashrc, ~/.zshrc, or ~/.profile and delete the export lines
```

---

## Step 1 — Sanity check: can Claude Code reach your wrapper?

```bash
cd your-project
claude "say hello"
```

- **Expected**: Claude Code starts and replies "hello" through your wrapper provider.
- **If `401 Unauthorized`**: go back to **Prerequisites** above and clear the conflicting environment variables, then retry.

---

## Step 2 — Logout

```bash
claude logout
```

Clears the session so the next launch picks up the proxy-routed configuration cleanly.

---

## Step 3 — Override the target URL through Headroom

**The idea**: instead of pointing Claude Code directly at your provider's URL (e.g. `https://api.minimax.io/anthropic`), you let Headroom's local proxy intercept the traffic and forward it to the provider. This allows Headroom to compress requests before they leave your machine.

### PowerShell

```powershell
cd your-project
$env:ANTHROPIC_TARGET_API_URL = "https://api.minimax.io/anthropic"
headroom wrap claude
```

### macOS / Linux

```bash
cd your-project
export ANTHROPIC_TARGET_API_URL="https://api.minimax.io/anthropic"
headroom wrap claude
```

### Verify Headroom is in the path

After `headroom wrap claude` starts, open one of these files and check the value:

- `~/.claude/settings.json`
- `<your-project>/.claude/settings.local.json`

You should see:

```json
"ANTHROPIC_BASE_URL": "http://127.0.0.1:8787"
```

> :warning: If `ANTHROPIC_BASE_URL` is still pointing at your provider's URL (e.g. `https://api.minimax.io/anthropic`), Headroom is **not** in the path and savings will not apply. Stop the session (`Ctrl+C`), re-check **Prerequisites**, and rerun.

---

## Step 4 — Enjoy

Talk to Claude Code as usual. All Anthropic-format traffic now flows through the local Headroom proxy, which compresses requests before forwarding them to your provider.

---

## Step 5 — On exit

When you stop the session (`Ctrl+C` or `exit`), `headroom wrap` automatically restores `ANTHROPIC_BASE_URL` to its previous value (e.g. `https://api.minimaxi.com/anthropic`). No manual cleanup needed.

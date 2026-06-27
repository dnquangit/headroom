# HOW-TO-RUN

This project adds support for configuring custom Anthropic-compatible base URLs (like z.AI) in Headroom.

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

### Windows Setup

Configure the environment variables:

```cmd
setx ANTHROPIC_BASE_URL https://api.z.ai/api/anthropic
setx ANTHROPIC_AUTH_TOKEN your_zai_api_key
```

Then run the wrapper:

```cmd
headroom wrap claude
```

### Linux/macOS Setup

Configure the environment variables:

```bash
export ANTHROPIC_BASE_URL=https://api.z.ai/api/anthropic
export ANTHROPIC_AUTH_TOKEN=your_zai_api_key
```

Then run the wrapper:

```bash
headroom wrap claude
```

## How it works

This implementation preserves your custom `ANTHROPIC_BASE_URL` setting and forwards it to the Headroom proxy, so compressed requests are properly routed to your chosen Anthropic-compatible gateway (z.AI or others).

The custom URL is captured before it would be overwritten by the proxy URL, ensuring your gateway configuration is respected throughout the wrap session.

## Environment Variables

- `ANTHROPIC_BASE_URL`: Your custom Anthropic-compatible API endpoint (e.g., `https://api.z.ai/api/anthropic`)
- `ANTHROPIC_AUTH_TOKEN`: Your API authentication token for the custom gateway

## Additional Notes

- The default Anthropic endpoint (`https://api.anthropic.com`) is automatically detected and not forwarded (the proxy already uses it by default)
- Loopback protection prevents the proxy from being configured to point to itself
- Compatible with Azure AI Foundry and Vertex modes - this enhancement only applies to the default Anthropic path

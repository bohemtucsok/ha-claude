# 📱 Messaging Integration Guide

This Amira addon supports **Telegram**, **WhatsApp**, and **Discord** messaging integrations, allowing you to chat with Amira from your favorite messaging apps.

## ✨ Features

- **Telegram Bot**: Long polling support with background thread
- **WhatsApp**: Twilio integration with webhook support
- **Discord Bot**: Token-based bot integration with optional channel/user allow-lists
- **Persistent History**: Automatic chat history storage (last 50 messages per user)
- **Context Aware**: AI responses include conversation context
- **Multi-channel**: Use Telegram, WhatsApp, and Discord simultaneously
- **Token Efficient**: Device control uses minimal tokens (interpretation only)

---

## 🤖 Telegram Setup

### Step 1: Create a Telegram Bot

1. Open Telegram and search for **`@BotFather`**
2. Send `/newbot`
3. Follow the prompts:
   - **Bot name**: e.g., "My Home Assistant"
   - **Username**: e.g., `my_ha_bot` (must end with `_bot`)
4. You'll receive a **TOKEN** that looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
5. Keep this token safe!

### Step 2: Get Your Chat ID (Optional but Recommended)

1. Message your bot with: `/start`
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find your `"chat"."id"` in the response

### Step 3: Configure in Home Assistant

1. Open Home Assistant **Settings** → **Add-ons** → **Amira**
2. Go to **Configuration** tab
3. Paste the token in **Telegram Bot Token**:
   ```
   123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   ```
4. Click **Save** → **Restart**

### Step 4: Start Chatting

1. Message your Telegram bot
2. It will respond with AI responses from Claude
3. Full conversation context is maintained

### Example Conversation

```
You: What's the temperature?
Claude: I'll check the temperature sensor.
Temperature: 22.5°C

You: Turn on the kitchen light
Claude: I'm turning on the kitchen light now.
Done!

You: What did I just turn on?
Claude: You just turned on the kitchen light.
```

---

## 💬 WhatsApp Setup

### Step 1: Create Twilio Account

1. Visit [twilio.com](https://twilio.com)
2. Sign up (free account with $15 credit)
3. Go to **Console** → **Phone Numbers** → **Manage Numbers**
4. Get your **Account SID** and **Auth Token** from the console
5. Keep these credentials safe!

### Step 2: Enable WhatsApp in Twilio

1. In Twilio Console, go to **Messaging** → **Services**
2. Create a new **Messaging Service**
3. Select **WhatsApp** as a channel
4. Follow the verification process
5. You'll get a **WhatsApp From Number** (your bot number)

### Step 3: Configure in Home Assistant

1. Open Home Assistant **Settings** → **Add-ons** → **Amira**
2. Go to **Configuration** tab
3. Fill in the WhatsApp fields:
   - **Twilio Account SID**: Your Account SID
   - **Twilio Auth Token**: Your Auth Token
   - **Twilio WhatsApp From**: Your Twilio WhatsApp sender (E.164). You can use either `+19876543210` or `whatsapp:+19876543210`.
4. Note: You may need to set up a **webhook URL** (this will be explained below)
5. Click **Save** → **Restart**

### Step 4: Configure Webhook (Important!)

For Twilio to send messages to Amira, Twilio must reach the **Amira backend** on the internet.

Important notes:

- Home Assistant **Ingress URLs are not stable** (they include a session token), so they are not suitable for Twilio.
- You need a **public HTTPS URL** that forwards to the add-on backend (port 5010) or an equivalent reverse-proxy path.

1. In Twilio Console, go to **Messaging** → **Settings**
2. Find **Webhook URLs**
3. Set **POST Webhook URL** to:
   ```
   https://<your-public-amira-url>/api/whatsapp/webhook
   ```
   Example (direct port mapping): `https://amira.example.com:5010/api/whatsapp/webhook`
4. Save the settings
5. Twilio will now send incoming WhatsApp messages to your addon

### Step 5: Start Chatting

1. Add the WhatsApp bot number to your contacts
2. Message it via WhatsApp
3. You'll receive AI responses via WhatsApp

### Example Conversation

```
You: Turn on the living room light
Claude: I'm turning on the living room light now. Done!

You: What's the current humidity?
Claude: The humidity is 65%.

You: Create a reminder for tomorrow
Claude: I'll create a reminder for tomorrow at 9 AM.
```

---

## 🟣 Discord Setup

### Step 1: Create a Discord Application + Bot

1. Open the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and choose a name
3. Open **Bot** in the left menu, then click **Add Bot**
4. Copy the **Bot Token** (keep it private)
5. In **Privileged Gateway Intents**, enable:
   - **Message Content Intent**

### Step 2: Invite the Bot to Your Server

1. In the Developer Portal, open **OAuth2** → **URL Generator**
2. Select scopes:
   - `bot`
3. Select bot permissions:
   - `View Channels`
   - `Read Message History`
   - `Send Messages`
4. Open the generated URL and invite the bot to your server

### Step 3: Configure in Home Assistant

1. Open Home Assistant **Settings** → **Add-ons** → **Amira**
2. Open Amira, then go to **Settings** (gear icon) → **Messaging**
3. Enable **Discord**
4. Fill in:
   - **Discord Bot Token**
   - **Allowed Channel IDs** (optional, comma-separated)
   - **Allowed User IDs** (optional, comma-separated)
5. Save settings

### Step 4: Get Channel/User IDs (Optional but Recommended)

1. In Discord, open **User Settings** → **Advanced** → enable **Developer Mode**
2. Right-click a channel → **Copy Channel ID**
3. Right-click a user → **Copy User ID**
4. Paste IDs in Amira settings (comma-separated)

### Step 5: Start Chatting

1. Open one allowed channel
2. Mention the bot or send a direct message (based on your server setup)
3. Amira replies in Discord with full context

---

## 🔐 Security & Privacy

### Telegram
- **Long Polling**: Your addon polls Telegram servers for messages
- **HTTPS**: Communication with Telegram is encrypted
- **Bot Token**: Keep it private — it's unique to your bot

### WhatsApp (Twilio)
- **Webhook Signature**: Twilio signs all webhooks with HMAC-SHA1 — Amira verifies every request automatically
- **Auth Token**: Keep it private — equivalent to a password

### Discord
- **Bot Token**: Keep it private — equivalent to full bot account access
- **Allow-lists**: Restrict channels/users with `DISCORD_ALLOWED_CHANNEL_IDS` and `DISCORD_ALLOWED_USER_IDS`

### Best Practices
- Don't share tokens or credentials
- Monitor addon logs for unexpected access
- Regenerate tokens if compromised

---

## 📊 API Endpoints

### Get Messaging Statistics

```bash
GET /api/messaging/stats
```

**Response:**
```json
{
  "total_chats": 12,
  "total_messages": 486,
  "channels": {
    "telegram": {
      "enabled": true,
      "chats": 8,
      "messages": 324
    },
    "whatsapp": {
      "enabled": true,
      "chats": 4,
      "messages": 162
    },
    "discord": {
      "enabled": true,
      "chats": 3,
      "messages": 91
    }
  }
}
```

### Send Telegram Message

```bash
POST /api/telegram/message
```

**Request:**
```json
{
  "user_id": "123456",
  "chat_id": "123456",
  "text": "What's the temperature?"
}
```

### WhatsApp Webhook

Twilio will POST to: `POST /api/whatsapp/webhook`

Your addon handles this automatically.

### Send Discord Message

```bash
POST /api/discord/message
```

---

## 🛠️ Troubleshooting

### Telegram Not Working

1. **Check Token**:
   ```bash
   curl https://api.telegram.org/botYOUR_TOKEN/getMe
   ```
   Should return bot info

2. **Check Logs**:
   - Look for error messages in Home Assistant logs
   - Enable **Debug Mode** in addon settings

3. **Network Issues**:
   - Ensure addon can reach `api.telegram.org`
   - Check firewall rules

### WhatsApp Not Working

1. **Verify Webhook**:
   A plain `curl` POST will return **403** because Amira validates Twilio's webhook signature.
   Instead, use Twilio Console message logs/debugger to verify delivery status.

2. **Check Signature Validation**:
   - Ensure **Auth Token** is correct
   - Webhook signatures will fail if token is wrong

3. **Twilio Console**:
   - Check message logs in Twilio Console
   - Look for webhook delivery errors

### Discord Not Working

1. **Check Token**:
   - Confirm the bot token is valid and not regenerated
2. **Check Intents**:
   - Ensure **Message Content Intent** is enabled in Discord Developer Portal
3. **Check Allow-lists**:
   - If allow-lists are set, verify channel/user IDs are correct
4. **Check Bot Permissions**:
   - Bot needs `View Channels`, `Read Message History`, and `Send Messages`

---

## 💬 Device Control via Messaging

### Examples

```
Telegram: "Turn on the bedroom light"
Claude: Turns on bedroom light via Home Assistant

WhatsApp: "Get temperature"
Claude: Reads temperature sensor and responds

Discord: "Set living room light to 30%"
Claude: Calls Home Assistant service and confirms result

Telegram: "Create automation"
Claude: Helps you set up automations via natural language
```

### How It Works

1. Message is sent to bot
2. Bot adds message to chat history
3. Claude interprets the natural language command
4. If it's a device control command:
   - **NO token consumption** for execution
   - Direct call to Home Assistant service
   - Response sent back with status
5. Chat history updated for context

---

## 🛠️ Advanced Features via Messaging

Enable these in Home Assistant Configuration for extended messaging capabilities:

| Feature | What It Does | Learn More |
|---------|-------------|-----------|
| **Device Control** | "Turn on kitchen light" → executed via HA | [DOCS.md](../addons/claude-backend/DOCS.md) |
| **Persistent Memory** | AI remembers past conversations | [DOCS.md](../addons/claude-backend/DOCS.md) |
| **Custom Tools** | Add API integrations via MCP | [MCP.md](MCP.md) |
| **Image Analysis** | Send images for AI analysis | [DOCS.md](../addons/claude-backend/DOCS.md) |

---

## 📞 Support

Having issues? Check:

1. **Logs**: Home Assistant → Settings → System → Logs
2. **Health Status**: `/api/messaging/stats`
3. **Credentials**: Verify tokens are correct and active
4. **Network**: Ensure connectivity to external APIs

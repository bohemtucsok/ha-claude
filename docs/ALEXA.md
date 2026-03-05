# 🔊 Alexa Integration Guide

Connect your **Amazon Alexa** devices to Amira and control your smart home with natural language through any Echo device, Fire TV, or Alexa-enabled speaker.

## ✨ Features

- **Voice control**: Ask Amira anything through Alexa — lights, sensors, temperature, automations
- **Conversational**: Multi-turn conversations within the same session
- **Multi-language**: Responds in the language configured in Amira (Italian, English, Spanish, French)
- **Full AI power**: Same AI capabilities as the web chat — tools, intents, context-aware responses
- **No cloud dependency**: Everything runs locally on your Home Assistant (except Alexa voice processing)

---

## 📋 Prerequisites

Before starting, make sure you have:

1. **Amira addon** installed and running on Home Assistant
2. **HTTPS access** to your Home Assistant (with a valid SSL certificate)
3. An **Amazon Developer account** (free) — [developer.amazon.com](https://developer.amazon.com)
4. The Amira addon **port 5010** accessible from the internet (see [Network Setup](#network-setup))

---

## 🌐 Network Setup

Alexa requires an **HTTPS endpoint** on port 443 to send requests. Since the Amira addon runs on port 5010, you need a reverse proxy to forward requests.

### Option A: Dedicated Subdomain (Recommended)

Use a subdomain like `amira.yourdomain.com` pointing to your Amira addon.

#### 1. DNS Record

Add a DNS record at your domain registrar:

| Type | Name | Value |
|------|------|-------|
| **CNAME** | `amira` | `ha.yourdomain.com` |

Or an **A** record pointing to the same public IP as your HA instance.

#### 2. Reverse Proxy Rule

Configure your reverse proxy to forward the subdomain to port 5010:

**Nginx Proxy Manager / Synology DSM:**

| Field | Value |
|-------|-------|
| Source Protocol | HTTPS |
| Source Hostname | `amira.yourdomain.com` |
| Source Port | 443 |
| Destination Protocol | HTTP |
| Destination Hostname | Your HA local IP (e.g. `192.168.1.x`) |
| Destination Port | 5010 |

**Nginx (manual config):**

```nginx
server {
    listen 443 ssl;
    server_name amira.yourdomain.com;

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://192.168.1.x:5010;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
    }
}
```

**Caddy:**

```
amira.yourdomain.com {
    reverse_proxy 192.168.1.x:5010
}
```

#### 3. SSL Certificate

Make sure you have a valid SSL certificate for the subdomain:
- **Wildcard certificate** (`*.yourdomain.com`) — works automatically
- **Let's Encrypt** — request a new certificate for `amira.yourdomain.com`
- **Synology DSM** — Settings → Security → Certificate → Add (Let's Encrypt)

### Option B: Same Domain, Different Port

If you can't create a subdomain, use a different port (e.g. 5443):

1. Forward port 5443 on your router to your HA machine port 5010
2. Create a reverse proxy rule: `ha.yourdomain.com:5443` → `localhost:5010`
3. Alexa endpoint will be: `https://ha.yourdomain.com:5443/api/alexa/webhook`

> ⚠️ Some corporate firewalls block non-standard ports. The subdomain approach is more reliable.

### Verify Connectivity

Test your endpoint before configuring Alexa:

```bash
curl -X POST https://amira.yourdomain.com/api/alexa/webhook \
  -H "Content-Type: application/json" \
  -d '{"request":{"type":"LaunchRequest"},"session":{"sessionId":"test123","attributes":{}}}'
```

Expected response:
```json
{
  "version": "1.0",
  "response": {
    "outputSpeech": {
      "type": "PlainText",
      "text": "Ciao! Sono Amira, la tua assistente di casa. Chiedimi qualsiasi cosa!"
    },
    "shouldEndSession": false
  }
}
```

---

## 🛠️ Create the Alexa Skill

### Step 1: Amazon Developer Console

1. Go to [developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask)
2. Sign in with your Amazon account (the same one linked to your Alexa devices)
3. Click **"Create Skill"**

### Step 2: Skill Settings

| Setting | Value |
|---------|-------|
| **Skill name** | `Amira` |
| **Primary locale** | `Italian (IT)` (or your language) |
| **Type of experience** | Other |
| **Model** | Custom |
| **Hosting** | Provision your own |

Click **"Next"** → select **"Start from Scratch"** → **"Create Skill"**

### Step 3: Invocation Name

1. In the left sidebar, click **"Invocations"** → **"Skill Invocation Name"**
2. Set the invocation name to: `amira`
3. Click **"Save"**

> 💡 The invocation name is what you say to activate the skill: "Alexa, apri **amira**"

### Step 4: Create the Intent

1. In the left sidebar, click **"Interaction Model"** → **"Intents"**
2. Click **"Add Intent"**
3. Select **"Create custom intent"**
4. Name: `AskAmiraIntent`
5. Click **"Create custom intent"**

### Step 5: Add the Slot

1. In the **Intent Slots** section at the bottom, add a new slot:
   - **Name**: `query`
   - **Slot Type**: `AMAZON.SearchQuery`

### Step 6: Sample Utterances

Add these sample utterances (one per line):

```
chiedi {query}
dimmi {query}
domanda {query}
vorrei sapere {query}
fammi sapere {query}
rispondi {query}
```

> 📝 Each utterance needs a "carrier phrase" before the `{query}` slot. Amazon requires at least one word before `AMAZON.SearchQuery` slots.

Click **"Save Model"**

### Step 7: Configure the Endpoint

1. In the left sidebar, click **"Endpoint"**
2. Select **"HTTPS"**
3. In **Default Region**, enter your endpoint URL:
   ```
   https://amira.yourdomain.com/api/alexa/webhook
   ```
4. For **SSL certificate type**, select:
   - `My development endpoint has a certificate from a trusted certificate authority`
5. Click **"Save Endpoints"**

### Step 8: Build the Model

1. Click **"Build Model"** (top of the page)
2. Wait for the build to complete (1-2 minutes)
3. You should see: ✅ *"Build Successful"*

---

## 🧪 Testing

### Test in the Developer Console

1. Go to the **"Test"** tab
2. Enable testing: set the dropdown to **"Development"**
3. Type or say: `apri amira`
4. Amira should respond with a greeting
5. Then type: `chiedi quante luci sono accese`
6. Amira should respond with the light status

### Test on Your Alexa Device

Once the build succeeds, the skill is **automatically available** on all Alexa devices linked to the same Amazon account:

- **"Alexa, apri Amira"** — Opens the skill, Amira greets you
- *(then speak freely)* **"chiedi accendi la luce del salotto"** — Amira processes the command
- **"Alexa, chiedi ad Amira dimmi che temperatura c'è"** — One-shot command (without opening first)

---

## 💬 Usage Examples

| What you say | What happens |
|-------------|-------------|
| "Alexa, apri Amira" | Activates the skill, Amira greets you |
| "chiedi accendi la luce della cucina" | Turns on the kitchen light |
| "dimmi che temperatura c'è in camera" | Reports bedroom temperature |
| "chiedi quante luci sono accese" | Counts active lights |
| "domanda qual è lo stato dell'allarme" | Reports alarm status |
| "chiedi abbassa il riscaldamento a 20 gradi" | Sets heating to 20°C |
| "Alexa, stop" | Closes the skill |

### One-Shot Commands

You can also use Amira without opening the skill first:

```
"Alexa, chiedi ad Amira di accendere tutte le luci"
"Alexa, chiedi ad Amira che tempo fa"
"Alexa, chiedi ad Amira di spegnere il condizionatore"
```

---

## ❓ Troubleshooting

### "Non ho capito" / Alexa doesn't understand

- Make sure you're starting your request with a carrier phrase: **"chiedi..."**, **"dimmi..."**
- Check that the skill build was successful in the Developer Console
- Verify the invocation name is correct: "Alexa, apri **amira**"

### Alexa says there was an error

- Check the Amira addon logs in Home Assistant for error details
- Verify the endpoint is reachable: run the `curl` test from [Verify Connectivity](#verify-connectivity)
- Make sure the SSL certificate is valid and not expired

### Timeout / No response

- The AI might take too long to respond. Check if the same query works in the Amira web chat
- Alexa has an **8-second timeout** for skill responses. Complex queries might need optimization
- Consider using a faster AI model for Alexa interactions

### Skill not appearing on Alexa devices

- The skill appears automatically on devices linked to the **same Amazon account** used in the Developer Console
- Make sure the skill is in **"Development"** testing mode
- Try saying: "Alexa, abilita la skill Amira"

### Response is cut off

- Alexa has a speech limit of ~8000 characters. Very long AI responses are automatically trimmed to 6000 characters
- Ask more specific questions for shorter answers

---

## 🔒 Security Notes

- The Alexa webhook endpoint is accessible via HTTPS only
- For production use, consider implementing [Alexa request signature validation](https://developer.amazon.com/docs/custom-skills/host-a-custom-skill-as-a-web-service.html#verifying-that-the-request-was-sent-by-alexa)
- The skill in "Development" mode is only accessible from your Amazon account
- No Amazon credentials are stored in Amira — all authentication is handled by Amazon's skill infrastructure

---

## 📖 Additional Resources

- [Alexa Skills Kit Documentation](https://developer.amazon.com/docs/alexa/custom-skills/understanding-custom-skills.html)
- [Amazon Developer Console](https://developer.amazon.com/alexa/console/ask)
- [AMAZON.SearchQuery Slot Type](https://developer.amazon.com/docs/custom-skills/slot-type-reference.html#searchquery)

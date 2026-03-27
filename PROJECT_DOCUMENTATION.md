# Project Documentation
## Industry 4.0 Machine Monitoring System with OT Security

---

> 🇩🇪 Die deutsche Version finden Sie weiter unten.
> 🇬🇧 The German version can be found below.

---

## 🇬🇧 English

### Project Overview

This project implements a complete Industry 4.0 monitoring pipeline for a simulated factory environment. It demonstrates how modern industrial systems collect, transmit, process, store and visualise machine data in real time — using the same tools and protocols found in professional industrial environments.

The system monitors 4 machines simultaneously, calculates OEE (Overall Equipment Effectiveness) metrics, tracks downtime, and presents data through two dashboards: a live operator view (Node-RED) and a historical analytics view (Grafana).

The project also includes a complete **OT Security module** — simulating real-world cyberattacks on the MQTT infrastructure, building a rule-based Intrusion Detection System (IDS), and implementing MQTT authentication as a prevention layer.

---

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Environment                        │
│                                                             │
│  ┌──────────────┐    MQTT      ┌──────────────┐            │
│  │  Simulator   │ ──────────▶  │  Mosquitto   │            │
│  │ (4 machines) │  port 1883   │  MQTT Broker │            │
│  └──────────────┘              │  + Auth      │            │
│                                └──────┬───────┘            │
│                                       │ MQTT                │
│                                       ▼                     │
│                               ┌──────────────┐             │
│                               │   Node-RED   │             │
│                               │  port 1880   │             │
│                               │  + IDS Engine│             │
│                               └──────┬───────┘             │
│                                      │                      │
│                    ┌─────────────────┼──────────────┐      │
│                    ▼                 ▼               ▼      │
│             ┌──────────┐    ┌──────────────┐  ┌─────────┐  │
│             │ Node-RED │    │   InfluxDB   │  │ Grafana │  │
│             │Dashboard │    │  port 8086   │  │port 3000│  │
│             │+ Alerts  │    └──────────────┘  └─────────┘  │
│             └──────────┘                                    │
└─────────────────────────────────────────────────────────────┘
```

---

### Technologies Used

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.11 | Machine data simulator + attack scripts |
| paho-mqtt | 1.6.1 | MQTT client library |
| Docker | Latest | Container orchestration |
| Eclipse Mosquitto | 2.1.2 | MQTT broker with authentication |
| Node-RED | Latest | Data processing, IDS engine, live dashboard |
| node-red-contrib-influxdb | Latest | InfluxDB integration for Node-RED |
| @flowfuse/node-red-dashboard | 1.30.2 | Node-RED Dashboard 2.0 |
| InfluxDB | 2.7 | Time-series database |
| Grafana | 10.4.0 | Historical analytics + security timeline |

---

### Machine Configuration

| Machine | ON Probability | OFF Probability | Temp Range (ON) |
|---------|---------------|-----------------|-----------------|
| Machine 1 | 80% | 20% | 45–75°C |
| Machine 2 | 82% | 18% | 50–80°C |
| Machine 3 | 86% | 14% | 40–70°C |
| Machine 4 | 85% | 15% | 42–72°C |

**OEE Thresholds (Industry Standard):**
- 🔴 Below 50% — Poor
- 🟡 50–85% — Acceptable
- 🟢 Above 85% — World Class

---

### OEE Calculation

```
Availability = (Total Time - Downtime) / Total Time × 100
```

Where Total Time = messages × 3 seconds, Downtime = OFF messages × 3 seconds.

---

### Node-RED Flow Design

- **Parse & Validate** — single entry point, validates all messages
- **MQTT Wildcard** — `factory/+/data` subscribes to all 4 machines
- **IDS Engine** — security rule checker on every message
- **Machine filters** — per-machine display routing
- **Downtime & Availability** — OEE calculation using machine_id keys
- **Save to InfluxDB** — stores complete enriched payload

---

---

## OT Security Module

### What is OT Security?

**OT (Operational Technology) Security** protects industrial systems — factory machines, power grids, water treatment plants — from cyberattacks. Unlike IT security which protects data, OT security protects physical processes where a successful attack causes real-world damage.

**Why MQTT is vulnerable by default:**
- No authentication — anyone on the network can connect
- No authorisation — any client can publish to any topic
- No encryption — all messages are plain text
- No rate limiting — anyone can flood the broker

This project demonstrates all four vulnerabilities through simulated attacks, then implements defences.

---

### Reconnaissance

**Script:** `Attack Vectors/recon.py`

Before attacking, a real attacker silently observes the target. The recon script connects to Mosquitto without credentials, subscribes to `#` (all topics), and records all traffic without sending anything.

**Intelligence gathered from recon:**
```
Topics discovered  : factory/machine1-4/data
Machine IDs found  : machine1, machine2, machine3, machine4
Status values      : ON, OFF
Temperature range  : 30.25°C — 79.77°C
Message interval   : ~0.7s combined (3s per machine)
Message format     : machine_id (str), status (str),
                     temperature (float), production_count (int)
```

This reconnaissance is completely invisible — Mosquitto logs no subscriber connections by default. The attacker now knows everything needed to craft undetectable fake messages.

---

### Attack 1 — Data Injection

**Script:** `Attack Vectors/attack1.py`

Connects to Mosquitto and publishes fake sensor data to `factory/machine1/data` at the same 3-second interval as the legitimate simulator.

**Fake data characteristics:**
- Temperature: 15–25°C (suspiciously low — hiding overheating)
- Production count: 9000–9999 (unrealistically high)
- Status: always ON (hiding machine failures)

**Effect:** Node-RED receives both real and fake messages. Dashboard temperature flickers between normal and injected values. InfluxDB stores corrupted records permanently.

**Evidence:** InfluxDB temperature chart shows a violent zigzag pattern — alternating between normal operating range (45-75°C) and injected low values (15-25°C).

**Real-world equivalent:** An attacker hides a machine that is overheating. The operator sees normal readings while the machine physically destroys itself. This is the same principle used in the Stuxnet attack (2010) against Iranian nuclear centrifuges.

---

### Attack 2 — Message Flooding (DoS)

**Script:** `Attack Vectors/attack2.py`

Launches 4 simultaneous threads, each flooding one machine topic at 50 messages/second.

| Metric | Value |
|--------|-------|
| Total flood rate | ~200 messages/second |
| Normal system rate | ~1.3 messages/second |
| Amplification factor | 150× |
| Duration | 60 seconds |
| Total messages sent | 11,534 |

**Effect:** Node-RED message queue overwhelmed. Dashboard values flicker and become unreliable. Legitimate machine data buried in flood traffic.

**Real-world equivalent:** A Denial of Service (DoS) attack on an industrial control system. Operators cannot trust any readings and may be forced into emergency shutdown.

---

### Attack 3 — Identity Spoofing

**Script:** `Attack Vectors/attack3.py`

**Scenario 1 — Ghost Machine:**
Injects a fake `machine5` that doesn't exist. Node-RED's wildcard topic accepts it automatically. Ghost machine data stored permanently in InfluxDB.

**Scenario 2 — Identity Confusion:**
Sends messages with variations of valid machine IDs:

| Spoofed ID | Technique |
|-----------|-----------|
| `Machine1` | Capital letter |
| `machine_1` | Underscore |
| `machine 1` | Space injection |
| `machine-1` | Hyphen |
| `machine01` | Zero padded |
| `MACHINE1` | All caps |

**Verified result:** InfluxDB confirmed all fake IDs stored alongside legitimate data — permanently corrupting historical records and OEE analytics.

---

### Prevention — MQTT Authentication

**Files:** `mosquitto/mosquitto.conf`, `mosquitto/passwd`

**Key configuration:**
```ini
allow_anonymous false
password_file /mosquitto/config/passwd
```

**Users created:**
- `simulator` — for the machine simulator container
- `nodered` — for Node-RED subscription

**Setup steps:**
1. Create `mosquitto/mosquitto.conf` with `allow_anonymous false`
2. Create `mosquitto/passwd` with plain text credentials
3. Hash passwords using Mosquitto's tool:
   ```bash
   docker run --rm -v "./mosquitto:/mosquitto/config" \
   eclipse-mosquitto mosquitto_passwd -U /mosquitto/config/passwd
   ```
4. Mount config files in docker-compose.yml
5. Add credentials to simulator: `client.username_pw_set("simulator", "password")`
6. Add credentials in Node-RED broker Security tab

**Result from Mosquitto logs:**
```
simulator    → connected successfully (u'simulator')
nodered      → connected successfully (u'nodered')
rogue_attacker_001 → disconnected: not authorised
```

**Important limitation:** Authentication prevents unauthorised connections but not insider threats or compromised credentials. The IDS detection layer is essential as a second line of defence.

---

### Detection — IDS Engine

**Location:** Node-RED function node "IDS Engine"

Runs on every incoming MQTT message. Checks 4 rules. Outputs alert objects when threats detected.

#### Rule 1 — Unknown Machine ID
**Catches:** Attack 3 (spoofing, ghost machines)
**Severity:** HIGH

```javascript
const VALID_MACHINES = ['machine1','machine2','machine3','machine4'];
if (!VALID_MACHINES.includes(mid)) → ALERT: UNKNOWN_MACHINE_ID
```

Any message from an unrecognised machine_id triggers an immediate alert. Catches ghost machines, identity confusion, and any future unauthorised device.

#### Rule 2 — Temperature Anomaly
**Catches:** Attack 1 (data injection)
**Severity:** HIGH / CRITICAL

```javascript
// ON machine with impossibly low temperature = injection
if (status === 'ON' && temperature < 28) → TEMPERATURE_ANOMALY [HIGH]

// Any machine above safe operating limit
if (temperature > 85) → TEMPERATURE_CRITICAL [CRITICAL]
```

When a machine is ON, temperature below 28°C is physically impossible under normal operation — it indicates injected false readings designed to hide overheating.

#### Rule 3 — Message Flood Detection
**Catches:** Attack 2 (flooding)
**Severity:** CRITICAL

```javascript
// Count messages in 3-second sliding window
// Normal = ~4 messages per 3s
// Alert threshold = 10 messages per 3s (2.5× normal)
if (messagesInWindow > FLOOD_THRESHOLD) → MESSAGE_FLOOD [CRITICAL]
```

Uses a sliding window counter stored in flow context. Alert rate-limited to once per 5 seconds to prevent alert flooding during sustained attacks.

#### Rule 4 — Suspicious Production Count
**Catches:** Attack 1 (injected fake counts)
**Severity:** MEDIUM

```javascript
// Real machines start at 0 and increment 1-6 per cycle
// Attack 1 injects random counts 9000-9999
if (production_count > 8000) → SUSPICIOUS_PRODUCTION_COUNT [MEDIUM]
```

---

### Alert System

**Node-RED Dashboard popup:**
```
⚠️ [HIGH] Temp too low on machine1 — possible injection | 10:56:09 AM
```
- Appears top-right corner
- Colour coded by severity
- Auto-dismisses after 15 seconds
- All 4 alert types produce distinct messages

**InfluxDB storage:**
All alerts stored in `machine_data` bucket, `security_alerts` measurement with fields: `type`, `severity`, `machine_id`, `detail`, `timestamp`

**Grafana Security Monitor row:**
- Security Events Timeline — red bar chart showing attack periods
- Total Alerts (last 1h) — real-time alert count stat panel

---

### Lessons Learned

**1. MQTT is insecure by default**
Default Mosquitto allows anonymous connections from any network client. Security must be explicitly configured — it is not enabled out of the box. Many real factory deployments still run with no authentication.

**2. Passive reconnaissance is undetectable**
The recon script gathered complete system intelligence without sending a single message. No Mosquitto log entry exists for subscriber connections. An attacker can study a system indefinitely before attacking.

**3. Authentication alone is not enough — defence in depth is required**
MQTT authentication blocks unauthorised connections. But a compromised credential or insider threat bypasses it entirely. The IDS detection layer catches attacks that authentication cannot prevent.

**4. OT attacks target operator trust, not just data**
The most dangerous aspect of data injection is not the corrupted values — it is that the operator dashboard looks completely normal. The operator has no reason to suspect anything. This is the core principle of sophisticated OT attacks: make the monitoring system lie while physical damage occurs.

**5. Rule-based IDS has known limitations**
Our IDS detects known attack patterns with fixed thresholds. A sophisticated attacker who stays within normal temperature ranges and message rates would not be detected. Production-grade OT IDS systems (Claroty, Dragos, Nozomi Networks) use machine learning and behavioural baselines to detect subtle anomalies that rule-based systems miss.

---

### Security Architecture Summary

```
┌─────────────────────────────────────────┐
│           Defence in Depth              │
│                                         │
│  Layer 1: Prevention                    │
│  └─ MQTT Authentication                 │
│     Blocks unauthorised connections     │
│                                         │
│  Layer 2: Detection                     │
│  └─ Node-RED IDS Engine (4 rules)       │
│     Catches attacks that get through    │
│                                         │
│  Layer 3: Response                      │
│  └─ Real-time alerts (Node-RED popup)   │
│     Security audit log (InfluxDB)       │
│     Attack timeline (Grafana)           │
└─────────────────────────────────────────┘
```

---

---

## 🇩🇪 Deutsch

### Projektüberblick

Dieses Projekt implementiert eine vollständige Industrie-4.0-Überwachungspipeline mit einem vollständigen **OT-Sicherheitsmodul** — Angriffssimulation, regelbasiertem Intrusion Detection System (IDS) und MQTT-Authentifizierung.

---

### OT-Sicherheitsmodul

#### Was ist OT-Sicherheit?

**OT-Sicherheit (Operational Technology)** schützt industrielle Systeme vor Cyberangriffen. Im Gegensatz zur IT-Sicherheit schützt OT-Sicherheit physische Prozesse, bei denen ein erfolgreicher Angriff reale Schäden verursachen kann.

**Warum MQTT standardmäßig unsicher ist:**
- Keine Authentifizierung — jeder im Netzwerk kann sich verbinden
- Keine Autorisierung — jeder Client kann in jedem Topic veröffentlichen
- Keine Verschlüsselung — alle Nachrichten sind im Klartext
- Kein Rate-Limiting — jeder kann den Broker überfluten

---

#### Aufklärung

**Skript:** `Attack Vectors/recon.py`

Verbindet sich anonym mit Mosquitto, abonniert alle Topics (`#`) und zeichnet den gesamten Datenverkehr auf — völlig unsichtbar für den Fabrikbetreiber.

---

#### Angriff 1 — Dateninjektion

**Skript:** `Attack Vectors/attack1.py`

Sendet gefälschte Sensordaten mit unrealistisch niedrigen Temperaturen (15–25°C) und überhöhten Produktionszählern (9000–9999). Das Dashboard zeigt normale Werte — die Maschine könnte tatsächlich überhitzen. Entspricht dem Prinzip des Stuxnet-Angriffs (2010).

---

#### Angriff 2 — Nachrichtenüberflutung (DoS)

**Skript:** `Attack Vectors/attack2.py`

Überflutet alle 4 MQTT-Topics mit 200 Nachrichten/Sekunde (150× normale Rate). 11.534 gefälschte Nachrichten in 60 Sekunden. Das Dashboard wird unzuverlässig.

---

#### Angriff 3 — Identitätsspoofing

**Skript:** `Attack Vectors/attack3.py`

Injiziert eine nicht existierende `machine5` und sendet Nachrichten mit ungültigen machine_id-Varianten. Alle werden dauerhaft in InfluxDB gespeichert und korrumpieren historische Analysen.

---

#### Prävention — MQTT-Authentifizierung

```ini
allow_anonymous false
password_file /mosquitto/config/passwd
```

Angreifer ohne gültige Anmeldedaten werden sofort abgewiesen:
```
Client rogue_attacker_001 disconnected: not authorised
```

---

#### Erkennung — IDS-Engine

**4 Erkennungsregeln in Node-RED:**

| Regel | Erkennt | Schweregrad |
|-------|---------|-------------|
| Unbekannte machine_id | Spoofing (Angriff 3) | HOCH |
| Temperatur außerhalb Bereich | Injektion (Angriff 1) | HOCH/KRITISCH |
| Nachrichtenrate zu hoch | Überflutung (Angriff 2) | KRITISCH |
| Verdächtiger Produktionszähler | Injektion (Angriff 1) | MITTEL |

---

#### Gelernte Lektionen

1. MQTT ist standardmäßig unsicher — Sicherheit muss explizit konfiguriert werden
2. Passive Aufklärung ist nicht nachweisbar
3. Authentifizierung allein reicht nicht — Tiefenverteidigung ist erforderlich
4. OT-Angriffe untergraben das Vertrauen des Bedieners
5. Regelbasierte IDS haben Grenzen — produktionsreife Systeme nutzen ML (Claroty, Dragos, Nozomi)

---

*Built with passion for Industry 4.0 + OT Security*

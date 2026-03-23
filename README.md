# Industry 4.0 Machine Monitoring System
### Industrie 4.0 Maschinenüberwachungssystem

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Node-RED](https://img.shields.io/badge/Node--RED-8F0000?style=flat&logo=node-red&logoColor=white)
![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=flat&logo=influxdb&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-660066?style=flat&logo=mqtt&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

---

> 🇩🇪 Die deutsche Version finden Sie weiter unten.
> 🇬🇧 The German version can be found below.

---

## 🇬🇧 English

A fully containerised Industry 4.0 monitoring system simulating 4 industrial machines with real-time MQTT data, Node-RED processing, InfluxDB storage, and Grafana/Node-RED dashboards.

> 📄 For full project documentation, architecture details and technical explanation, see [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)

---

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — **required**
- [Git](https://git-scm.com/) — **required**

> No Python installation needed — everything runs inside Docker.

---

### Quick Start

#### 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/industry4-monitoring-system.git
cd industry4-monitoring-system
```

#### 2 — Start all services

```bash
docker compose up -d --build
```

First run downloads all images and builds the simulator — allow 2–3 minutes.

#### 3 — Verify containers are running

```bash
docker ps
```

You should see 5 containers: `mosquitto` `nodered` `influxdb` `grafana` `simulator`

#### 4 — Import the Node-RED flow

1. Open `http://localhost:1880`
2. Hamburger menu (☰) → **Import** → select `flows.json` → **Deploy**

#### 5 — Configure InfluxDB in Node-RED

1. Double-click **"Save to InfluxDB"** node → click pencil icon ✏️
2. Set:
   - Version: `2.0`
   - URL: `http://influxdb:8086`
   - Token: `my-secret-token`
   - Organisation: `factory`
3. Click **Update** → **Done** → **Deploy**

#### 6 — Import the Grafana dashboard

1. Open `http://localhost:3000` → login: `admin` / `admin1234`
2. **Dashboards** → **Import** → upload `grafana/grafana-dashboard.json`
3. Map datasource to InfluxDB → **Import**

---

### Access

| Service | URL | Credentials |
|---------|-----|-------------|
| Node-RED Editor | http://localhost:1880 | — |
| Node-RED Dashboard | http://localhost:1880/dashboard | — |
| InfluxDB | http://localhost:8086 | admin / admin1234 |
| Grafana | http://localhost:3000 | admin / admin1234 |

---

### Useful Commands

```bash
# Start everything
docker compose up -d

# Stop everything
docker compose down

# View simulator logs
docker logs simulator

# Rebuild after code changes
docker compose up -d --build
```

---

### Project Structure

```
industry4-monitoring-system/
├── simulator/
│   ├── machine_simulator.py
│   ├── Dockerfile
│   └── requirements.txt
├── grafana/
│   └── grafana-dashboard.json
├── docker-compose.yml
├── flows.json
├── PROJECT_DOCUMENTATION.md
└── README.md
```

---
---

## 🇩🇪 Deutsch

Ein vollständig containerisiertes Industrie-4.0-Überwachungssystem mit 4 simulierten Maschinen, MQTT-Datenübertragung, Node-RED-Verarbeitung, InfluxDB-Speicherung und Grafana/Node-RED-Dashboards.

> 📄 Vollständige Projektdokumentation und technische Details: [PROJECT_DOCUMENTATION.md](./PROJECT_DOCUMENTATION.md)

---

### Voraussetzungen

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — **erforderlich**
- [Git](https://git-scm.com/) — **erforderlich**

> Keine Python-Installation erforderlich — alles läuft in Docker.

---

### Schnellstart

#### 1 — Repository klonen

```bash
git clone https://github.com/YOUR_USERNAME/industry4-monitoring-system.git
cd industry4-monitoring-system
```

#### 2 — Alle Dienste starten

```bash
docker compose up -d --build
```

Beim ersten Start werden alle Images heruntergeladen — ca. 2–3 Minuten einplanen.

#### 3 — Container überprüfen

```bash
docker ps
```

Es sollten 5 Container angezeigt werden: `mosquitto` `nodered` `influxdb` `grafana` `simulator`

#### 4 — Node-RED Flow importieren

1. `http://localhost:1880` öffnen
2. Hamburger-Menü (☰) → **Importieren** → `flows.json` auswählen → **Bereitstellen**

#### 5 — InfluxDB in Node-RED konfigurieren

1. **„Save to InfluxDB"**-Node doppelklicken → Bleistift-Symbol ✏️ klicken
2. Einstellungen:
   - Version: `2.0`
   - URL: `http://influxdb:8086`
   - Token: `my-secret-token`
   - Organisation: `factory`
3. **Aktualisieren** → **Fertig** → **Bereitstellen**

#### 6 — Grafana-Dashboard importieren

1. `http://localhost:3000` öffnen → Anmeldung: `admin` / `admin1234`
2. **Dashboards** → **Importieren** → `grafana/grafana-dashboard.json` hochladen
3. Datenquelle auf InfluxDB setzen → **Importieren**

---

### Zugriff

| Dienst | URL | Anmeldedaten |
|--------|-----|-------------|
| Node-RED Editor | http://localhost:1880 | — |
| Node-RED Dashboard | http://localhost:1880/dashboard | — |
| InfluxDB | http://localhost:8086 | admin / admin1234 |
| Grafana | http://localhost:3000 | admin / admin1234 |

---

### Nützliche Befehle

```bash
# Alles starten
docker compose up -d

# Alles stoppen
docker compose down

# Simulator-Logs anzeigen
docker logs simulator

# Nach Code-Änderungen neu bauen
docker compose up -d --build
```

---

*Built with ❤️ as an Industry 4.0*

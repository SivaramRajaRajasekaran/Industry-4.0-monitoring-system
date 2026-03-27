import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Before attacking, an attacker silently observes the system.
# This script connects to the broker and subscribes to ALL topics.
# It records everything it sees — message format, timing, machine IDs,
# topic structure — without sending anything.
# This is completely passive — no logs on the broker show anything suspicious.

BROKER = "localhost"
PORT = 1883

# Statistics we collect during recon
stats = {
    "topics_discovered": set(),
    "machine_ids": set(),
    "message_count": 0,
    "first_message_time": None,
    "last_message_time": None,
    "sample_payload": None,
    "min_temp": float('inf'),
    "max_temp": float('-inf'),
    "status_values": set()
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("=" * 60)
        print("RECONNAISSANCE — MQTT LISTENER")
        print("=" * 60)
        print(f"Connected to broker at {BROKER}:{PORT}")
        print("Subscribing to ALL topics using wildcard #")
        print("Listening silently... press Ctrl+C to see summary")
        print("=" * 60)
        print()
        # '#' wildcard:
        # In MQTT, # means "match everything at this level and below"
        # factory/# matches factory/machine1/data, factory/machine2/data etc.
        # Just # matches EVERY topic on the entire broker
        # An attacker uses this to discover what topics exist
        client.subscribe("#")
    else:
        print(f"Connection failed with code {rc}")

def on_message(client, userdata, msg):
    now = datetime.now()
    stats["message_count"] += 1

    # Record timing
    if stats["first_message_time"] is None:
        stats["first_message_time"] = now
    stats["last_message_time"] = now

    # Record topic
    stats["topics_discovered"].add(msg.topic)

    # Try to parse payload
    try:
        payload = json.loads(msg.payload.decode())
        stats["sample_payload"] = payload

        # Extract intelligence from the message
        if "machine_id" in payload:
            stats["machine_ids"].add(payload["machine_id"])

        if "temperature" in payload:
            temp = payload["temperature"]
            if temp < stats["min_temp"]:
                stats["min_temp"] = temp
            if temp > stats["max_temp"]:
                stats["max_temp"] = temp

        if "status" in payload:
            stats["status_values"].add(payload["status"])

        # Print each message we intercept
        print(f"[{now.strftime('%H:%M:%S')}] "
              f"Topic: {msg.topic} | "
              f"machine_id: {payload.get('machine_id', '?')} | "
              f"status: {payload.get('status', '?')} | "
              f"temp: {payload.get('temperature', '?')}°C | "
              f"count: {payload.get('production_count', '?')}")

    except Exception as e:
        # Non-JSON message — still record it
        print(f"[{now.strftime('%H:%M:%S')}] "
              f"Topic: {msg.topic} | "
              f"Raw payload: {msg.payload.decode()[:50]}")

def on_disconnect(client, userdata, rc):
    # Print intelligence summary when attacker stops listening
    print()
    print("=" * 60)
    print("RECONNAISSANCE SUMMARY — INTELLIGENCE GATHERED")
    print("=" * 60)
    print(f"Total messages intercepted : {stats['message_count']}")
    print(f"Topics discovered          : {stats['topics_discovered']}")
    print(f"Machine IDs found          : {stats['machine_ids']}")
    print(f"Status values observed     : {stats['status_values']}")

    if stats["min_temp"] != float('inf'):
        print(f"Temperature range observed : "
              f"{stats['min_temp']}°C — {stats['max_temp']}°C")

    if (stats["first_message_time"] and
            stats["last_message_time"] and
            stats["message_count"] > 1):
        # Calculate approximate message interval
        total_seconds = (stats["last_message_time"] -
                        stats["first_message_time"]).total_seconds()
        avg_interval = total_seconds / (stats["message_count"] - 1)
        print(f"Approx message interval    : {avg_interval:.1f} seconds")
        print(f"Messages per minute        : "
              f"{60 / avg_interval:.1f}")

    if stats["sample_payload"]:
        print(f"Message format (sample)    :")
        for key, value in stats["sample_payload"].items():
            print(f"  {key}: {type(value).__name__}")

    print()
    print("ATTACK RECOMMENDATIONS BASED ON RECON:")
    print(f"  → Target topic  : {list(stats['topics_discovered'])[0] if stats['topics_discovered'] else 'unknown'}")
    print(f"  → Use machine_id: {list(stats['machine_ids'])[0] if stats['machine_ids'] else 'unknown'}")
    print(f"  → Match interval: {avg_interval:.0f}s for stealth, 0.1s for flood")
    print(f"  → Fake temp range to hide: below {stats['min_temp']}°C")
    print("=" * 60)

client = mqtt.Client(client_id="passive_listener_recon")
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

client.connect(BROKER, PORT, 60)

try:
    # loop_forever:
    # Keeps the script running and processing incoming messages
    # until the attacker manually stops it with Ctrl+C
    client.loop_forever()
except KeyboardInterrupt:
    print("\nStopping reconnaissance...")
    client.disconnect()
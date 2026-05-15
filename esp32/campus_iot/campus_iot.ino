/**
 * Campus IoT — ESP32
 * Sincroniza relés com o estado das lâmpadas na API (salas configuráveis).
 *
 * Dependência: ArduinoJson (Library Manager) v6.x ou v7.x
 * Copie config.h.example → config.h antes de compilar.
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

struct LampPin {
  int roomId;
  int slot;
  int gpio;
};

// Mapa padrão: salas 1 e 2, três lâmpadas cada
static const LampPin LAMP_PINS[] = {
    {1, 1, ROOM1_SLOT1_PIN},
    {1, 2, ROOM1_SLOT2_PIN},
    {1, 3, ROOM1_SLOT3_PIN},
    {2, 1, ROOM2_SLOT1_PIN},
    {2, 2, ROOM2_SLOT2_PIN},
    {2, 3, ROOM2_SLOT3_PIN},
};
static const size_t LAMP_PINS_COUNT = sizeof(LAMP_PINS) / sizeof(LAMP_PINS[0]);

unsigned long lastPoll = 0;
uint32_t pollIntervalMs = POLL_INTERVAL_MS;
bool wifiOk = false;

int findGpio(int roomId, int slot) {
  for (size_t i = 0; i < LAMP_PINS_COUNT; i++) {
    if (LAMP_PINS[i].roomId == roomId && LAMP_PINS[i].slot == slot) {
      return LAMP_PINS[i].gpio;
    }
  }
  return -1;
}

void setupPins() {
  for (size_t i = 0; i < LAMP_PINS_COUNT; i++) {
    pinMode(LAMP_PINS[i].gpio, OUTPUT);
    digitalWrite(LAMP_PINS[i].gpio, LOW);
  }
}

void connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    wifiOk = true;
    return;
  }
  wifiOk = false;
  Serial.println("[WiFi] Conectando...");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    wifiOk = true;
    Serial.print("[WiFi] OK — IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("[WiFi] Falha — tentando novamente no próximo ciclo");
  }
}

bool fetchAndApplyStates() {
  if (!wifiOk) return false;

  String url = String(API_BASE_URL) + "/api/v1/iot/state?room_ids=" + ROOM_IDS;

  HTTPClient http;
  http.begin(url);
  http.addHeader("X-Device-Key", DEVICE_KEY);
  http.setTimeout(8000);

  int code = http.GET();
  if (code != 200) {
    Serial.printf("[API] Erro HTTP %d em %s\n", code, url.c_str());
    http.end();
    return false;
  }

  String payload = http.getString();
  http.end();

  JsonDocument doc;
  DeserializationError err = deserializeJson(doc, payload);
  if (err) {
    Serial.printf("[JSON] Parse falhou: %s\n", err.c_str());
    return false;
  }

  if (doc["poll_interval_ms"].is<uint32_t>()) {
    pollIntervalMs = doc["poll_interval_ms"].as<uint32_t>();
    if (pollIntervalMs < 500) pollIntervalMs = 500;
  }

  JsonArray lamps = doc["lamps"].as<JsonArray>();
  if (lamps.isNull()) {
    Serial.println("[JSON] Campo 'lamps' ausente");
    return false;
  }

  for (JsonObject lamp : lamps) {
    int roomId = lamp["room_id"] | 0;
    int slot = lamp["slot"] | 0;
    bool isOn = lamp["is_on"] | false;
    int gpio = findGpio(roomId, slot);
    if (gpio < 0) {
      Serial.printf("[GPIO] Sem pino para sala %d slot %d\n", roomId, slot);
      continue;
    }
    digitalWrite(gpio, isOn ? HIGH : LOW);
    Serial.printf("[Lamp] sala=%d slot=%d -> GPIO %d = %s\n", roomId, slot, gpio, isOn ? "ON" : "OFF");
  }

  return true;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== Campus IoT ESP32 ===");
  Serial.printf("Salas monitoradas: %s\n", ROOM_IDS);
  setupPins();
  connectWiFi();
}

void loop() {
  unsigned long now = millis();
  if (WiFi.status() != WL_CONNECTED) {
    wifiOk = false;
    connectWiFi();
  }

  if (now - lastPoll >= pollIntervalMs) {
    lastPoll = now;
    if (wifiOk) {
      fetchAndApplyStates();
    }
  }

  delay(50);
}

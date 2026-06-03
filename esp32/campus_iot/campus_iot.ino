/**
 * Campus IoT — ESP32
 * Sincroniza relés (lâmpadas) e envia IR (ar-condicionado) conforme a API.
 *
 * Dependências (Gerenciador de bibliotecas Arduino):
 *   - ArduinoJson v6.x ou v7.x
 *   - IRremoteESP8266 (opcional; necessário para sinal IR real — veja ENABLE_AC_IR_LIBRARY)
 *
 * Copie config.h.example → config.h antes de compilar.
 */
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

#if defined(ENABLE_AC_IR_LIBRARY) && ENABLE_AC_IR_LIBRARY
#include <IRremoteESP8266.h>
#include <IRac.h>
#ifndef AC_IR_PROTOCOL
#define AC_IR_PROTOCOL decode_type_t::COOLIX
#endif
#endif

struct LampPin {
  int roomId;
  int slot;
  int gpio;
};

struct AcIrPin {
  int roomId;
  int gpio;
};

/** Mapa de relés — lâmpadas (sala + slot). */
static const LampPin LAMP_PINS[] = {
    {1, 1, ROOM1_SLOT1_PIN},
    {1, 2, ROOM1_SLOT2_PIN},
    {1, 3, ROOM1_SLOT3_PIN},
    {2, 1, ROOM2_SLOT1_PIN},
    {2, 2, ROOM2_SLOT2_PIN},
    {2, 3, ROOM2_SLOT3_PIN},
};
static const size_t LAMP_PINS_COUNT = sizeof(LAMP_PINS) / sizeof(LAMP_PINS[0]);

/**
 * GPIO do LED infravermelho (módulo IR) por sala.
 * TESTE: use TEST_IR_ROOM_ID no config.h — uma sala por vez no Serial Monitor.
 */
static const AcIrPin AC_IR_PINS[] = {
    {1, ROOM1_AC_IR_PIN},
    {2, ROOM2_AC_IR_PIN},
};
static const size_t AC_IR_PINS_COUNT = sizeof(AC_IR_PINS) / sizeof(AC_IR_PINS[0]);

struct AcLastState {
  int roomId;
  bool isOn;
  int tempC;
  bool known;
};

static AcLastState acLastStates[8];
static size_t acLastStatesCount = 0;

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

int findAcIrPin(int roomId) {
  for (size_t i = 0; i < AC_IR_PINS_COUNT; i++) {
    if (AC_IR_PINS[i].roomId == roomId) {
      return AC_IR_PINS[i].gpio;
    }
  }
  return -1;
}

AcLastState* getAcLastState(int roomId) {
  for (size_t i = 0; i < acLastStatesCount; i++) {
    if (acLastStates[i].roomId == roomId) {
      return &acLastStates[i];
    }
  }
  if (acLastStatesCount >= sizeof(acLastStates) / sizeof(acLastStates[0])) {
    return nullptr;
  }
  AcLastState* s = &acLastStates[acLastStatesCount++];
  s->roomId = roomId;
  s->isOn = false;
  s->tempC = 23;
  s->known = false;
  return s;
}

/**
 * Envia comando IR ao ar-condicionado da sala.
 *
 * ONDE TESTAR CADA AR:
 *   1. Em config.h defina TEST_IR_ROOM_ID para o ID da sala (ex: 1).
 *   2. Grave o firmware e abra o Monitor Serial (115200).
 *   3. No boot, runAcIrSelfTest() envia ligar 23°C e desligar só para essa sala.
 *   4. Aponte o LED IR ao aparelho; ajuste AC_IR_PROTOCOL no config.h se necessário.
 *   5. Repita para a próxima sala (altere TEST_IR_ROOM_ID).
 */
void sendAcIrCommand(int roomId, bool powerOn, int tempC) {
  int pin = findAcIrPin(roomId);
  if (pin < 0) {
    Serial.printf("[AC-IR] Sala %d: sem pino IR em AC_IR_PINS — configure ROOMx_AC_IR_PIN\n", roomId);
    return;
  }

  Serial.printf("[AC-IR] Sala %d | GPIO %d | %s | %d°C\n", roomId, pin, powerOn ? "LIGAR" : "DESLIGAR", tempC);

#if defined(ENABLE_AC_IR_LIBRARY) && ENABLE_AC_IR_LIBRARY
  IRsend irsend(pin);
  IRac ac(&irsend);
  ac.next.protocol = decode_type_t::kLastDecodeType;
  ac.next.model = AC_IR_PROTOCOL;
  ac.next.mode = stdAc::opmode_t::kCool;
  ac.next.degrees = tempC;
  ac.next.fanspeed = stdAc::fanspeed_t::kAuto;
  ac.next.swingv = stdAc::swingv_t::kOff;
  ac.next.power = powerOn;
  if (!ac.sendAc()) {
    Serial.printf("[AC-IR] Falha ao enviar IR (sala %d). Verifique protocolo/marca.\n", roomId);
  }
#else
  Serial.println("[AC-IR] Modo simulação: defina ENABLE_AC_IR_LIBRARY=1 e instale IRremoteESP8266.");
#endif
}

#if defined(TEST_IR_ROOM_ID)
void runAcIrSelfTest() {
  const int room = TEST_IR_ROOM_ID;
  Serial.println();
  Serial.println("========================================");
  Serial.printf("  TESTE IR — AR-CONDICIONADO SALA %d\n", room);
  Serial.println("  Aponte o LED IR ao aparelho desta sala.");
  Serial.println("  Em 3s: LIGAR 23°C … depois DESLIGAR.");
  Serial.println("========================================");
  delay(3000);
  sendAcIrCommand(room, true, 23);
  delay(4000);
  sendAcIrCommand(room, false, 23);
  Serial.printf("[AC-IR] Teste da sala %d concluído.\n", room);
  Serial.println();
}
#endif

void applyAcState(int roomId, bool isOn, int tempC) {
  AcLastState* last = getAcLastState(roomId);
  if (!last) return;

  if (last->known && last->isOn == isOn && last->tempC == tempC) {
    return;
  }

  sendAcIrCommand(roomId, isOn, tempC);
  last->isOn = isOn;
  last->tempC = tempC;
  last->known = true;
}

void setupPins() {
  for (size_t i = 0; i < LAMP_PINS_COUNT; i++) {
    pinMode(LAMP_PINS[i].gpio, OUTPUT);
    digitalWrite(LAMP_PINS[i].gpio, LOW);
  }
  for (size_t i = 0; i < AC_IR_PINS_COUNT; i++) {
    pinMode(AC_IR_PINS[i].gpio, OUTPUT);
    digitalWrite(AC_IR_PINS[i].gpio, LOW);
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
  if (!lamps.isNull()) {
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
  }

  JsonArray acUnits = doc["air_conditioners"].as<JsonArray>();
  if (!acUnits.isNull()) {
    for (JsonObject ac : acUnits) {
      int roomId = ac["room_id"] | 0;
      bool isOn = ac["is_on"] | false;
      int tempC = ac["target_temp_c"] | 23;
      applyAcState(roomId, isOn, tempC);
    }
  }

  return true;
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println();
  Serial.println("=== Campus IoT ESP32 (lâmpadas + ar IR) ===");
  Serial.printf("Salas monitoradas: %s\n", ROOM_IDS);
  setupPins();
  connectWiFi();

#if defined(TEST_IR_ROOM_ID)
  runAcIrSelfTest();
#endif
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

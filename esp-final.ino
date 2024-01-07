#include <ESP8266WiFi.h>
#include <Adafruit_NeoPixel.h>
#include <WiFiUdp.h>


// Konstante
const char* ssid = "AndroidAP2605";
const char* password = "tilen4321";
#define NEOPIXEL_PIN 5  // Podatkovni pin
#define NUM_LEDS 120
Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_LEDS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
unsigned int localPort = 5555; 

WiFiUDP udp;

void setup() {
  Serial.begin(115200);
  delay(10);

  // Povezava na Wi-Fi
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  udp.begin(localPort);

  strip.begin();
  strip.show();
}

void loop() {

  int packetSize = udp.parsePacket();
  if (packetSize) {
    char packetBuffer[packetSize];
    udp.read(packetBuffer, packetSize);

    // Sprejem
    String message = String(packetBuffer);
    int commaIndex = message.indexOf(',');
    int r = message.substring(0, commaIndex).toInt();
    message = message.substring(commaIndex + 1);
    commaIndex = message.indexOf(',');
    int g = message.substring(0, commaIndex).toInt();
    message = message.substring(commaIndex + 1);
    int b = message.toInt();

    // Prikaz
    for (int i = 0; i < NUM_LEDS; i++) {
      strip.setPixelColor(i, strip.Color(r, g, b));
    }
    strip.show();
  }
}

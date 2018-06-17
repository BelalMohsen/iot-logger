// Released under an MIT license.

#include "DHT.h"
#include <ESP8266WiFi.h>
#include <ESP8266mDNS.h>
#include <stdlib.h>

#define DHTPIN            2         // Pin which is connected to the DHT sensor.

//the type of sensor in use:
#define DHTTYPE           DHT11     // DHT 11 
const int LED_PIN = 5;

DHT dht(DHTPIN, DHTTYPE);
WiFiServer server(80);

const char WiFiSSID[] = "SSID";
const char WiFiPSK[] = "PSK";
float temp = 0;
float humid = 0;
char buff[10];

void setup() {
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  
  // Initialize server.
  connectWiFi();
  server.begin();
  setupMDNS();
  
  // Initialize sensor.
  dht.begin();
  // Set delay between sensor readings based on sensor details.

}

void loop() {
  delay(2000);

  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float humid = dht.readHumidity();
  // Read temperature as Celsius (the default)
  float temp = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humid) || isnan(temp)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }

  // Read the first line of the request
  String req = client.readStringUntil('\r');
  Serial.println(req);
  client.flush();

  // Match the request
  int val = -1; // We'll use 'val' to keep track of both the
                // request type (read/set) and value if set.
  if (req.indexOf("/weather") != -1){
    val = 1;
    Serial.println("getting weather data");
  }
    
  // Set GPIO5 according to the request
  if (val >= 0){
    Serial.println("inside sensor loop");
    digitalWrite(LED_PIN, HIGH);
    // Delay between measurements.
  }
  else {
    digitalWrite(LED_PIN, LOW);
  }

  client.flush();

  // Prepare the response. Start with the common header:
  String s = "HTTP/1.1 200 OK\r\n";
  s += "Content-Type: text/html\r\n\r\n";
  s += "<!DOCTYPE HTML>\r\n<html>\r\n<body>\r\n";
  // If we're setting the LED, print out a message saying we did
  if (val == 1)
  {
    Serial.println("inside page creation");
    s += "<p>";
    s += dtostrf(temp, 4, 6, buff);
    s += ", ";
    s += dtostrf(humid, 4, 6, buff);
    s += "</p>\r\n";
  }
  else
  {
    Serial.println("inside wrong page creation");
    s += "Invalid Request.<br> Try /weather.";
  }
  s += "</body>\r\n</html>\n";

  // Send the response to the client
  client.print(s);
  delay(1);
  Serial.println("Client disonnected");

  // The client will actually be disconnected 
  // when the function returns and 'client' object is detroyed

}

void connectWiFi()
{
  byte ledStatus = LOW;
  Serial.println();
  Serial.println("Connecting to: " + String(WiFiSSID));
  // Set WiFi mode to station (as opposed to AP or AP_STA)
  WiFi.mode(WIFI_STA);

  // WiFI.begin([ssid], [passkey]) initiates a WiFI connection
  // to the stated [ssid], using the [passkey] as a WPA, WPA2,
  // or WEP passphrase.
  WiFi.begin(WiFiSSID, WiFiPSK);

  // Use the WiFi.status() function to check if the ESP8266
  // is connected to a WiFi network.
  while (WiFi.status() != WL_CONNECTED)
  {
    // Blink the LED
    digitalWrite(LED_PIN, ledStatus); // Write LED high/low
    ledStatus = (ledStatus == HIGH) ? LOW : HIGH;

    // Delays allow the ESP8266 to perform critical tasks
    // defined outside of the sketch. These tasks include
    // setting up, and maintaining, a WiFi connection.
    delay(100);
    // Potentially infinite loops are generally dangerous.
    // Add delays -- allowing the processor to perform other
    // tasks -- wherever possible.
  }
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void setupMDNS()
{
  // Call MDNS.begin(<domain>) to set up mDNS to point to
  // "<domain>.local"
  if (!MDNS.begin("thermo")) 
  {
    Serial.println("Error setting up MDNS responder!");
    while(1) { 
      delay(1000);
    }
  }
  MDNS.addService("http", "tcp", 80);
  Serial.println("mDNS responder started");

}



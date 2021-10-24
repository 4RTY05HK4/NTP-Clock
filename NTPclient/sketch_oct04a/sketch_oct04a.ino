#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "NTPserver";
const char* password = "pasz12port";
String receivedData = "";
String httpGETRequest(const char* serverName) {
  WiFiClient client;
  HTTPClient http;
    
  // Your Domain name with URL path or IP address with path
  http.begin(client, serverName);
  
  // Send HTTP POST request
  int httpResponseCode = http.GET();
  
  String payload = "--"; 
  
  if (httpResponseCode>0) {
    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);
    payload = http.getString();
  }
  else {
    Serial.print("Error code: ");
    Serial.println(httpResponseCode);
  }
  
  http.end();

  Serial.println(payload);
  return payload;
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.println("Connecting");
  while(WiFi.status() != WL_CONNECTED) { 
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("Connected with IP:");
  Serial.println(WiFi.localIP());
    if(WiFi.status()== WL_CONNECTED ){ 
      receivedData = httpGETRequest("http://192.168.137.25/?getTimeNDate");

  }
  Serial.println(receivedData);
}

void loop() {

}

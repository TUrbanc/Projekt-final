Naslov naloge: ZVOČNI DETEKTOR NIZKIH TONOV NA LED TRAKU

1. Namen projektne naloge

Razviti zvočni detektor nizkih tonov na LED traku, ki bo zajel sistemski zvok in ga sprocesiral v Pythonu tako, da bo filtriral nizke frekvence ter nato preko Wi-Fi povezave glede na njihovo amplitudo prikazal ustrezne jakosti barve na RGB traku.

2. Zasnova rešitve

Za izvedbo se uporablja Python s knjižnicami PyAudio za procesiranje zvoka in PyQtGraph za prikaz grafa frekvenc in amplitude. Zajem sistema poteka preko virtualnega kabla na računalniku, nato se zvok filtrira, in ustrezne frekvence se prikažejo na RGB traku, povezanem s pomočjo ESP8266.

3. Uporabljena orodja, knjižnice, storitve,..

Uporabljene so knjižnice PyAudio in PyQtGraph za procesiranje in prikaz zvoka. Za zajem sistema se uporablja virtualni kabel na računalniku. Na ESP8266 sem uporabil knjižnici ESP8266WiFi in WiFiUdp za omogočanje povezave preko Wi-Fi-ja ter knjižnico Adafruit_NeoPixel za funkcionalnost RGB traka.

4. Predstavitev rešitve

Prvi korak je bila fizična povezava ESP-ja z RGB trakom in napajalnikom. Glede na to, da izbrani trak deluje na le 5 V napetosti je potreba po toku precej velika, zato sem uporabil kar računalniški napajalnik. Na ESP sem naložil skripto, ki je omogočala prikaz barv na traku. Ta je vsebovala sledečo zanko v kateri sem izbral R, G, B vrednosti barv in pa število led diod na traku, ki so se uspešno prikazale:

    for (int i = 0; i < NUM_LEDS; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b));
        }
        strip.show();

To je bilo prvo zagotovilo, da osnovni hardware deluje kot pričakovano. Nato sem ESP povezal v omrežje, kar mi je omogočilo spreminjanje barv preko Python programa na računalniku. Ključni del te kode je bil sledeč, kjer sem se povezal na Wi-Fi:

    WiFi.begin(ssid, password);

Nato zanka čaka, da je povezava uspešna:

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

Zaženem še UDP strežnik na prej določenem portu (5555):
    
    udp.begin(localPort);

Nato v zanki pregledujem prihajajoče pakete:

    int packetSize = udp.parsePacket();
    if (packetSize) {
        char packetBuffer[packetSize];
        udp.read(packetBuffer, packetSize);

packetBuffer je spremenljivka v kateri se skriva prejeto sporočilo RGB vrednosti tipa string, ki jih nato, pred prikazom s pomočjo prej navedene zanke, še pretvorim v posamične intiger vrednosti.

Na računalinku sem napisal funkcijo za pošiljanje na ESP, katere ključni del je bil ustvarjanje socket objekta za pošiljanje sporočila:

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

kjer socket.AF_INET predstavlja, da bo uporabljen IPv4, socket.SOCK_DGRAM pa UDP protokol. Nato sem željene RGB vrednosti pretvoril v string spremenljivko "message" in jo poslal na določen IP naslov in port:

    sock.sendto(message, (UDP_IP, UDP_PORT))

Ta korak je bil ključen za vzpostavitev povezave in preizkus komunikacije med računalnikom in RGB trakom.

Naslednji izziv je bil zajem in procesiranje zvoka na računalniku. Začel sem s procesiranjem zvoka iz datoteke, kar je služilo kot osnova za nadaljnje razumevanje dela s samim zvokom. Knjižnica PyAudio se je izkazala kot ključni del za zajem zvoka sistema, vendar je bilo potrebno reševati težave, povezane s kompatibilnostjo na novejših različicah Pythona in namestitvijo povezanih knjižnic. Pri tem sem našel eno izmed različic Pythona, ki ima možnost avtomatske namestitve vseh potrebnih knjižnic, imenovano Anaconda. Namestil sem še virtualni kabel, gonilnik za zvok, ki posluša "izhod" sistemskega zvoka in ga interpretera kot zvočni "vhod". Ob enem je zvok, s pomočjo ene izmed nastavitev sistema Windows, mogoče poslušati tudi na drugem zvočnem izhodu. Nato sem s pomočjo "GetAudioIndex" skripte ugotovil na katerem index-u je vhod virtualnega kabla. Zajem zvoka sem v programu dosegel tako, da sem zajel "stream" zvoka, ki sem ga ves čas osveževal:

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=DEVICE_INDEX)

Ko sem to uspešno izvedel, sem se lotil filtriranja zvoka za izločanje nizkih frekvenc. Zadeva je precej kompleksna. Spodnja koda prikazuje ključni del, kjer se pregleduje jakost na željenih frekvenčnih razponih s pomočjo prej podane frekvence vzorčenja in predhodno izračunanega spektra po furieriovi transformaciji:

    spec_20_40 = spectrum[int(20 / RATE * len(spectrum)):int(40 / RATE * len(spectrum))]
    spec_40_60 = spectrum[int(40 / RATE * len(spectrum)):int(60 / RATE * len(spectrum))]
    spec_60_80 = spectrum[int(60 / RATE * len(spectrum)):int(80 / RATE * len(spectrum))]

To je omogočilo koncentracijo na želene frekvence. Maksimume teh vrednosti nato preverjam z želenimi amplitudami in na trak pošljem izbrane vrednosti:

    if np.max(spec_20_40) > 3000000:
            print("20 - 40 Hz")
            rgb_values = [0, 0, 255]

        elif np.max(spec_40_60) > 3000000:
            print("40 - 60 Hz")
            rgb_values = [0, 0, 130]

        elif np.max(spec_60_80) > 3000000:
            print("60 - 80 Hz")
            rgb_values = [0, 0, 30]

        else:
            print("other")
            rgb_values = [0, 0, 0]
            
        send_rgb_to_esp(rgb_values)

Občutljivost frekvenčnih razponov lahko določim z izbiro vrednosti za primerjanje, te so namreč amplitude na grafu pri določenih frekvencah.
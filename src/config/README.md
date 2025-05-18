
## config.json

- `connection` enthält Konfigurationsparameter für den Verbindungsaufbau per WiFi
	- `ssid` von dem host network
	- `password`
- `input` enthält Konfigurationsparameter für die Eingabe am controller
	- `lib` welche pypi-library für den seriellen Empfang vom Controller genutzt wird. In Zukunft sollte hier auch eine Option für eine library, die die Möglichkeit bietet, generische HID-Geräte auszulesen implementiert werden
- `communication` enthält Konfigurationsparameter für die übertragungscodierung
	- `map` eine schlüssel <-> wert Bibliothek für die Eingabemöglichkeiten, übersetzt in die Funktion
		- wert `acc` -> Beschleunigung (wert normiert zwischen 0 und 1)
		- wert `dcc` -> Abbremsen (wert normiert zwischen 0 und 1)
		- wert `str` -> Lenken (wert normiert zwischen -1 und 1)
		- wert `off` -> Aus (komplette Trennung vom Strom)
		- wert `ems` -> Nothalt (bei Drohnen z. B.  return-to-home Modus)
		- wert `eff` -> Notaus (komplette Trennung vom Strom)

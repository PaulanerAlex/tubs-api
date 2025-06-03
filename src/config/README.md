
## conf.json

Wird benötigt um das Programm auszuführen. Inhalt:

- `vehicle` enthält Konfigurationsparameter über das Fahrzeug
	- `type` Ob Auto, Drohne etc.
	- `name` für interne Konfigurationsparameter, z. B. den Prefix der Kommunikationstopics
- `program` enthält Konfigurationsparameter des Programms
	- `debug` bool, ob der debugging modus aktiviert werden soll
	- `headless` bool, ob der headless modus (ohne Display) aktiviert werden soll. Für das Fahrzeug sollte der Wert immer `False` sein
- `connection` enthält Konfigurationsparameter für den Verbindungsaufbau per WiFi
	- `type` aktuell nur wifi unterstützt
	- `ssid` von dem host network
	- `password`
	- `interface` das Interface mit dem nach Netzwerken gesucht wird. Wenn der Wert `auto` ist, wird versucht mittels ip link das interface herauszusuchen
- `input` enthält Konfigurationsparameter für die Eingabe am controller
	- `lib` welche pypi-library für den seriellen Empfang vom Controller genutzt wird. In Zukunft sollte hier auch eine Option für eine library, die die Möglichkeit bietet, generische HID-Geräte auszulesen implementiert werden
- `communication` enthält Konfigurationsparameter für die Übertragungscodierung
	- `encoding` eine Schlüssel <-> Wert Bibliothek für die Eingabemöglichkeiten, übersetzt in die Funktion
		- wert `acc` -> Beschleunigung (wert normiert zwischen 0 und 1)
		- wert `dcc` -> Abbremsen (wert normiert zwischen 0 und 1)
		- wert `str` -> Lenken (wert normiert zwischen -1 und 1)
		- wert `off` -> Aus (komplette Trennung vom Strom)
		- wert `ems` -> Nothalt (bei Drohnen z. B.  return-to-home Modus)
		- wert `eff` -> Notaus (komplette Trennung vom Strom)
	- `encoding_norm` maximaler Wert, mit dem die werte der `encoding` map mittels schlüssel evtl. normalisiert werden können, für start bei 0
- `gui` enthält Konfigurationsparameter für die Grafische Benutzeroberfläche
	- `encoding` eine Schlüssel <-> Wert Bibliothek für die Eingabemöglichkeiten, übersetzt in die Funktion, so wie in `communication/encoding`
		- wert `gui_menu` Menü öffnen
		- wert `gui_select` Auswählen
		- wert `gui_du` / `gui_ud` Oben, unten. Welcher Knopf oben und welcher unten ist, hängt vom Gerät ab, daher gibt es zwei Auswahlmöglichkeiten. Wenn die Tasten vertauscht sind, einfach anderen Wert nehmen.
		- wert `gui_rl` / `gui_lr` Rechts, links.  Welcher Knopf oben und welcher unten ist, hängt vom Gerät ab, daher gibt es zwei Auswahlmöglichkeiten. Wenn die Tasten vertauscht sind, einfach anderen Wert nehmen.

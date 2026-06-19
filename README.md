# Basen Green BMS — Home Assistant Integration

Custom integration για μπαταρίες **Basen Green** με Tianpower BMS (`TP_*`) μέσω **Bluetooth**.

Ξεχωριστός αισθητήρας για **κάθε κελί** (1–16), θερμοκρασίες, SOC, ρεύμα, ισχύς και διαγνωστικά.

## Υποστηριζόμενες συσκευές

- Basen Green 30kWh (BR-PC-LV, 51.2V / 300Ah)
- Όλες οι μπαταρίες με Bluetooth όνομα `TP_*` (Tianpower BMS)
- Παράδειγμα: `TP_BSTBD-25C-2`

## Απαιτήσεις

- Home Assistant **2024.1+**
- Bluetooth (built-in Raspberry Pi ή USB adapter)
- Κλείστε την εφαρμογή **BasenGreen** στο κινητό κατά τη σύνδεση

## Εγκατάσταση

### Μέθοδος 1 — HACS (προτείνεται)

1. **HACS** → **Integrations** → **⋮** (πάνω δεξιά) → **Custom repositories**
2. Προσθέστε: `https://github.com/papazachariakis/BASENGREEN`
3. Category: **Integration** → **Add**
4. **HACS** → **Integrations** → αναζήτηση **Basen Green BMS** → **Download**
5. **Restart** Home Assistant
6. **Ρυθμίσεις** → **Συσκευές & υπηρεσίες** → **Προσθήκη ενσωμάτωσης** → **Basen Green BMS**

### Μέθοδος 2 — Χειροκίνητη εγκατάσταση

1. Αντιγράψτε τον φάκελο `custom_components/basengreen` στο config directory του HA:

   ```
   /config/custom_components/basengreen/
   ```

   **Windows (Samba):** `\\192.168.x.x\config\custom_components\basengreen\`

2. **Restart** Home Assistant

3. **Ρυθμίσεις** → **Συσκευές & υπηρεσίες** → **Προσθήκη ενσωμάτωσης** → **Basen Green BMS**

### Μέθοδος 3 — PowerShell script (Windows)

```powershell
cd "C:\Users\papaz\Documents\Claude\Projects\BASENGREEN"
.\install.ps1 -HaConfigPath "\\192.168.99.100\config"
```

Μετά κάντε restart το Home Assistant.

## Ρύθμιση

1. Διαγράψτε το **BLE Battery Management** (BMS BLE) αν το έχετε — δεν μπορούν και τα δύο να συνδεθούν ταυτόχρονα
2. Κλείστε την app BasenGreen
3. Προσθέστε **Basen Green BMS** και επιλέξτε `TP_BSTBD-25C-2`
4. Περιμένετε 1–2 λεπτά για πρώτη ενημέρωση sensors

## Sensors

| Sensor | Περιγραφή |
|--------|-----------|
| SOC | State of charge (%) |
| Συνολική τάση | Τάση πακέτου (V) |
| Ρεύμα / Ισχύς | Φόρτιση (+) / εκφόρτιση (-) |
| SOH | State of health (%) |
| **Τάση κελιού 1–16** | Ξεχωριστός sensor ανά κελί |
| Θερμοκρασία αισθητήρα 1–8 | Θερμοκρασίες BMS |
| Min/max/delta τάση | Διάγνωση ισορροπίας κελιών |
| RSSI / Ποιότητα σύνδεσης | Διάγνωση Bluetooth |

## Αντιμετώπιση προβλημάτων

| Πρόβλημα | Λύση |
|----------|------|
| `Failed to connect` / connection slots | Power cycle Pi, κλείστε άλλα BLE integrations |
| RSSI -80 ή χειρότερο | USB Bluetooth adapter ή ESP32 Bluetooth proxy |
| Sensors `unavailable` | Κλείστε BasenGreen app, reload Bluetooth |
| Δεν εμφανίζεται η συσκευή | Advertisement Monitor → βεβαιωθείτε ότι broadcast-άρει `TP_*` |

## Άδεια

Apache 2.0 — χρησιμοποιεί τη βιβλιοθήκη [aiobmsble](https://github.com/patman15/aiobmsble).

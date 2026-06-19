# Lovelace Dashboard — Basen Green

## Γρήορη εγκατάσταση

1. **Επεξεργασία πίνακα** (Edit Dashboard) → **Προσθήκη κάρτας**
2. **Manual** (χειροκίνητη)
3. Αντιγραφή περιεχομένου από `basengreen-dashboard.yaml`
4. **Αποθήκευση**

## Αρχεία

| Αρχείο | Περιγραφή |
|--------|-----------|
| `basengreen-dashboard.yaml` | Πλήρης κάρτα με όλους τους sensors (built-in cards) |
| `basengreen-auto.yaml` | Αυτόματη ανίχνευση entities (χρειάζεται Auto-Entities από HACS) |

## Διόρθωση entity_id

Αν κάποια entities εμφανίζονται κόκκινα:

1. **Ρυθμίσεις → Συσκευές → TP_BSTBD-25C-2**
2. Δες τα entity_id (π.χ. `sensor.tp_bstbd_25c_2_state_of_charge`)
3. Αντικατάστησε στο YAML το prefix `tp_bstbd_25c_2` αν διαφέρει

## Τι περιλαμβάνει η κάρτα

- SOC, τάση, ρεύμα, ισχύς, θερμοκρασία
- Gauges SOC / SOH
- Φόρτιση / εκφόρτιση / balancing
- **16 gauges** τάσης κελιών (πλέγμα 4×4)
- Λίστα κελιών + min/max/delta
- Γράφημα 24h τάσεων κελιών
- Χωρητικότητα, κύκλοι, θερμοκρασίες
- Διάγνωση BMS + RSSI

# Lovelace Dashboard — Basen Green

## Ποια κάρτα να διαλέξεις

| Αρχείο | Εμφάνιση | HACS απαιτείται |
|--------|----------|-----------------|
| **`basengreen-dashboard-beautiful.yaml`** ⭐ | Premium — Mushroom + BMS Cells Card | Ναι |
| `basengreen-dashboard.yaml` | Βασική — built-in HA cards | Όχι |
| `basengreen-auto.yaml` | Αυτόματη ανίχνευση entities | Auto-Entities |

---

## Premium Dashboard (προτείνεται)

### 1. Εγκατάσταση HACS cards (Frontend)

| Card | HACS αναζήτηση |
|------|----------------|
| **Mushroom Cards** | `Mushroom` |
| **BMS Battery Cells Card** | `BMS Battery Cells` |
| **stack-in-card** | `stack-in-card` |
| **mini-graph-card** | `mini-graph-card` |

### 2. Προσθήκη στον πίνακα

1. **Επεξεργασία πίνακα** → **+ Προσθήκη κάρτας** → **Manual**
2. Αντιγραφή από: [basengreen-dashboard-beautiful.yaml](https://raw.githubusercontent.com/papazachariakis/BASENGREEN/main/lovelace/basengreen-dashboard-beautiful.yaml)
3. **Αποθήκευση**

### 3. Τι θα δεις

- **Hero card** με SOC, τάση, ισχύ — χρώμα ανά επίπεδο μπαταρίας
- **Chips** φόρτιση / εκφόρτιση / balancing / θερμοκρασία / RSSI
- **BMS Battery Cells Card** — οπτικό γράφημα 16 κελιών με χρώματα
- **Mini graphs** SOC & ισχύς 24h
- Ομαδοποιημένες ενότητες χωρητικότητας, θερμοκρασιών, διάγνωσης

---

## Διόρθωση entity_id

Αν entities εμφανίζονται κόκκινα:

**Ρυθμίσεις → Συσκευές → TP_BSTBD-25C-2 → Entities**

Αντικατάστησε `tp_bstbd_25c_2` στο YAML αν διαφέρει.

---

## Raw links

- [Premium](https://raw.githubusercontent.com/papazachariakis/BASENGREEN/main/lovelace/basengreen-dashboard-beautiful.yaml)
- [Basic](https://raw.githubusercontent.com/papazachariakis/BASENGREEN/main/lovelace/basengreen-dashboard.yaml)
- [Auto](https://raw.githubusercontent.com/papazachariakis/BASENGREEN/main/lovelace/basengreen-auto.yaml)

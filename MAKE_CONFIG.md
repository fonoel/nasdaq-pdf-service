# 🔧 Configuration Make.com - Guide Détaillé

## 📍 Position du module HTTP dans votre workflow

Votre workflow actuel:
```
[Modules 1-3] → [OpenAI Module 4] → [Module 82 VIX] → [Module 5 HTML] → [Email]
```

Nouveau workflow:
```
[Modules 1-3] → [OpenAI Module 4] → [Module 82 VIX] → [🆕 HTTP PDF Generator] → [Email avec PDF]
```

---

## ➕ Ajout du module HTTP

### 1. Ajouter le module après le module 82

1. Dans Make.com, cliquez sur le **+** après le module 82
2. Recherchez **"HTTP"**
3. Sélectionnez **"Make a request"**

### 2. Configuration complète du module HTTP

#### ⚙️ Paramètres généraux

| Paramètre | Valeur |
|-----------|--------|
| **URL** | `https://votre-service.up.railway.app/generate-pdf` |
| **Method** | `POST` |
| **Request timeout** | `30` (secondes) |

#### 📋 Headers

Cliquez sur "Add item" et ajoutez:

| Name | Value |
|------|-------|
| `Content-Type` | `application/json` |

#### 📦 Body

**Body type:** Sélectionnez **"Raw"**

**Content type:** Sélectionnez **"JSON (application/json)"**

**Request content:** Copiez-collez exactement ceci:

```json
{
  "report_date": "{{4.report_date}}",
  "report_title": "{{4.report_title}}",
  "macro_dashboard": {
    "vix": {
      "level": "{{4.macro_dashboard.vix.level}}",
      "change": "{{4.macro_dashboard.vix.change}}",
      "change_pct": "{{4.macro_dashboard.vix.change_pct}}",
      "regime": "{{4.macro_dashboard.vix.regime}}",
      "interpretation": "{{4.macro_dashboard.vix.interpretation}}",
      "z_score_20d": "{{4.macro_dashboard.vix.z_score_20d}}",
      "percentile_252d": "{{4.macro_dashboard.vix.percentile_252d}}",
      "sd_from_20d_ma": "{{4.macro_dashboard.vix.sd_from_20d_ma}}",
      "implied_minus_realized": "{{4.macro_dashboard.vix.implied_minus_realized}}"
    },
    "📈 VIX TERM STRUCTURE": {
      "front_month": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.front_month}}",
      "2nd_month": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.2nd_month}}",
      "6_month": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.6_month}}",
      "12_month": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.12_month}}",
      "slope_short_term": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.slope_short_term}}",
      "slope_medium_term": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.slope_medium_term}}",
      "term_structure_shape": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.term_structure_shape}}",
      "interpretation": "{{4.macro_dashboard.📈 VIX TERM STRUCTURE.interpretation}}"
    },
    "ust10y": {
      "level": "{{4.macro_dashboard.ust10y.level}}",
      "change_bps": "{{4.macro_dashboard.ust10y.change_bps}}",
      "stance": "{{4.macro_dashboard.ust10y.stance}}",
      "valuation_pressure": "{{4.macro_dashboard.ust10y.valuation_pressure}}",
      "interpretation": "{{4.macro_dashboard.ust10y.interpretation}}"
    },
    "dxy": {
      "level": "{{4.macro_dashboard.dxy.level}}",
      "change": "{{4.macro_dashboard.dxy.change}}",
      "change_pct": "{{4.macro_dashboard.dxy.change_pct}}",
      "trend": "{{4.macro_dashboard.dxy.trend}}",
      "fx_impact": "{{4.macro_dashboard.dxy.fx_impact}}",
      "interpretation": "{{4.macro_dashboard.dxy.interpretation}}"
    },
    "fed_funds": {
      "rate": "{{4.macro_dashboard.fed_funds.rate}}",
      "date": "{{4.macro_dashboard.fed_funds.date}}",
      "next_meeting": "{{4.macro_dashboard.fed_funds.next_meeting}}",
      "hold_probability": "{{4.macro_dashboard.fed_funds.hold_probability}}",
      "cut_probability": "{{4.macro_dashboard.fed_funds.cut_probability}}",
      "interpretation": "{{4.macro_dashboard.fed_funds.interpretation}}"
    },
    "regime_summary": "{{4.macro_dashboard.regime_summary}}"
  },
  "Executive summary": {
    "Headline": "{{4.Executive summary.Headline}}",
    "Market regime": "{{4.Executive summary.Market regime}}",
    "Sentiment": "{{4.Executive summary.Sentiment}}",
    "Confidence score": "{{4.Executive summary.Confidence score}}",
    "Key insight": "{{4.Executive summary.Key insight}}",
    "Trading thesis": "{{4.Executive summary.Trading thesis}}"
  },
  "Market statistics": {
    "Advancers": "{{4.Market statistics.Advancers}}",
    "Decliners": "{{4.Market statistics.Decliners}}",
    "ad_ratio": "{{4.Market statistics.ad_ratio}}",
    "Avg performance": "{{4.Market statistics.Avg performance}}",
    "Median performance": "{{4.Market statistics.Median performance}}",
    "dispersion": "{{4.Market statistics.dispersion}}"
  },
  "breadth_nasdaq_10": {
    "total_stocks": "{{4.breadth_nasdaq_10.total_stocks}}",
    "advancers": "{{4.breadth_nasdaq_10.advancers}}",
    "decliners": "{{4.breadth_nasdaq_10.decliners}}",
    "unchanged": "{{4.breadth_nasdaq_10.unchanged}}",
    "ad_ratio": "{{4.breadth_nasdaq_10.ad_ratio}}",
    "avg_performance": "{{4.breadth_nasdaq_10.avg_performance}}",
    "median_performance": "{{4.breadth_nasdaq_10.median_performance}}",
    "breadth_quality": "{{4.breadth_nasdaq_10.breadth_quality}}",
    "top_5_gainers": {
      "1": {
        "symbol": "{{4.breadth_nasdaq_10.top_5_gainers.1.symbol}}",
        "performance": "{{4.breadth_nasdaq_10.top_5_gainers.1.performance}}"
      }
    },
    "top_5_losers": {
      "1": {
        "symbol": "{{4.breadth_nasdaq_10.top_5_losers.1.symbol}}",
        "performance": "{{4.breadth_nasdaq_10.top_5_losers.1.performance}}"
      }
    },
    "breadth_analysis": "{{4.breadth_nasdaq_10.breadth_analysis}}"
  },
  "Top movers": {
    "1": {
      "symbol": "{{4.Top movers.1.symbol}}",
      "price": "{{4.Top movers.1.price}}",
      "change_pct": "{{4.Top movers.1.change_pct}}",
      "z_score": "{{4.Top movers.1.z_score}}",
      "intraday_range_pct": "{{4.Top movers.1.intraday_range_pct}}",
      "volume_vs_avg": "{{4.Top movers.1.volume_vs_avg}}",
      "support_level": "{{4.Top movers.1.support_level}}",
      "resistance_level": "{{4.Top movers.1.resistance_level}}",
      "momentum": "{{4.Top movers.1.momentum}}",
      "risk_level": "{{4.Top movers.1.risk_level}}",
      "reason": "{{4.Top movers.1.reason}}",
      "analysis": "{{4.Top movers.1.analysis}}"
    }
  },
  "Stocks": {
    "1": {
      "symbol": "{{4.Stocks.1.symbol}}",
      "price": "{{4.Stocks.1.price}}",
      "change_pct": "{{4.Stocks.1.change_pct}}",
      "z_score": "{{4.Stocks.1.z_score}}",
      "intraday_range_pct": "{{4.Stocks.1.intraday_range_pct}}",
      "support": "{{4.Stocks.1.support}}",
      "resistance": "{{4.Stocks.1.resistance}}",
      "change_color": "{{4.Stocks.1.change_color}}",
      "analysis": "{{4.Stocks.1.analysis}}"
    }
  },
  "Sector performance": {
    "Technology": {
      "Avg performance": "{{4.Sector performance.Technology.Avg performance}}",
      "z_score": "{{4.Sector performance.Technology.z_score}}",
      "correlation": "{{4.Sector performance.Technology.correlation}}",
      "Best performer": "{{4.Sector performance.Technology.Best performer}}",
      "Worst performer": "{{4.Sector performance.Technology.Worst performer}}",
      "Comment": "{{4.Sector performance.Technology.Comment}}"
    }
  },
  "Forecast 5days": {
    "Direction": "{{4.Forecast 5days.Direction}}",
    "Expected return pct": "{{4.Forecast 5days.Expected return pct}}",
    "Probability": "{{4.Forecast 5days.Probability}}",
    "sharpe_estimate": "{{4.Forecast 5days.sharpe_estimate}}",
    "max_drawdown_risk": "{{4.Forecast 5days.max_drawdown_risk}}",
    "bull_case": "{{4.Forecast 5days.bull_case}}",
    "base_case": "{{4.Forecast 5days.base_case}}",
    "bear_case": "{{4.Forecast 5days.bear_case}}",
    "key_catalysts": {
      "1": "{{4.Forecast 5days.key_catalysts.1}}",
      "2": "{{4.Forecast 5days.key_catalysts.2}}",
      "3": "{{4.Forecast 5days.key_catalysts.3}}"
    }
  },
  "Action items": {
    "1": "{{4.Action items.1}}",
    "2": "{{4.Action items.2}}",
    "3": "{{4.Action items.3}}"
  },
  "vix_term_structure_html": "{{82.choices[].message.content}}"
}
```

#### ✅ Parse response

- **Parse response:** `Yes`

#### 🔍 Advanced settings

- **Follow redirect:** `Yes`
- **Reject certificates:** `No`
- **Use Mutual TLS:** `No`

---

## 📧 Modification du module Email

### Supprimer l'ancien système

1. Supprimez ou désactivez le **module 5** (HTML_report) s'il n'est plus utilisé
2. Dans votre module Email, supprimez les anciennes configurations HTML

### Configurer les pièces jointes

Dans le module Email, section **Attachments**:

1. Cliquez sur **"Add item"**
2. Configurez:

| Paramètre | Valeur |
|-----------|--------|
| **File name** | `Nasdaq_Daily_Report_{{formatDate(now; "YYYY-MM-DD")}}.pdf` |
| **Data** | `{{[NUMERO_MODULE_HTTP].data}}` |
| **MIME type** | `application/pdf` |

⚠️ **Important:** Remplacez `[NUMERO_MODULE_HTTP]` par le numéro réel du module HTTP que vous avez ajouté (probablement 83 si le module 82 est VIX).

---

## ✅ Checklist finale

- [ ] Module HTTP ajouté après le module 82
- [ ] URL Railway correcte dans le module HTTP
- [ ] Header `Content-Type: application/json` configuré
- [ ] Body JSON copié-collé avec toutes les variables
- [ ] Parse response activé
- [ ] Module Email modifié pour utiliser le PDF
- [ ] Workflow testé avec succès
- [ ] PDF reçu par email et bien formaté

---

## 🎯 Résultat attendu

Après configuration, vous devriez recevoir un email avec:
- ✅ Un PDF professionnel en pièce jointe
- ✅ Toutes les sections présentes et bien formatées
- ✅ Aucune coupure de page disgracieuse
- ✅ Headers et footers sur chaque page
- ✅ Numérotation des pages

---

## 🐛 Troubleshooting

### Le module HTTP échoue

1. **Vérifiez l'URL:** Elle doit être exactement `https://votre-url.railway.app/generate-pdf`
2. **Vérifiez que Railway est déployé:** Allez sur Railway et vérifiez le statut
3. **Testez l'URL manuellement:**
   ```bash
   curl https://votre-url.railway.app/health
   ```

### Le PDF n'est pas attaché à l'email

1. Vérifiez le numéro du module HTTP dans la configuration de l'email
2. Vérifiez que "Parse response" est activé dans le module HTTP
3. Inspectez l'output du module HTTP pour voir si des données sont retournées

### Des données manquent dans le PDF

1. Vérifiez que toutes les variables du module 4 sont bien présentes
2. Comparez le JSON du module 4 avec la structure dans la configuration HTTP
3. Consultez les logs Railway pour voir les erreurs

---

## 📞 Support Make.com

Si vous rencontrez des difficultés avec Make.com:

1. Utilisez l'inspecteur d'exécution (icône loupe)
2. Vérifiez chaque étape du workflow
3. Consultez les logs de chaque module

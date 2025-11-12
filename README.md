# 📊 Nasdaq Daily Report - Service PDF Automatisé

Service API Flask pour générer automatiquement des PDF professionnels à partir de vos données Make.com.

## 🎯 Vue d'ensemble

Ce service reçoit les données JSON de votre workflow Make.com et retourne un PDF professionnel du Nasdaq Daily Report, parfaitement formaté sans coupures de page.

**Architecture:**
```
Make.com → Collecte données → OpenAI (module 4) → 
→ VIX HTML (module 82) → HTTP POST vers ce service → PDF retourné → Email
```

---

## 📦 Déploiement sur Railway (GRATUIT)

### Étape 1 : Créer un compte Railway

1. Allez sur [Railway.app](https://railway.app)
2. Cliquez sur "Start a New Project"
3. Connectez-vous avec GitHub (recommandé)

### Étape 2 : Créer un nouveau projet

1. Créez un **nouveau repository GitHub** pour ce service
2. Uploadez tous les fichiers de ce dossier dans le repository:
   - `app.py`
   - `requirements.txt`
   - `Procfile`
   - `runtime.txt`
   - `README.md`

### Étape 3 : Déployer sur Railway

1. Dans Railway, cliquez sur "New Project"
2. Sélectionnez "Deploy from GitHub repo"
3. Choisissez votre repository
4. Railway détectera automatiquement la configuration Python
5. Le déploiement prend 2-3 minutes

### Étape 4 : Obtenir l'URL publique

1. Une fois déployé, cliquez sur votre service
2. Allez dans "Settings"
3. Activez "Public Networking"
4. Copiez l'URL (ex: `https://votre-service.up.railway.app`)

🎉 **Votre API est maintenant en ligne !**

---

## 🔧 Configuration Make.com

### Étape 1 : Ajouter un module HTTP

Après votre **module 82** (VIX Term Structure), ajoutez un **nouveau module HTTP**:

1. Recherchez "HTTP" dans les modules Make.com
2. Sélectionnez **"Make a request"**

### Étape 2 : Configuration du module HTTP

**URL:**
```
https://votre-service.up.railway.app/generate-pdf
```

**Method:**
```
POST
```

**Headers:**
```
Content-Type: application/json
```

**Body Type:**
```
Raw
```

**Body (JSON):**
```json
{
  "report_date": "{{4.report_date}}",
  "report_title": "{{4.report_title}}",
  "macro_dashboard": {{4.macro_dashboard}},
  "Executive summary": {{4.Executive summary}},
  "Market statistics": {{4.Market statistics}},
  "breadth_nasdaq_10": {{4.breadth_nasdaq_10}},
  "Top movers": {{4.Top movers}},
  "Stocks": {{4.Stocks}},
  "Sector performance": {{4.Sector performance}},
  "Forecast 5days": {{4.Forecast 5days}},
  "Action items": {{4.Action items}},
  "vix_term_structure_html": "{{82.choices[].message.content}}"
}
```

**Parse Response:**
- ✅ Cochez "Yes"
- Format: Binary

### Étape 3 : Configurer le module Email

Dans votre module Email (celui qui envoie actuellement le rapport):

**Attachments:**
1. Supprimez l'ancien attachement (s'il y en a un)
2. Ajoutez un nouvel attachment:
   - **File name:** `Nasdaq_Daily_Report_{{formatDate(now; "YYYY-MM-DD")}}.pdf`
   - **Data:** `{{[numéro_module_HTTP].data}}`
   - **MIME type:** `application/pdf`

---

## 📋 Test du service

### Test manuel (via terminal/Postman)

```bash
curl -X POST https://votre-service.up.railway.app/generate-pdf \
  -H "Content-Type: application/json" \
  -d @test_data.json \
  --output test_report.pdf
```

### Test dans Make.com

1. Lancez votre scenario Make.com
2. Vérifiez que le module HTTP reçoit bien une réponse (statut 200)
3. Vérifiez que l'email contient le PDF en pièce jointe
4. Ouvrez le PDF pour vérifier qu'il est bien formaté

---

## 🎨 Personnalisation

### Modifier les couleurs

Dans `app.py`, cherchez les codes de couleur HexColor et modifiez-les:

```python
# Exemples de couleurs actuelles:
colors.HexColor('#1E3A8A')  # Bleu foncé (header)
colors.HexColor('#3B82F6')  # Bleu vif (VIX)
colors.HexColor('#10B981')  # Vert (VIX Term Structure)
colors.HexColor('#F59E0B')  # Orange (Treasury)
```

### Ajouter/Modifier des sections

1. Modifiez le fichier `app.py`
2. Commitez sur GitHub
3. Railway redéploie automatiquement

---

## 🐛 Dépannage

### Le PDF n'est pas généré

1. **Vérifiez les logs Railway:**
   - Allez dans votre projet Railway
   - Cliquez sur "Deployments"
   - Consultez les logs

2. **Vérifiez le JSON envoyé:**
   - Dans Make.com, inspectez l'output du module HTTP
   - Assurez-vous que toutes les variables sont correctement mappées

3. **Test de santé:**
   ```bash
   curl https://votre-service.up.railway.app/health
   ```
   Devrait retourner: `{"status":"healthy"}`

### Le module HTTP échoue dans Make.com

1. **Vérifiez l'URL:** Elle doit se terminer par `/generate-pdf`
2. **Vérifiez le header:** `Content-Type: application/json`
3. **Vérifiez le JSON:** Utilisez un validateur JSON en ligne

### PDF mal formaté

1. Vérifiez que toutes les données du module 4 sont bien présentes
2. Vérifiez que le module 82 retourne bien le HTML VIX Term Structure
3. Consultez les logs Railway pour voir les erreurs

---

## 💰 Coûts

**Railway Free Tier:**
- $5 de crédit gratuit par mois
- Largement suffisant pour des rapports quotidiens
- ~500 exécutions par mois gratuitement

**Pas de carte bancaire requise pour commencer !**

---

## 🔒 Sécurité

Pour ajouter une authentification (optionnel):

1. Ajoutez une variable d'environnement `API_KEY` dans Railway
2. Modifiez `app.py` pour vérifier cette clé
3. Dans Make.com, ajoutez le header:
   ```
   Authorization: Bearer VOTRE_API_KEY
   ```

---

## 📞 Support

Si vous rencontrez des problèmes:

1. Vérifiez les logs Railway
2. Testez avec curl en ligne de commande
3. Vérifiez que Make.com envoie bien toutes les données

---

## 🚀 Prochaines améliorations possibles

- [ ] Ajouter des graphiques (courbes VIX, performance stocks)
- [ ] Support multi-langues (FR/EN)
- [ ] Envoi automatique vers Google Drive
- [ ] Historique des rapports
- [ ] Notifications par Slack/Discord

---

## 📄 Licence

Usage personnel - Service créé pour automatiser les rapports Nasdaq Daily.

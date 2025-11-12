# 🚀 Démarrage Rapide - 5 Minutes Chrono !

## Ce que vous allez obtenir

✅ Un PDF automatique parfaitement formaté à chaque exécution de votre workflow Make.com  
✅ Plus besoin d'imprimer manuellement depuis l'email  
✅ Service gratuit hébergé sur Railway  

---

## Étape 1️⃣ : Déployer le service (2 min)

1. **Créez un compte sur Railway.app** (gratuit)
   - Allez sur https://railway.app
   - Connectez-vous avec GitHub

2. **Créez un nouveau repository GitHub**
   - Nom suggéré: `nasdaq-pdf-service`
   - Uploadez tous les fichiers du ZIP

3. **Déployez sur Railway**
   - Dans Railway: "New Project" → "Deploy from GitHub repo"
   - Sélectionnez votre repository
   - Attendez 2 minutes (le déploiement est automatique)

4. **Activez l'URL publique**
   - Settings → Generate Domain
   - Copiez l'URL (ex: `nasdaq-pdf-service.up.railway.app`)

---

## Étape 2️⃣ : Configurer Make.com (2 min)

1. **Ajoutez un module HTTP après le module 82**
   - Recherchez "HTTP" → "Make a request"
   
2. **Configuration du module:**
   - **URL:** `https://VOTRE-URL.railway.app/generate-pdf`
   - **Method:** `POST`
   - **Headers:** `Content-Type: application/json`
   - **Body:** Copiez le JSON complet depuis `MAKE_CONFIG.md`
   - **Parse response:** `Yes`

3. **Modifiez votre module Email:**
   - **Attachments** → Add item
   - **File name:** `Nasdaq_Report_{{formatDate(now; "YYYY-MM-DD")}}.pdf`
   - **Data:** `{{[NUMERO_MODULE_HTTP].data}}`
   - **MIME type:** `application/pdf`

---

## Étape 3️⃣ : Testez ! (1 min)

1. Lancez votre scenario Make.com
2. Attendez l'email
3. Ouvrez le PDF 🎉

---

## 🎯 Configuration JSON simplifiée

Si vous voulez la version minimale du JSON pour tester rapidement:

```json
{
  "report_date": "{{4.report_date}}",
  "macro_dashboard": {{4.macro_dashboard}},
  "Executive summary": {{4.Executive summary}},
  "Action items": {{4.Action items}},
  "vix_term_structure_html": "{{82.choices[].message.content}}"
}
```

⚠️ Cette version minimale marchera, mais certaines sections seront vides.  
Pour le PDF complet, utilisez le JSON dans `MAKE_CONFIG.md`.

---

## ❓ Problème ?

### Le service ne répond pas
```bash
# Testez avec cette commande:
curl https://VOTRE-URL.railway.app/health
```
Devrait retourner: `{"status":"healthy"}`

### Le PDF n'arrive pas
1. Vérifiez que le module HTTP a un status 200
2. Inspectez l'output du module HTTP dans Make.com
3. Vérifiez les logs dans Railway → Deployments

### Des données manquent
Comparez votre JSON avec l'exemple dans `MAKE_CONFIG.md`

---

## 📚 Documentation complète

- **README.md** - Guide complet du service
- **MAKE_CONFIG.md** - Configuration détaillée Make.com avec tous les champs
- **app.py** - Code source (pour personnalisation)

---

## 💡 Conseils

- **Testez d'abord avec le JSON minimal** pour valider que ça marche
- **Ensuite ajoutez progressivement** les autres sections
- **Consultez les logs Railway** si quelque chose ne marche pas

---

## 🎉 Félicitations !

Votre rapport Nasdaq est maintenant **100% automatisé** ! 

Plus besoin de :
- ❌ Imprimer depuis l'email
- ❌ Corriger les coupures de page
- ❌ Ajuster la mise en page

Tout se fait automatiquement ! 🚀

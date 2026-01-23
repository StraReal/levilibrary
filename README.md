# LeviLibrary - Demo

## Descrizione
LeviLibrary è un sito web di gestione di libri con autenticazione tramite email dell'organizzazione. Solo gli utenti con email dell'organizzazione `@levi.edu.it` possono accedere, a meno che la propria email non sia inserita nella lista degli admin.

## Requisiti
- Python 3.10+
- Uvicorn
- FastAPI
- SQLAlchemy (o altro ORM utilizzato nel backend)

## Configurazione

1. Creare un file `secrets.json` nella root del progetto con le credenziali seguenti:

```json
{
  "CLIENT_ID": "",
  "CLIENT_SECRET": "",
  "REDIRECT_URI": "http://localhost:8000/auth/callback",
  "admin_emails": [
    ""
  ]
}
```

- `CLIENT_ID` e `CLIENT_SECRET` servono per l’autenticazione OAuth.  
- `REDIRECT_URI` deve corrispondere a `http://localhost:8000/auth/callback`.  
- `admin_emails` è una lista di email che possono accedere anche se non appartengono al dominio `@levi.edu.it`.  

## Avvio del sito

1. Aprire un terminale nella cartella del progetto.  
2. Eseguire:

```bash
uvicorn backend:app --reload
```

3. Il sito sarà accessibile su:

```
http://127.0.0.1:8000
```

## Accesso

- Gli utenti devono utilizzare un’email dell’organizzazione `@levi.edu.it` per autenticarsi.  
- Se la tua email non appartiene al dominio, puoi inserirla nella lista `admin_emails` di `secrets.json` per ottenere l’accesso.  

## Funzionalità principali

- Visualizzazione della libreria con paginazione  
- Ricerca libri per ID, titolo o autore  
- Aggiunta/rimozione di libri attraverso il pannello admin
- Autenticazione tramite email dell’organizzazione con Google OAuth

# LeviLibrary - Demo

## Descrizione
LeviLibrary è un sito web di gestione di libri con autenticazione tramite email dell'organizzazione. Solo gli utenti con email dell'organizzazione `@levi.edu.it` possono accedere, a meno che la propria email non sia inserita nella lista degli admin.

## Requisiti
- Python 3.10+
- Uvicorn
- FastAPI
- SQLAlchemy

E altre dependencies, che possono essere installate direttamente eseguendo
```bash
  pip install -r requirements.txt
```
nella console del venv.

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
  uvicorn backend:app
```

3. Il sito sarà accessibile su:

```
http://127.0.0.1:8000
```

## Accesso

- Gli utenti devono utilizzare un’email dell’organizzazione `@levi.edu.it` per autenticarsi.  
- Altrimenti, le email admin potranno accedere ad ogni modo.

## Funzionalità principali

- Visualizzazione della libreria con paginazione  
- Ricerca libri per ID, titolo o autore
- Filtri per homepage
- Aggiunta, modifica o rimozione di libri attraverso il pannello admin
- Autenticazione tramite email dell’organizzazione con Google OAuth
- Prestito e restituzione dei libri
- Registro attività


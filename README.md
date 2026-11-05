# HelpDesk Lite : pipeline CI/CD DevSecOps

Application web de gestion de tickets de support informatique (Flask + SQLite),
livrée par un pipeline GitHub Actions qui intègre la sécurité à chaque étape
(approche *shift-left*). L'image Docker n'est publiée sur Docker Hub que si
**tous** les contrôles de sécurité sont au vert.

> Projet PFA, ENSI Tanger. La première version de l'application est
> **volontairement vulnérable** : le pipeline détecte les failles, puis chaque
> commit de correction en élimine une catégorie.

## Fonctionnalités

- Connexion / déconnexion
- Création de tickets (titre, description, priorité)
- Liste des tickets avec filtre par statut
- Changement de statut : Ouvert → En cours → Résolu

## Pipeline de sécurité

| # | Contrôle | Outil | Ce qui est vérifié |
|---|----------|-------|--------------------|
| 1 | Secrets | Gitleaks | Clés et mots de passe écrits dans le code |
| 2 | SAST | Semgrep | Failles dans le code source (injection SQL, XSS, debug…) |
| 3 | Tests | pytest | Tests fonctionnels + tests de sécurité |
| 4 | SCA | Trivy | Bibliothèques Python avec des CVE connues |
| 5 | IaC | Trivy | Mauvaises pratiques dans le Dockerfile |
| 6 | Build | Docker | Construction de l'image (une seule fois) |
| 7 | Scan image | Trivy | CVE du système et des paquets de l'image |
| 8 | DAST | OWASP ZAP | Application en cours d'exécution (en-têtes, cookies, CSRF) |
| 9 | Publication | Docker Hub | Uniquement si 1 à 8 sont validés |

```
 push ─┬─ 1 Secrets ──┐
       ├─ 2 SAST ─────┤
       ├─ 3 Tests ────┤
       ├─ 4 SCA ──────┼──► 9 Publication Docker Hub
       ├─ 5 IaC ──────┤
       └─ 6 Build ─┬─ 7 Scan image ─┤
                   └─ 8 DAST ───────┘
```

## Lancer l'application en local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest                           # tests

# Secrets (voir .env.example). Windows PowerShell : $env:SECRET_KEY="..."
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export ADMIN_PASSWORD=<mot de passe>
python run.py                    # http://127.0.0.1:8000
```

Avec Docker :

```bash
docker build -t helpdesk-lite .
docker run -p 8000:8000 -e SECRET_KEY=<clé aléatoire> -e ADMIN_PASSWORD=<mot de passe> helpdesk-lite
```

Compte : `admin` / la valeur de `ADMIN_PASSWORD`.

# HireLens AI

**AI ATS Resume Screening Platform**

HireLens AI is a production-ready Flask web application for HR teams and recruiters. It lets recruiters register, log in, create job screening sessions, upload multiple resumes, parse candidate data, calculate ATS match percentages with pretrained NLP models, rank candidates, shortlist the top candidates by openings, export reports, and revisit previous screening history.

## Features

- Recruiter registration, login, logout, and Remember Me support
- Gmail OTP password reset with one-time, expiring OTPs
- Job requirement creation with role, skills, experience, openings, and description
- Multiple resume upload for PDF, DOCX, PNG, JPG, and JPEG
- Temporary file storage only, followed by parsing and deletion
- Candidate extraction for name, email, phone, skills, experience, education, and links
- ATS scoring with skills, semantic similarity, experience, and bonus skill weights
- Shortlisting based on ATS score and required openings
- Account-specific dashboard and screening history
- CSV and Excel exports for all candidates and shortlisted candidates
- Premium responsive AI SaaS interface

## Tech Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail, Werkzeug, python-dotenv
- **Parsing:** PyMuPDF, python-docx, pytesseract, Pillow
- **NLP / AI:** spaCy `en_core_web_sm`, Sentence Transformers `all-MiniLM-L6-v2`, scikit-learn cosine similarity
- **Export:** pandas, openpyxl
- **Database:** SQLite locally, configurable for PostgreSQL with `DATABASE_URL`
- **Deployment:** gunicorn, Render-ready `Procfile` and `render.yaml`

## Folder Structure

```text
hirelens-ai/
├── app.py
├── config/
├── auth/
├── database/
├── parsers/
├── nlp/
├── services/
├── uploads/
├── exports/
├── templates/
└── static/
```

## Installation

```bash
cd hirelens-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

For image OCR, install Tesseract OCR and make sure the `tesseract` executable is available in your system PATH.

## Environment Variables

Copy `.env.example` to `.env` and fill in values:

```env
SECRET_KEY=replace-with-a-secure-secret
DATABASE_URL=
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-gmail-address
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-gmail-address
```

Leave `DATABASE_URL` empty for local SQLite. For PostgreSQL deployment, set a valid SQLAlchemy database URL.

## Run Locally

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

## How ATS Scoring Works

Total ATS score is capped at 100:

- Skills Match: 40%
- Semantic Similarity: 30%
- Experience Match: 20%
- Bonus Skills: 10%

The app combines the job role, required skills, required experience, and job description into one job profile. It compares that against the extracted resume profile using `all-MiniLM-L6-v2` sentence embeddings and cosine similarity. Skill detection combines keyword matching from the skills database with semantic matching. The final status is:

- 85+ Excellent Match
- 70-84 Good Match
- 50-69 Moderate Match
- Below 50 Weak Match

## Authentication

Passwords are hashed with Werkzeug. Flask-Login protects dashboard, screening, results, history, and download routes. Forgot password uses Gmail SMTP to send a 6-digit OTP. OTPs expire after 5 minutes, are single-use, and reject excessive attempts.

## Resume Parsing

- PDF resumes are parsed with PyMuPDF.
- DOCX resumes are parsed with python-docx.
- Image resumes are parsed with Pillow and pytesseract OCR.
- Original uploaded files are temporarily saved, parsed, processed, and deleted. Only structured candidate data is stored.

## Deploy on Render

Use the included `render.yaml`, or configure manually:

- Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
- Start command: `gunicorn app:app`
- Add all required environment variables in Render.
- For production persistence, configure PostgreSQL and set `DATABASE_URL`.

## Future Improvements

- Background task queue for very large resume batches
- Cloud object storage for temporary processing in distributed deployments
- Admin analytics and role-based permissions
- Advanced duplicate candidate detection
- More export templates and branded PDF reports

## Screenshots

Add screenshots here after running the application locally.


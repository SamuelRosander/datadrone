# datadrone

An app to keep track of anything and everything and get statistics about it.

### Requirements

- External database (Built and tested with PostgreSQL)



## Environment variables needed

```
DD_DATABASE_URI = postgresql://user:password@192.168.0.10:5432/datadrone
DD_MAIL_USERNAME = example.noreply@gmail.com
DD_MAIL_PASSWORD = password
DD_SECRET_KEY = randomstring
DD_GOOGLEMAPS_KEY = googlemapskey
```

### Initial setup
1.      git clone https://github.com/SamuelRosander/datadrone.git
        cd datadrone
        copy .env.sample .env
        python -m venv .venv
        .venv\Scripts\activate
        pip install -r .\requirements.txt
2. Set values in .env
3.      python
        from datadrone import create_app
        from datadrone.extensions import db
        from dotenv import load_dotenv

        load_dotenv()
        create_app().app_context().push()
        db.create_all()

### Running locally (Windows)
1.      .venv\Scripts\activate
        flask run

### Docker
1.      docker build -t datadrone .
2.      docker run -e DD_DATABASE_URI=postgresql://user:password@192.168.0.10:5432/datadrone -e DD_MAIL_PASSWORD=SrHfE2VSujSTBRL -e DD_MAIL_USERNAME=example.noreply@gmail.com -e DD_SECRET_KEY=728d6d6793e295996aafbb6f741542 -e DD_GOOGLEMAPS_KEY=AIheiDdij223JH2si92S_R82iaxNW292Nqo09xs -p 8000:8000 datadrone
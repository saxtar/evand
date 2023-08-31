from app import init
from dotenv import load_dotenv, find_dotenv

if  __name__ == '__main__':  
    load_dotenv(find_dotenv())
    from app.app import create_app
    app = create_app()
    app.run(debug=True)

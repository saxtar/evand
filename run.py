from app import init

if  __name__ == '__main__':  
    from app.app import create_app
    app = create_app()
    app.run(debug=True)

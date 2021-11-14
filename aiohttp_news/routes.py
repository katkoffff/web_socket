from views import index, getnews


def setup_routes(app):
    app.router.add_get('/', index)


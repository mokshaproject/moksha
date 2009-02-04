"""Moksha middleware initialization"""

from moksha.config.app_cfg import base_config
from moksha.config.environment import load_environment
from moksha.middleware import (MokshaMiddleware, MokshaConnectorMiddleware,
                              MokshaExtensionPointMiddleware)

# Use base_config to setup the necessary WSGI App factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)

def make_app(global_conf, full_stack=True, **app_conf):
    app = make_base_app(global_conf, wrap_app=MokshaMiddleware,
                        full_stack=True,
                        **app_conf)

    app = MokshaConnectorMiddleware(app)
    app = MokshaExtensionPointMiddleware(app)

    if base_config.squeeze:
        from repoze.squeeze.processor import ResourceSqueezingMiddleware
        app = ResourceSqueezingMiddleware(
                app,
                cache_dir='public/cache',
                url_prefix='/cache/',
                )

    if base_config.profile:
        from repoze.profile.profiler import AccumulatingProfileMiddleware
        app = AccumulatingProfileMiddleware(
                app,
                log_filename='profile.log',
                discard_first_request=True,
                flush_at_shutdown=True,
                path='/__profile__'
                )

    return app
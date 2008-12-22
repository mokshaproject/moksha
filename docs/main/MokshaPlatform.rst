===============
Moksha Platform
===============

Not only can Moksha be inserted into any existing WSGI-compliant application,
but on it's own offers a comprehensive top-to-bottom middleware stack that
provides a vast plethora of additional functionality.

`WSGI <http://wsgi.org>`_ Middleware Stack
------------------------------------------

===============================     ===============
Middleware Function                 Module
===============================     ===============
Profiling                           repoze.profile
Resource compression                repoze.squeeze
Theming engine                      Deliverance
                 **TG2 Middleware**
---------------------------------------------------
Application routing/dispatching     Routes
Session management                  Beaker
Caching layer                       Beaker
Widget resource injection           ToscaWidgets
Authentication                      repoze.who
Authorization                       repoze.what
Transaction management              repoze.tm2
Error handling & Debugging          WebError
Registry manager                    Paste
                 **Moksha Middleware**
---------------------------------------------------
Your application
===============================     ===============

from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^monitor/', include('monitor.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^main/$', 'main.views.index'),
    (r'^stats/interface/$', 'stats.views.interface'),
    (r'^stats/ethernet/$', 'stats.views.ethernet'),
    (r'^stats/capture/$', 'stats.views.capture'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root' : settings.MEDIA_ROOT, 'show_indexes': True })
)

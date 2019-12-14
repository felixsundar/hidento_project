from hidento_project import settings

def secretcrushapp_context_processor(request):
    return {
        'WEBSITE_COLOR':settings.WEBSITE_COLOR
    }
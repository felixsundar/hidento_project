from hidento_project import settings

def secretcrushapp_context_processor(request):
    return {
        'HIDENTO_BACKGROUND_COLOR':settings.HIDENTO_BACKGROUND_COLOR,
        'HIDENTO_HEADING_FONT_COLOR':settings.HIDENTO_HEADING_FONT_COLOR,
        'HIDENTO_FONT_COLOR':settings.HIDENTO_FONT_COLOR,
        'BASE_DIR':settings.BASE_DIR,
    }
from rest_framework import renderers
import json

class CustomJSONRenderer(renderers.JSONRenderer):
    charset = 'utf-8'
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = ""
        if 'ErrorDetails' in data:
            response = json.dumps({'error':data})
        else:
            response = json.dumps({'data':data})

        return response
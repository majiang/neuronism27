from os import path
from google.appengine.ext.webapp import template

app_root = path.dirname(__file__)

def template_path(file_name):
    return path.join(app_root, 'template/%s.html' % file_name)

def render(file_name, content):
    return template.render(template_path(file_name), content)

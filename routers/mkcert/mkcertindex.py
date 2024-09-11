from flask import Blueprint, current_app, render_template, url_for

mkcert_module = Blueprint('mkcert_module', __name__)


@mkcert_module.route('/', methods=['GET'])
def index():
    html_page = current_app.config['CONF']['mkcert']['html']['index']
    url_list = current_app.config['CONF']['mkcert']['link']['index']
    return render_template(html_page, url_list=url_list)

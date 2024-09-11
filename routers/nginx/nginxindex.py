from flask import Blueprint, render_template, current_app


nginx_module = Blueprint('nginx_module', __name__)


@nginx_module.route('/', methods=['GET'])
def index():
    """ 索引导航页
    """
    html_page = current_app.config["CONF"]["nginx"]["html"]["index"]
    url_list = current_app.config["CONF"]["nginx"]["link"]["index"]
    return render_template(html_page, url_list=url_list)
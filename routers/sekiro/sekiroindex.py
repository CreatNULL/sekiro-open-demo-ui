from flask import Blueprint, current_app, render_template, url_for

sekiro_module = Blueprint('sekiro_module', __name__)


@sekiro_module.route('/', methods=['GET'])
def index():
    """ 索引导航页
    """
    html_page = current_app.config["CONF"]["sekiro"]["html"]["index"]
    url_list = current_app.config["CONF"]["sekiro"]["link"]["index"]
    return render_template(html_page, url_list=url_list)
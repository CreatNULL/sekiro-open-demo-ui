# coding: utf-8
"""
    管理配置 nginx for windows
"""
import os
import subprocess
from flask import Blueprint, render_template, current_app, request, url_for
from util.service.servicemanger import ServiceManager, manage_service_in_thread
from config import CONF
# 实例化管理服务对象
print()
nginx_manger = ServiceManager(CONF['nginx']['service']['name'], bin_name=CONF['nginx']['app']['nginx']['bin_name'])
# nginx_manger = ServiceManager(current_app.config['CONF']['nginx']['service']['name'])

nginx_router = Blueprint('nginx_router', __name__)


@nginx_router.route('/manager')
def manager():
    html_page = current_app.config["CONF"]["nginx"]["html"]["nginx_router"]["manager"]
    css_file = current_app.config["CONF"]["nginx"]["css"]["nginx_router"]["manager"]
    js_file = current_app.config["CONF"]["nginx"]["js"]["nginx_router"]["manager"]
    get_status = current_app.config["CONF"]["nginx"]['api']["nginx_router"]["get_status_api"]
    start_app = current_app.config["CONF"]["nginx"]['api']["nginx_router"]["start_nginx_api"]
    stop_app = current_app.config["CONF"]["nginx"]['api']["nginx_router"]["stop_nginx_api"]
    restart_app = current_app.config["CONF"]["nginx"]['api']["nginx_router"]["restart_nginx_api"]
    get_conf = current_app.config["CONF"]["nginx"]['api']["nginx_router"]["get_conf_api"]
    set_conf = current_app.config["CONF"]["nginx"]['api']["nginx_router"]["set_conf_api"]
    return render_template(html_page, title="nginx管理配置页面", appname='Nginx', css_files=css_file, js_files=js_file,
                           get_status=url_for(get_status),
                           start_app=url_for(start_app),
                           stop_app=url_for(stop_app),
                           restart_app=url_for(restart_app),
                           get_conf=url_for(get_conf),
                           set_conf=url_for(set_conf),)


@nginx_router.route('/api/get_status', methods=['GET'])
def get_status_api():
    return nginx_manger.get_service_status()


@nginx_router.route('/api/stop', methods=['GET'])
def stop_nginx_api():
    return manage_service_in_thread(nginx_manger, 'stop')


@nginx_router.route('/api/start', methods=['GET'])
def start_nginx_api():
    bin_file = current_app.config["CONF"]["nginx"]["app"]["nginx"]["bin"]
    config_file = current_app.config['CONF']['nginx']['app']["nginx"]['conf']

    if not os.path.exists(bin_file):
        return {"status": "failed", "msg": "Nginx 程序不存在"}
    if not os.path.exists(config_file):
        return {"status": "failed", "msg": "Nginx配置文件丢失"}

    return manage_service_in_thread(nginx_manger, 'start')


@nginx_router.route('/api/restart', methods=['GET'])
def restart_nginx_api():
    bin_file = current_app.config["CONF"]["nginx"]["app"]["nginx"]["bin"]
    config_file = current_app.config['CONF']['nginx']['app']["nginx"]['conf']
    if not os.path.exists(bin_file):
        return {"status": "failed", "msg": "Nginx 程序不存在"}
    if not os.path.exists(config_file):
        return {"status": "failed", "msg": "Nginx配置文件丢失"}
    result = manage_service_in_thread(nginx_manger, 'restart')
    return result


@nginx_router.route('/api/get_config', methods=['GET'])
def get_conf_api():
    """ 获取 nginx 配置文件 内容
    """
    config_file = current_app.config['CONF']['nginx']['app']["nginx"]['conf']

    if os.path.exists(config_file):
        with open(config_file, mode='r', encoding='utf-8') as file:
            content = file.read()
            return {"config_file": content}
    else:
        return {"status": "failed", "msg": f"nginx 配置文件不存在"}


@nginx_router.route('/api/set_config', methods=['POST'])
def set_conf_api():
    """ 获取前端提交的字符串，然后写入配置文件

    前端提交示例:
    let configString = "这是您的配置文件内容";  // 替换为实际的配置字符串

    let xhr = new XMLHttpRequest();
    xhr.open('POST', '/write_nginx_config');
    xhr.setRequestHeader('Content-Type', 'text/plain');

    xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let response = JSON.parse(xhr.responseText);
            console.log(response);
        }
    };

    xhr.send(configString);
    """
    config_content = request.data.decode('utf-8')  # 从请求中获取配置字符串
    config_file = current_app.config['CONF']['nginx']['app']["nginx"]['conf']

    print(config_content)
    if not os.path.exists(config_file):
        return {"status": "failed", "msg": "配置文件不存在"}

    try:
        with open(config_file, mode='r', encoding='utf-8') as backup_file:
            backup_file_content = backup_file.read()
            with open(config_file, mode='w', encoding='utf-8') as write_file:
                write_file.write(config_content)
            check_config_result = check_config()
            if check_config_result['status'] != 'success':
                with open(config_file, mode='w', encoding='utf-8') as callback_backup_file:
                    callback_backup_file.write(backup_file_content)
                return {"status": "failed", "msg": check_config_result['msg']}
            else:
                return {"status": "success", 'msg': '配置写入成功'}
    except Exception as e:
        return {"status": "failed", 'msg': f'配置写入失败: {str(e)}'}


def check_config():
    try:
        # 获取当前工作目录
        original_path = os.getcwd()

        # 切换到指定的路径
        nginx_path = current_app.config['CONF']['nginx']['app']["nginx"]['path']
        os.chdir(nginx_path)

        # 使用 Popen 调用 nginx 配置检查
        process = subprocess.Popen(
            [current_app.config['CONF']['nginx']['app']["nginx"]['bin'], '-t'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # 获取输出和错误信息
        _, output = process.communicate()
        print(output)
        if 'test failed' in output:
            return {"status": "failed", "msg": output}
        elif 'test is successful' in output:
            return {"status": "success", "msg": "检测通过"}
        else:
            return {"status": "failed", "msg": '其他情况' + output}
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
    finally:
        # 切换回原来的工作目录
        os.chdir(original_path)


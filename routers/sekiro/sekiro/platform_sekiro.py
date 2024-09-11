# coding: utf-8
"""
    sekiro - js 文件
    参考:
        https://github.com/downdawn/JSreverse/blob/master/sekiro/sekiro_demo.html
"""
import os
import json
from typing import Dict
try:
    import requests
except ModuleNotFoundError:
    os.system('pip install requests')
from flask import Blueprint, render_template, current_app, send_file, request, redirect, Response, make_response, url_for
from util.service.servicemanger import ServiceManager, manage_service_in_thread
from config import CONF


monkey_js = """ 


"""
sekiro_router = Blueprint('sekiro_router', __name__)


@sekiro_router.route('/createTampermonkey_page', methods=['GET'])
def create_tampermonkey_page():
    html_file = current_app.config['CONF']['sekiro']['html']['sekiro_router']['create_tampermonkey_page']
    js_files = current_app.config['CONF']['sekiro']['js']['sekiro_router']['create_tampermonkey_page']
    css_files = current_app.config['CONF']['sekiro']['css']['sekiro_router']['create_tampermonkey_page']
    create_tampermonkey_js_api = current_app.config['CONF']['sekiro']['api']['sekiro_router']['create_tampermonkey_js_api']
    group_list = current_app.config['CONF']['sekiro']['api']['sekiro_router']['group_list_api']
    clinet_queue = current_app.config['CONF']['sekiro']['api']['sekiro_router']['client_queue_api']
    return render_template(html_file,
                           title="sekiro",
                           css_files=css_files,
                           js_files=js_files,
                           create_tampermonkey_js_api=url_for(create_tampermonkey_js_api),
                           group_list=url_for(group_list),
                           clinet_queue=url_for(clinet_queue)
                           )

@sekiro_router.route('/api/web_client_js', methods=['GET'])
def get_web_client_js_api() -> Response:
    """ sekiro_web_client.js 文件
    反正文件的内容, 如果本地文件访问失败，跳转到 远程服务器上的
    """
    try:
        js_file = os.path.join('static', current_app.config['CONF']['sekiro']['sekiro']['js']['sekiro']['sekiro']['get_web_client_js'][0])
        return send_file(js_file)
    except Exception as e:
        print(e)
        return redirect('http://file.virjar.com/sekiro_web_client.js')


@sekiro_router.route("/api/create_tampermonkey_js", methods=['POST'])
def create_tampermonkey_js_api() -> Dict[str, str]:
    """ 根据 post 提交的数据，返回生成的 油猴脚本代码
    post提交的时候的必要参数: protcol、group、client_id
    """

    try:
        # 获取使用的协议 ws / wss
        protcol = request.form.get('protocol')
        #
        if protcol not in ['ws', 'wss']:
            return {"error": "协议错误"}

        host = request.form.get('host')
        if not host:
            return {"error": "未指定主机"}

        port = request.form.get('port')
        if not port:
            return {"error": "未指定端口"}

        # 获取创建使用的组名
        group = request.form.get('group')
        if not group:
            return {"error": "未指定创建的组名"}

        # 获取创建使用的客户端id
        client_id = request.form.get('clientId')
        if not client_id:
            return {"error": "未指定创建的客户端 id"}

        # 获取前端提交的需要注入的代码
        jscode = request.form.get('code')

        # sekiro_web_client.js 的文件 url
        web_client_js_url = current_app.config['PROTOCOL'] + "://" + current_app.config['HOST'] + ':' + current_app.config['PORT'] + url_for('sekiro_router.get_web_client_js_api')
        if not web_client_js_url:
            return {"error": "尚未指定 sekiro 的 sekiro_web_client.js 文件的 URL"}
        client = protcol + "://" + str(host) + ":" + str(port) + "/business-demo/register?group=" + str(group).strip().replace('/', '').replace('\\', '').replace('&', '_') + "&clientId=" + str(client_id).strip().replace('/', '').replace('\\', '').replace('&', '_')
    except Exception as e:
        return {"error": str(e)}

    Tampermonkey_script = """ 
// ==UserScript==
// @name         sekiro script
// @namespace    http://tampermonkey.net/
// @version      2024-09-03
// @description  try to take over the world!
// @author       You
// @match        http://*/*
// @match        https://*/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=tampermonkey.net
// @grant        none
// ==/UserScript==


(function() {
    'use strict';
    """ + """ 
    function SekiroClient(e) {
        if (this.wsURL = e, this.handlers = {}, this.socket = {}, !e) throw new Error("wsURL can not be empty!!");
        this.webSocketFactory = this.resolveWebSocketFactory(), this.connect()
    }
    SekiroClient.prototype.resolveWebSocketFactory = function() {
        if ("object" == typeof window) {
            var e = window.WebSocket ? window.WebSocket : window.MozWebSocket;
            return function(o) {
                function t(o) {
                    this.mSocket = new e(o)
                }
                return t.prototype.close = function() {
                    this.mSocket.close()
                }, t.prototype.onmessage = function(e) {
                    this.mSocket.onmessage = e
                }, t.prototype.onopen = function(e) {
                    this.mSocket.onopen = e
                }, t.prototype.onclose = function(e) {
                    this.mSocket.onclose = e
                }, t.prototype.send = function(e) {
                    this.mSocket.send(e)
                }, new t(o)
            }
        }
        if ("object" == typeof weex) try {
            console.log("test webSocket for weex");
            var o = weex.requireModule("webSocket");
            return console.log("find webSocket for weex:" + o),
                function(e) {
                    try {
                        o.close()
                    } catch (e) {}
                    return o.WebSocket(e, ""), o
                }
        } catch (e) {
            console.log(e)
        }
        if ("object" == typeof WebSocket) return function(o) {
            return new e(o)
        };
        throw new Error("the js environment do not support websocket")
    }, SekiroClient.prototype.connect = function() {
        console.log("sekiro: begin of connect to wsURL: " + this.wsURL);
        var e = this;
        try {
            this.socket = this.webSocketFactory(this.wsURL)
        } catch (o) {
            return console.log("sekiro: create connection failed,reconnect after 2s:" + o), void setTimeout(function() {
                e.connect()
            }, 2e3)
        }
        this.socket.onmessage(function(o) {
            e.handleSekiroRequest(o.data)
        }), this.socket.onopen(function(e) {
            console.log("sekiro: open a sekiro client connection")
        }), this.socket.onclose(function(o) {
            console.log("sekiro: disconnected ,reconnection after 2s"), setTimeout(function() {
                e.connect()
            }, 2e3)
        })
    }, SekiroClient.prototype.handleSekiroRequest = function(e) {
        console.log("receive sekiro request: " + e);
        var o = JSON.parse(e),
            t = o.__sekiro_seq__;
        if (o.action) {
            var n = o.action;
            if (this.handlers[n]) {
                var s = this.handlers[n],
                    i = this;
                try {
                    s(o, function(e) {
                        try {
                            i.sendSuccess(t, e)
                        } catch (e) {
                            i.sendFailed(t, "e:" + e)
                        }
                    }, function(e) {
                        i.sendFailed(t, e)
                    })
                } catch (e) {
                    console.log("error: " + e), i.sendFailed(t, ":" + e)
                }
            } else this.sendFailed(t, "no action handler: " + n + " defined")
        } else this.sendFailed(t, "need request param {action}")
    }, SekiroClient.prototype.sendSuccess = function(e, o) {
        var t;
        if ("string" == typeof o) try {
            t = JSON.parse(o)
        } catch (e) {
            (t = {}).data = o
        } else "object" == typeof o ? t = o : (t = {}).data = o;
        (Array.isArray(t) || "string" == typeof t) && (t = {
            data: t,
            code: 0
        }), t.code ? t.code = 0 : (t.status, t.status = 0), t.__sekiro_seq__ = e;
        var n = JSON.stringify(t);
        console.log("response :" + n), this.socket.send(n)
    }, SekiroClient.prototype.sendFailed = function(e, o) {
        "string" != typeof o && (o = JSON.stringify(o));
        var t = {};
        t.message = o, t.status = -1, t.__sekiro_seq__ = e;
        var n = JSON.stringify(t);
        console.log("sekiro: response :" + n), this.socket.send(n)
    }, SekiroClient.prototype.registerAction = function(e, o) {
        if ("string" != typeof e) throw new Error("an action must be string");
        if ("function" != typeof o) throw new Error("a handler must be function");
        return console.log("sekiro: register action: " + e), this.handlers[e] = o, this
    };
    // 示例: """ + f"{'http' if 'ws' else 'https'}://{host}:{port}/business-demo/invoke?group={group}&action=testAction" + """
    var client = new SekiroClient(""" + '"' + client + '"' + """); 
""" + """
    client.registerAction("testAction", function(request, resolve, reject) {
        resolve("ok");
    });
""" + jscode + """ 
})();
"""

    return {"script": Tampermonkey_script}


@sekiro_router.route('/api/download/certificate/<type>', methods=['GET'])
def get_sekiro_certificate_api(type):
    """ 提供证书下载功能
    """
    if type == 'crt':
        cert_file = os.path.join('static', current_app.config['CONF']['cert']['sekiro']['pc']['crt'])
    elif type == 'pem':
        cert_file = os.path.join('static', current_app.config['CONF']['cert']['sekiro']['pc']['pem'])
    else:
        return {"error": "没有改类型的证书"}

    return send_file(cert_file)


@sekiro_router.route("/query_info", methods=['GET'])
def query_info() -> str:
    html_page = current_app.config['CONF']['sekiro']['html']['sekiro_router']['query_info']
    group_list = current_app.config['CONF']['sekiro']['api']['sekiro_router']['group_list_api']
    client_queue = current_app.config['CONF']['sekiro']['api']['sekiro_router']['client_queue_api']
    invoke = current_app.config['CONF']['sekiro']['api']['sekiro_router']['invoke_api']
    js_files = current_app.config['CONF']['sekiro']['js']['sekiro_router']['query_info']
    css_files = current_app.config['CONF']['sekiro']['css']['sekiro_router']['query_info']
    return render_template(html_page,
                           title='Sekiro API',
                           js_files=js_files,
                           css_file=css_files,
                           group_list_api=url_for(group_list),
                           client_queue_api=url_for(client_queue),
                           invoke_api=url_for(invoke),
                           )


@sekiro_router.route('/api/groupList', methods=['GET', 'POST'])
def group_list_api():
    """  获取注册的组列表
    """
    group_list_url = current_app.config['CONF']['outapi']['sekiro']['groupList']

    try:
        if request.method == 'GET':
            # 转发 GET 请求并传递查询参数
            params = request.args.to_dict()  # 获取所有查询参数
            response = requests.get(group_list_url, params=params)
            # 返回目标 URL 的响应内容
            return response.json()
        elif request.method == 'POST':
            # 转发 POST 请求并传递表单数据
            data = request.form.to_dict()  # 获取所有表单数据
            response = requests.post(group_list_url, data=data)
            # 返回目标 URL 的响应内容
            return response.json()
    except Exception as e:
        return {"error": str(e)}


@sekiro_router.route('/api/invoke', methods=['POST'])
def invoke_api():
    """ 处理前端 POST 请求并转发到目标 URL """
    # 获取必需的参数
    group = request.form.get('group')
    action = request.form.get('action')

    if not group or not action:
        return {"error": "Missing required parameters: 'group' and 'action'"}

    invoke_url = current_app.config['CONF']['outapi']['sekiro']['invoke']
    try:
        if request.method == 'GET':
            params = request.args.to_dict()  # 获取所有查询参数
            response = requests.get(invoke_url, params=params)
            return response.json()
        elif request.method == 'POST':
            params = request.form.to_dict()  # 获取所有表单参数
            response = requests.post(invoke_url, json=params)
            return response.json()
    except Exception as e:
        return {"error": str(e)}
    # 返回响应内容


@sekiro_router.route('/api/clientQueue', methods=['GET', 'POST'])
def client_queue_api():
    """ 请求指定的组的信息
    """
    """ 请求指定的组的信息 """
    client_queue_url = current_app.config['CONF']['outapi']['sekiro']['clientQueue']

    try:
        params = {}
        if request.method == 'GET':
            params = request.args.to_dict()  # 获取所有查询参数
        elif request.method == 'POST':
            params = request.form.to_dict()  # 获取所有表单参数

        # 转发请求到 client_queue_url
        response = requests.get(client_queue_url, params=params)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
    # 返回响应内容



# ----------------------------------- 管理 sekiro 服务的 ------------------------------------------


# 实例化管理服务对象
sekiro_manger = ServiceManager(CONF['sekiro']['service']['name'], CONF['sekiro']['app']['sekiro']['bin_name'])


@sekiro_router.route('/manager', methods=['GET'])
def manager():
    html_page = current_app.config['CONF']['sekiro']['html']['sekiro_router']['manager']
    css_file = current_app.config["CONF"]["sekiro"]["css"]["sekiro_router"]["manager"]
    js_file = current_app.config["CONF"]["sekiro"]["js"]["sekiro_router"]["manager"]
    get_status = current_app.config['CONF']['sekiro']['api']['sekiro_router']['get_status_api']
    start_app = current_app.config['CONF']['sekiro']['api']['sekiro_router']['start_sekiro_api']
    stop_app = current_app.config['CONF']['sekiro']['api']['sekiro_router']['stop_sekiro_api']
    restart_app = current_app.config['CONF']['sekiro']['api']['sekiro_router']['restart_sekiro_api']
    get_conf = current_app.config['CONF']['sekiro']['api']['sekiro_router']['get_conf_api']
    set_conf = current_app.config['CONF']['sekiro']['api']['sekiro_router']['set_conf_api']
    return render_template(html_page,
                           title='Sekiro管理工具',
                           css_files=css_file,
                           js_files=js_file,
                           appname='Sekiro',
                           get_status=url_for(get_status),
                           start_app=url_for(start_app),
                           stop_app=url_for(stop_app),
                           restart_app=url_for(restart_app),
                           get_conf=url_for(get_conf),
                           set_conf=url_for(set_conf))


@sekiro_router.route("api/get_status", methods=['GET'])
def get_status_api():
    return sekiro_manger.get_service_status()


@sekiro_router.route("api/start_sekiro", methods=['GET'])
def start_sekiro_api():
    bin_file = current_app.config["CONF"]["sekiro"]["app"]["sekiro"]["bin"]
    config_file = current_app.config['CONF']['sekiro']['app']["sekiro"]['conf']

    if not os.path.exists(bin_file):
        return {"status": "failed", "msg": "sekiro 程序不存在"}
    if not os.path.exists(config_file):
        return {"status": "failed", "msg": "sekiro配置文件丢失"}

    return manage_service_in_thread(sekiro_manger, 'start')


@sekiro_router.route("api/stop_sekiro", methods=['GET'])
def stop_sekiro_api():
    return manage_service_in_thread(sekiro_manger, 'stop')


@sekiro_router.route("api/restart_sekiro", methods=['GET'])
def restart_sekiro_api():
    bin_file = current_app.config["CONF"]["sekiro"]["app"]["sekiro"]["bin"]
    config_file = current_app.config['CONF']['sekiro']['app']["sekiro"]['conf']
    if not os.path.exists(bin_file):
        return {"status": "failed", "msg": "sekiro 程序不存在"}
    if not os.path.exists(config_file):
        return {"status": "failed", "msg": "sekiro配置文件丢失"}
    result = manage_service_in_thread(sekiro_manger, 'restart')
    if 'Already started' in result['msg']:
        return {"status": "failed", "msg": "请再次尝试重启"}
    return result


@sekiro_router.route("api/set_conf", methods=['POST'])
def set_conf_api():
    config_content = request.data.decode('utf-8')  # 从请求中获取配置字符串
    config_file = current_app.config['CONF']['sekiro']['app']["sekiro"]['conf']

    if not os.path.exists(config_file):
        return {"status": "failed", "msg": "配置文件不存在"}

    try:
        if '=' not in config_content:
            return {"status": "failed", "msg": "配置文件内容格式错误"}

        tmp_content = config_content.split("=")
        if len(tmp_content) != 2:
            return {"status": "failed", "msg": "配置文件内容格式错误, 目前仅支持修改端口"}

        key, port = tmp_content
        if not key or key.strip() != 'sekiro.port':
            return {"status": "failed", "msg": "配置文件内容格式错误, 目前仅支持修改端口"}
        try:
            port = int(port)
            if port > 0 and port < 65536:
                pass
            else:
                return {"status": "failed", "msg": "指定的端口错误"}
        except:
            return {"status": "failed", "msg": "指定的端口错误"}


        with open(config_file, mode='w', encoding='utf-8') as write_file:
            write_file.write(config_content)

            return {"status": "success", 'msg': '配置写入成功'}
    except Exception as e:
        return {"status": "failed", 'msg': f'配置写入失败: {str(e)}'}


@sekiro_router.route("api/get_conf", methods=['GET'])
def get_conf_api():
    config_file = current_app.config['CONF']['sekiro']['app']["sekiro"]['conf']

    if os.path.exists(config_file):
        with open(config_file, mode='r', encoding='utf-8') as file:
            content = file.read()
            return {"config_file": content}
    else:
        return {"status": "failed", "msg": f"sekiro 配置文件不存在"}

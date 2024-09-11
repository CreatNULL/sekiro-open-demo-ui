import os
from config import CONF
from util.service.servicemanger import ServiceManager
import subprocess


def install_nginx_service():
    # 实例化服务管理对象
    server_manager = ServiceManager(CONF['nginx']['service']['name'])
    # 查询服务注册状态
    status = server_manager.get_service_status()

    nginx_bin = CONF['nginx']['app']['nginx']['bin']
    nginx_service_bin = CONF['nginx']['app']['nginx_service']['bin']
    nginx_service_xml = CONF['nginx']['app']['nginx_service']['conf']
    nginx_service_log = CONF['nginx']['app']['nginx_service']['log']

    # 文件丢失不存在
    if not os.path.exists(nginx_bin):
        print("nginx bin not found, error path: {}".format(nginx_bin))
        return "Not installed"
    if not os.path.exists(nginx_service_bin):
        print("nginx service bin not found, error path: {}".format(nginx_service_bin))
        return "Not installed"
    if not os.path.exists(nginx_service_log):
        print("nginx service log directory not found, error path: {}".format(nginx_service_log))
        return "Not installed"

    # 如果服务没有注册
    if 'Not Installed' in status['msg']:
        nginx_tool_str = """
<service>
    <id>nginx</id>
    <name>Nginx Service for sekiro</name>
    <description>Nginx Service for sekiro</description>
    <logpath>""" + nginx_service_log + """</logpath>
    <logmode>roll</logmode>
    <executable>""" + nginx_bin + """</executable>
    <startarguments></startarguments>
    <stoparguments>-s stop</stoparguments>
</service>"""

        with open(nginx_service_xml, "w", encoding='utf-8') as fp:
            fp.write(nginx_tool_str)

        if not os.path.exists(nginx_service_xml):
            print("nginx service xml not found")
            return "Not Installed"

        # 使用 WinSW.exe 来注册服务
        result = subprocess.run(nginx_service_bin + " install", shell=True, capture_output=True)
        # 通过返回码判断是否成功，0 通常表示成功，非 0 表示失败
        if result.returncode == 0:
            status = server_manager.get_service_status()
            if 'Not Installed' in status['msg']:
                return 'Not Installed'
            else:
                return 'Install Successful'
        else:
            print("安装失败")
            print("错误信息: ", result.stderr.decode('utf-8'))
            print("输出信息: ", result.stdout.decode('utf-8'))
            return 'Not Installed'

    # 已经注册的状态
    return 'Install Already'


def install_sekiro_service():
    sekiro_bin = CONF['sekiro']['app']['sekiro']['bin']
    sekiro_service_bin = CONF['sekiro']['app']['sekiro_service']['bin']
    # 文件丢失不存在
    if not os.path.exists(sekiro_service_bin):
        print("sekiro bin not found, error path: {}".format(sekiro_service_bin))
        return "Not Installed"
    if not os.path.exists(sekiro_service_bin):
        print("sekiro service bin not found, error path: {}".format(sekiro_service_bin))
        return "Not Installed"

    # 实例化服务管理对象
    server_manager = ServiceManager('Sekiro Service', binary_path=sekiro_bin, nssm_path=sekiro_service_bin)
    # 查询服务注册状态
    status = server_manager.get_service_status()

    # 尚未安装服务
    if 'Not Installed' in status['msg']:
        install_status = server_manager.install_service_by_nssm()
        if install_status['status'] != 'success':
            return 'Not Installed'
        else:
            return 'Install Successful'

    return 'Install Already'


if __name__ == '__main__':
    # install_nginx_service()
    # install_sekiro_service()
    a = ServiceManager(CONF['nginx']['service']['name'])
    a.uninstall_service()
    b = ServiceManager(CONF['sekiro']['service']['name'])
    b.uninstall_service()
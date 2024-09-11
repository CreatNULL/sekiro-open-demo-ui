import os
import subprocess
from flask import Blueprint, request, jsonify, current_app, render_template, url_for


mkcert_router = Blueprint('mkcert_router', __name__)


@mkcert_router.route('/aip/create_cert', methods=['GET', 'POST'])
def create_cert_api():
    if request.method == 'POST':
        # Get domains and strip unnecessary spaces
        domains = request.form.get('domains', '').strip()
        install = request.form.get('install') == 'on'
        uninstall = request.form.get('uninstall') == 'on'

        # Replace commas with spaces, remove duplicates and empty values
        domain_list = domains.replace(',', ' ').split()
        unique_domains = list(set(filter(None, domain_list)))

        if not unique_domains and not install and not uninstall:
            return jsonify({'success': False, 'message': '没有有效的域名!'})

        mkcert_bin = current_app.config['CONF']['mkcert']['app']['mkcert']['bin']
        cert_file = os.path.join(current_app.config['CONF']['nginx']['app']['nginx']['path'], 'ssl/server.crt')
        key_file = os.path.join(current_app.config['CONF']['nginx']['app']['nginx']['path'], 'ssl/server.key')

        # Call mkcert to generate the certificate
        try:
            subprocess.run([mkcert_bin,
                            '--cert-file', cert_file,
                            '--key-file', key_file] + unique_domains,
                           check=True)

            # 以管理员运行
            if install:
                try:
                    subprocess.run([mkcert_bin, '-install'], check=True, text=True)
                except subprocess.CalledProcessError as e:
                    return jsonify({'success': False, 'message': f'安装证书失败: {str(e)}'})

            if uninstall:
                try:
                    subprocess.run([mkcert_bin, '-uninstall'], check=True, text=True)
                except subprocess.CalledProcessError as e:
                    return jsonify({'success': False, 'message': f'卸载证书失败: {str(e)}'})

            return jsonify({'success': True, 'message': '证书生成成功!'})

        except subprocess.CalledProcessError as e:
            return jsonify({'success': False, 'message': f'生成证书失败: {str(e)}'})


@mkcert_router.route('/create_cert', methods=['GET', 'POST'])
def create_cert():
    html_file = current_app.config['CONF']['mkcert']['html']['mkcert_router']['create_cert']
    create_cert = current_app.config['CONF']['mkcert']['api']['mkcert_router']['create_cert']
    js_file = current_app.config['CONF']['mkcert']['js']['mkcert_router']['create_cert']
    css_file = current_app.config['CONF']['mkcert']['css']['mkcert_router']['create_cert']
    return render_template(html_file, title="mkcert工具", css_files=css_file, js_files=js_file, create_cert=url_for(create_cert))
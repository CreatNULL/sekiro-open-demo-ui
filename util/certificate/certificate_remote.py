"""
@Project ：ssl证书验证
@File    ：get_ssl.py
@IDE     ：PyCharm
@Author  ：zhizhuo
@Date    ：2023/10/19 10:13
"""
import socket
import OpenSSL
import hashlib


def get_ssl_cert_info(host):
    context = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
    conn = OpenSSL.SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))
    conn.connect((host, 443))
    conn.do_handshake()
    cert = conn.get_peer_certificate()

    issuer_components = cert.get_issuer().get_components()
    issuer_info = {component[0].decode("UTF-8"): component[1].decode("UTF-8") for component in issuer_components}

    cert_info = {
        '版本': str(cert.get_version()+1),
        '序列号': str(cert.get_serial_number()),
        '组织信息': str(cert.get_subject().organizationName),
        '颁发机构': issuer_info,
        '颁发者': str(cert.get_issuer().commonName),
        '有效期从': str(cert.get_notBefore().decode()),
        '过期时间': str(cert.get_notAfter().decode()),
        '是否过期': str(cert.has_expired()),
        '主题': str(cert.get_subject().CN),
        '证书中使用的签名算法': cert.get_signature_algorithm().decode("UTF-8"),
        '公钥长度':cert.get_pubkey().bits(),
        '公钥': OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey()).decode("utf-8"),
        '公钥SHA256指纹': hashlib.sha256(OpenSSL.crypto.dump_publickey(OpenSSL.crypto.FILETYPE_PEM, cert.get_pubkey())).hexdigest(),
        '证书SHA256指纹': hashlib.sha256(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)).hexdigest(),
    }

    return cert_info


if __name__ == "__main__":
    host = 'www.baidu.com'
    # host = 'devpress.csdn.net'
    # host = 'www.butian.net'
    cert_info = get_ssl_cert_info(host)
    for key, value in cert_info.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for sub_key, sub_value in value.items():
                print(f"    {sub_key}: {sub_value}")
        else:
            print(f"{key}: {value}")

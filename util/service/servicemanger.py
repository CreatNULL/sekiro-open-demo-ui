import os
try:
    import win32serviceutil
except ModuleNotFoundError:
    os.system("pip3 install pypiwin32")
try:
    import win32service
except ModuleNotFoundError:
    os.system("pip3 install pywin32")
import win32event
import servicemanager
import threading
import subprocess
# from util.runas.adminstrator import run_as_admin


class MyService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'MyService'  # Default service name
    _svc_display_name_ = 'My Service'  # Default display name
    _svc_description_ = 'This is a sample service.'  # Default description

    def __init__(self, service_name, binary_path):
        win32serviceutil.ServiceFramework.__init__(self, service_name, binary_path)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        while self.running:
            win32event.WaitForSingleObject(self.stop_event, 500)


class ServiceManager:
    def __init__(self, service_name, binary_path=None, bin_name=None, binary_args=None, nssm_path=None):
        """

        :param service_name:  指定服务的名称
        :param binary_path:  指定程序的路径 + 程序名称
        :param bin_name:    指定程序名,可选， 如果没有指定，默认从binary_path 中获取，用来强制结束对应名称的程序
        :param binary_args:
        """
        self.service_name = service_name
        self.binary_path = None if not binary_path else binary_path
        self.bin_name = os.path.basename(binary_path) if not bin_name and binary_path else bin_name
        self.binary_args = None if not binary_args else binary_args
        self.nssm_path = nssm_path
        self.lock = threading.Lock()  # 用于同步的线程锁
        if bin_name and not self.bin_name.endswith('.exe'):
            raise ValueError("指定的程序名称错误")

    def install_service(self):
        """ 安装系统服务

        """
        if not self.binary_path:
            raise ValueError("服务安装失败, 尚未给出程序路径")

        # run_as_admin()
        try:
            with self.lock:
                win32serviceutil.InstallService(
                    MyService,
                    self.service_name,
                    self.service_name,
                    exeName=self.binary_path,
                    exeArgs=self.binary_args,
                    startType=win32service.SERVICE_AUTO_START,
                )
            print(f'Service {self.service_name} installed.')
            return {"status": "success", "msg": f"Install Service {self.service_name} successful."}
        except Exception as e:
            # return {"status": "success", "msg": f"Service {self.service_name} installed."}
            return {"status": "failed", "msg": f"Install Service {self.service_name} failed." + str(e)}

    def uninstall_service(self):
        # run_as_admin()
        try:
            with self.lock:
                win32serviceutil.RemoveService(self.service_name)
                print(f'服务 {self.service_name} 已卸载。')
                return {"status": "success", "msg": f"Remote Service {self.service_name} successful."}
        except Exception as e:
            if '(1060' == str(e).split(",")[0]:     # (1060, 'GetServiceKeyName', '指定的服务未安装。')
                return {"status": "failed", "msg": f"Remote Service {self.service_name} failed. Already Remove"}
            else:
                return {"status": "failed", "msg": f"Remote Service {self.service_name} failed" + str(e)}

    def start_service(self):
        # run_as_admin()
        try:
            with self.lock:
                win32serviceutil.StartService(self.service_name)

                return {'status': 'success', 'msg': f'Start Service {self.service_name} successful.'}
        except Exception as e:
            if '(1060' == str(e).split(",")[0]:     # (1060, 'GetServiceKeyName', '指定的服务未安装。')
                return {"status": "failed", "msg": f"Start Service {self.service_name} failed. Not Installed"}
            elif '(1056' == str(e).split(",")[0]:   # 服务已经启动
                return {"status": "success", "msg": f"Start Service {self.service_name} failed. Already started."}
            else:
                return {"status": "failed", "msg": f"Start Service {self.service_name} failed." + str(e)}

    def stop_service(self):
        # run_as_admin()
        try:
            with self.lock:
                win32serviceutil.StopService(self.service_name)
                # 没有的请情况下，直接判断停止成功
                return {"status": "success", "msg": f"Stop Service {self.service_name} successful."}
        except Exception as e:
            if '(1060' == str(e).split(",")[0]:     # (1060, 'GetServiceKeyName', '指定的服务未安装。')
                return {"status": "failed", "msg": f"Stop Service {self.service_name} failed. Not Installed"}
            elif '(1062' == str(e).split(",")[0]:
                return {"status": "failed", "msg": f"Stop Service {self.service_name} failed. Not Started"}
            elif '(1061' == str(e).split(",")[0]:   # 服务无法在此时接受控制信息, 服务启动了，在运行，然后不断的点重启，开关，nginx进程就一直在那
                os.system(f"taskkill /F /IM {self.bin_name} ")
                return {"status": "success", "msg": f"Stop Service {self.service_name} successful."}
            else:
                return {"status": "failed", "msg": f"Stop Service {self.service_name} failed." + str(e)}

    def restart_service(self):
        # run_as_admin()
        stop_result = self.stop_service()
        # stop_status = self.get_service_status()
        # if stop_status['status'] == 'running':
        #     self.stop_service()
        start_result = self.start_service()
        return {"status": start_result["status"], "msg": start_result["msg"].replace("Start Service", "Restart Service")}

    def get_service_status(self):
        try:
            status = win32serviceutil.QueryServiceStatus(self.service_name)
            state = status[1]
            if state == win32service.SERVICE_RUNNING:
                return {"status": "running", "msg": f"Get Service {self.service_name} status successful. Running."}
            elif state == win32service.SERVICE_STOPPED:
                return {"status": "stopped", "msg": f"Get Service {self.service_name} status successful. Stopped."}
            elif state == win32service.SERVICE_PAUSED:
                return {"status": "paused", "msg": f"Get Service {self.service_name} status successful. Paused."}
            else:
                return {"status": "failed", "msg": f"Get Service {self.service_name} status failed. Unknown State.", "debug_msg": str(status)}
        except Exception as e:
            if '(1060' == str(e).split(",")[0]:     # (1060, 'GetServiceKeyName', '指定的服务未安装。')
                return {"status": "failed", "msg": f"Get Service {self.service_name} status failed. Not Installed"}
            else:
                return {"status": "failed", "msg": f"Get Service {self.service_name} status failed." + str(e)}

    def install_service_by_nssm(self, ):
        """ 通过 nssm 的方式注册服务 """
        if not self.nssm_path:
            raise ValueError("尚未指定 nssm 二进制文件路径, 注册服务失败")
        if not os.path.exists(self.nssm_path):
            raise FileNotFoundError("指定的 nssm 的二进制文件不不存在, 注册服务失败")
        if not os.path.isfile(self.nssm_path):
            raise ValueError("指定的 nssm 并非二进制文件, 注册服务失败")

        command = f'"{self.nssm_path}" install "{self.service_name}" "{self.binary_path}"' + '' if not self.binary_args else self.binary_args

        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output, error = result.stdout, result.stderr

        if 'installed successfully' in output:
            return {"status": "success", "msg": f"Install Service {self.service_name} successful."}
        else:
            return {"status": "failed", "msg": f"Install Service {self.service_name} failed." + str(output)}


# 示例：使用多线程调用服务操作
def manage_service_in_thread(service_manager, action):
    if action == 'start':
        result = service_manager.start_service()
    elif action == 'stop':
        result = service_manager.stop_service()
    elif action == 'restart':
        result = service_manager.restart_service()
    elif action == 'install':
        result = service_manager.install_service()
    elif action == 'uninstall':
        result = service_manager.uninstall_service()
    else:
        result = {"status": "failed", "msg": "无效的行动。"}

    return result

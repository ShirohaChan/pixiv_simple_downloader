from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QCoreApplication, QTimer, QByteArray
from PyQt5.QtWebEngineCore import QWebEngineHttpRequest
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


# 用qt_web_engine制作的一个浏览器
class WebWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(WebWindow, self).__init__(*args, **kwargs)

        self.refresh_count = None
        self.webview = QWebEngineView()
        self.setCentralWidget(self.webview)

        # 连接cookieAdded信号到槽函数
        profile = QWebEngineProfile.defaultProfile()
        profile.cookieStore().cookieAdded.connect(self.handleCookieAdded)

        # 访问一个网页
        request = QWebEngineHttpRequest(QtCore.QUrl("https://www.pixiv.net"))
        request.setHeader(QByteArray.fromPercentEncoding("Accept-Language".encode()),QByteArray.fromPercentEncoding("zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6".encode()))
        self.webview.load(request)
        # 添加变量存储cookie
        self.cookies = {}
        # 规定只获取'PHPSESSID'的值
        self.required_cookies = ["PHPSESSID"]

    # 删除cookie
    def delete_cookies(self):
        profile = QWebEngineProfile.defaultProfile()
        profile.clearAllVisitedLinks()
        profile.clearHttpCache()
        profile.cookieStore().deleteAllCookies()

    # cookie过滤
    def handleCookieAdded(self, cookie):
        # 获取cookie的名称和值
        name = cookie.name().data().decode()
        value = cookie.value().data().decode()
        # 判断获取到的cookie名称是否与required_cookies一致
        if name == 'PHPSESSID':
            # 只保留最后一个值
            self.cookies[name] = [value]
            # 如果获取完cookie就检测是否已经登录
            QTimer.singleShot(1000, self.check_login_status)

    # 退出函数
    def Quit(self):
        QCoreApplication.quit()

    # 检查用户是否已经登录
    def check_login_status(self):
        # 检查登录状态的JavaScript代码
        js = """
            function checkLoginStatus() {
                // 检查网页中是否存在下拉菜单按钮
                var loginStatusElement = document.querySelector("pixiv-icon[name='16/Menu']");
                if (loginStatusElement) {
                    return true;
                } else {
                    return false;
                }
            }
            checkLoginStatus();
        """
        # 发送测试状态至下一个函数
        self.webview.page().runJavaScript(js, self.on_login_status_checked)

    # 判断登录的后续：已登：退出；没登：1s后在检测
    def on_login_status_checked(self, is_logged_in):

        if is_logged_in:
            # 如果用户已经登录，则1s后关闭程序
            QTimer.singleShot(1000, self.Quit)
        elif not is_logged_in:
            # 如果用户尚未登录，则1s后再次检查登录状态
            QTimer.singleShot(1000, self.check_login_status)

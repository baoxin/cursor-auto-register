from DrissionPage import ChromiumOptions, Chromium
import sys
import os
from dotenv import load_dotenv
from logger import info

load_dotenv()


class BrowserManager:
    def __init__(self):
        self.browser = None

    def init_browser(self):
        """初始化浏览器"""
        co = self._get_browser_options()
        self.browser = Chromium(co)
        return self.browser

    def _get_browser_options(self):
        """获取浏览器配置"""
        co = ChromiumOptions()

        # 设置浏览器路径 - 添加这段代码
        browser_path = os.getenv("BROWSER_PATH")
        if not browser_path and sys.platform == "win32":
            # 仅在Windows系统下尝试常见的浏览器路径
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    browser_path = path
                    info(f"自动找到浏览器路径: {browser_path}")
                    break

            if not browser_path:
                info("未找到浏览器路径，请在.env文件中设置BROWSER_PATH环境变量")

        if browser_path:
            co.set_browser_path(browser_path)

        try:
            extension_path = self._get_extension_path()
            co.add_extension(extension_path)
        except FileNotFoundError as e:
            info(f"警告: {e}")

        co.set_user_agent(
            os.getenv(
                "BROWSER_USER_AGENT",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            )
        )
        co.set_pref("credentials_enable_service", False)
        co.set_argument("--hide-crash-restore-bubble")
        proxy = os.getenv("BROWSER_PROXY")
        if proxy:
            co.set_proxy(proxy)

        # 禁用自动化特征（关键参数）
        co.set_argument("--disable-blink-features=AutomationControlled")
        co.set_argument("--disable-features=AutomationControlled")
        co.set_argument("--disable-automation-extension")

        # 随机化指纹参数
        co.set_pref("webgl.vendor", "NVIDIA Corporation")
        co.set_pref(
            "webgl.renderer",
            "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0)",
        )
        co.set_pref("navigator.plugins.length", 5)
        co.set_pref("navigator.hardwareConcurrency", 8)

        # 覆盖自动化特征（关键）
        co.set_pref("dom.webdriver.enabled", False)
        co.set_pref("useAutomationExtension", False)

        # 设置时区参数
        co.set_argument("--timezone=Asia/Shanghai")
        co.set_pref("timezone.override", "Asia/Shanghai")

        # 设置更真实的屏幕参数
        co.set_pref("screen.width", 1920)
        co.set_pref("screen.height", 1080)
        co.set_pref("screen.pixelDepth", 24)
        co.auto_port()
        co.headless(
            os.getenv("BROWSER_HEADLESS", "True").lower() == "true"
        )  # 生产环境使用无头模式

        # Mac 系统特殊处理
        if sys.platform == "darwin" or sys.platform == "linux":
            co.set_argument("--no-sandbox")
            co.set_argument("--disable-gpu")

        return co

    def _get_extension_path(self):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "turnstilePatch")

        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "turnstilePatch")

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")
        info(f"插件路径: {extension_path}")
        return extension_path

    def quit(self):
        """关闭浏览器"""
        if self.browser:
            try:
                self.browser.quit()
            except:
                pass

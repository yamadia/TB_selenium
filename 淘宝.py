import time
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class SeleniumTB:
    """
        初始化浏览器驱动
        :param start_url: 浏览器驱动路径 (如ChromeDriver)
        :param headless: 是否使用无头模式
        :param implicit_wait: 隐式等待时间(秒)
    """
    def __init__(self, executable_path, headless=False, implicit_wait=10):
        self.keyword = "茅台"
        self.account = ''
        self.password = ''
        self.cookies = {}
        # 设置浏览器选项
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument("--disable-blink-features=AutomationControlled")  # 禁用自动化控制提示
        options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 隐藏"自动化控制"提示
        options.add_experimental_option("useAutomationExtension", False)   # 禁用自动化扩展
        options.add_argument("--disable-popup-blocking")  # 添加弹窗阻止禁用
        try:
            if executable_path:
                service = ChromeService(executable_path=executable_path)

                self.driver = webdriver.Chrome(service=service, options=options)
                # 设置隐式等待时间为 10 秒
                self.driver.implicitly_wait(implicit_wait)

            else:
                print("驱动地址为空")

        except Exception as e:
            print(f"初始化浏览器驱动失败: {e}")


    def wait_for_element(self, locator, timeout=10):
        """
            显式等待元素出现
            :param locator: 元素定位器 (By.XPATH, By.ID等)
            :param timeout: 超时时间(秒)
            :return: WebElement对象或None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.ID, locator)))
            return element
        except TimeoutException as e:
            print(f"等待元素超时: {locator}")
            return None


    def search_keyword(self):
        # 先等待输入框可见并可点击
        input_element = WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#q")))
        input_element.click()
        input_element.send_keys(self.keyword)
        self.driver.implicitly_wait(5)
        input_element.send_keys(Keys.ENTER)

    def switch_to_iframe(self):
        # 检查是否有iframe
        try:
            iframes = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
            )
            iframe = self.driver.find_element(By.CSS_SELECTOR, "body > div.J_MIDDLEWARE_FRAME_WIDGET").find_element(
                By.TAG_NAME, "iframe")

            print("iframe的值：", iframe)
            self.driver.switch_to.frame(iframe)
            return True

        except:
            print("发生报错！")
            return False

    def setcookie(self, cookies):
        self.cookies = cookies


    def getcookie(self):
        return self.cookies


    def login(self):

        account_input_ele = self.driver.find_element(By.CSS_SELECTOR, "#fm-login-id")
        account_input_ele.click()
        account_input_ele.clear()
        account_input_ele.send_keys(self.account)
        password_input_ele = self.driver.find_element(By.CSS_SELECTOR, "#fm-login-password")
        password_input_ele.click()
        password_input_ele.clear()
        password_input_ele.send_keys(self.password)

        login_button_ele = self.driver.find_element(By.CSS_SELECTOR, "#login-form > div.fm-btn > button")
        login_button_ele.click()
        time.sleep(10)
        self.driver.refresh()
        # try:
        #     cookies = self.driver.get_cookies()
        #     print("当前cookies：", cookies)
        #     self.setcookie(cookies)
        # except:
        #     print("还没登陆，或者登录已过期！")

    def gradual_scroll_to_element(self, element_locator, max_attempts=30):
        """
        从快到慢地滚动页面，直到找到指定元素

        参数:

            element_locator: 元素定位器 (By.XPATH, By.ID等)
            max_attempts: 最大尝试次数

        返回:
            WebElement对象或None(如果未找到)
        """
        found_element = None
        attempt = 0

        while not found_element and attempt < max_attempts:
            try:
                # 尝试查找元素
                found_element = self.driver.find_element(*element_locator)
                if found_element.is_displayed() and found_element.is_enabled():
                    return found_element
                else:
                    found_element = None
            except Exception as e:
                print(f"滑动滚动条出错: {e}")
                pass

            # 计算滚动距离和速度 (从快到慢)
            scroll_distance = max(500 - attempt * 15, 50)  # 滚动距离逐渐减小
            scroll_pause = min(0.1 + attempt * 0.05, 1.5)  # 暂停时间逐渐增加

            # 执行滚动
            self.driver.execute_script(f"window.scrollBy(0, {scroll_distance});")

            # 等待一段时间
            time.sleep(scroll_pause)
            attempt += 1

        return None

    def scroll_and_click(self, element_locator, timeout=30):
        """
        滚动页面直到元素可见并可点击，然后点击它

        参数:
            driver: WebDriver实例
            element_locator: 元素定位器 (By.XPATH, By.ID等)
            timeout: 超时时间(秒)
        """
        try:
            # 首先尝试直接等待元素出现(可能已经在视图中)
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(element_locator)
            )
            element.click()
            return
        except Exception as e:
            # 如果直接等待失败，则开始渐进式滚动
            print(f"等待元素出错: {e}")
            pass

        # 使用渐进式滚动查找元素
        element = self.gradual_scroll_to_element(driver, element_locator)

        if element:
            try:
                # 确保元素可点击
                element = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(element_locator)
                )

                # 使用ActionChains更精确地点击
                actions = ActionChains(self.driver)
                actions.move_to_element(element).pause(0.5).click().perform()
            except Exception as e:
                print(f"点击元素时出错: {e}")
                # 作为后备方案，使用JavaScript点击
                self.driver.execute_script("arguments[0].click();", element)
        else:
            raise Exception(f"在指定时间内未找到可点击元素: {element_locator}")

    def parse_data(self):

        self.search_keyword()

        # # 等待新窗口出现并切换
        WebDriverWait(self.driver, 20).until(lambda d: len(d.window_handles) > 1)
        self.driver.switch_to.window(self.driver.window_handles[1])

        # 等待新页面完全加载
        WebDriverWait(self.driver, 20).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        if self.switch_to_iframe():
            self.login()


        # 等待数据父元素出现
        parent_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "content_items_wrapper"))
        )
        # 获取所有子元素（假设每个商品是一个直接子元素）
        items = parent_element.find_elements(By.XPATH, './*')
        print("元素：", items)
        # 遍历每个商品元素
        for index, item in enumerate(items, 1):

            try:
                # 获取商品标题
                title = item.find_element(By.XPATH,
                                          './a[starts-with(@id, "item_id")]/div/div[1]/div[3]/div/span'
                                          ).text

                # 获取商品价格
                price = item.find_element(By.XPATH,
                                          './a[starts-with(@id, "item_id")]/div/div[1]/div[5]/div/div[1]/div[@class="priceInt--yqqZMJ5a"]'
                                          ).text

                # 获取购买次数
                sales = item.find_element(By.XPATH,
                                          './a[starts-with(@id, "item_id")]/div/div[1]/div[5]/div/span[@class="realSales--XZJiepmt"]'
                                          ).text

                print(f"商品 {index}:")
                print(f"标题: {title}")
                print(f"价格: {price}¥")
                print(f"购买次数: {sales}")
                print("-" * 50)

            except Exception as e:
                print(f"处理第 {index} 个商品时出错: {str(e)}")
                continue

        element_locator = (By.CSS_SELECTOR, '.next-btn.next-medium.next-btn-normal.next-pagination-item.next-next')
        self.scroll_and_click(element_locator)

        time.sleep(10)


    def scrape_page(self, url):
        try:
            self.driver.get(url)
            cookies = self.driver.get_cookies()
            print("首页cookies：", cookies)

            self.setcookie(cookies)
            print(f"成功访问: {url}")

            locator = 'q'
            element = self.wait_for_element(locator)
            if not element:
                print("页面数据未加载成功！")
                return
            self.parse_data()

        except Exception as e:
            print(f"爬取页面时出错: {e}");


    def close(self):
        """
        关闭浏览器
        """
        try:
            self.driver.quit()
            print("浏览器已关闭")
        except Exception as e:
            print(f"关闭浏览器时出错: {e}");


    def __enter__(self):
        """ 支持with语句 """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ 支持with语句 """
        self.close()


if __name__ == "__main__":
    start_url = 'https://www.taobao.com/'
    executable_path = 'G:\lwy\chromedriver\chromedriver-win64_137\chromedriver-win64\chromedriver.exe'
    # 使用with语句确保浏览器会被正确关闭
    with SeleniumTB(headless=False, executable_path=executable_path) as driver:
        # 爬取示例网站
        driver.scrape_page(start_url)
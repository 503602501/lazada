import asyncio
import tkinter

from pyppeteer import launcher

# 注意 在导入launch之前先把默认参数改了
# 去除自动化 启动参数
from pyppeteer import launch


def screen_size():
    # 使用tkinter获取屏幕大小
    import tkinter
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height

# ,'userDataDir=D:\project_demo'
# "userDataDir ":"d:\chrome", 'slowMo': 30,
async def main():
  browser = await launch({'headless': False, 'dumpio': True, 'autoClose': False,
                          'userDataDir':r'D:\chrome_temp',
                          'args': ['--no-sandbox',
                              '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                              '--disable-infobars', '--disable-popup-blocking','--disable-notifications', '--start-maximized','--ignore-certificate-errors','--disable-web-security']})

  page = await browser.createIncognitoBrowserContext()
  #await browser.newPage()

  # pages = await browser.pages();
  # page = pages[0];


  await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'  '{ webdriver:{ get: () => false } }) }')  # 本页刷新后值不变
  width, height = screen_size()
  await page.setViewport({
      "width": width,
      "height": height
  })
  # 第二步，修改 navigator.webdriver检测
  # 其实各种网站的检测js是不一样的，这是比较通用的。有的网站会检测运行的电脑运行系统，cpu核心数量，鼠标运行轨迹等等。
  # 反爬js
  js_text = """
  () =>{ 
      Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
      window.navigator.chrome = { runtime: {},  };
      Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
   }
      """
  await page.evaluateOnNewDocument(js_text)  # 本页刷新后值不变，自动执行js
  await page.goto("https://www.baidu.com", options={'timeout': 5000})
    # await browser.close()


asyncio.get_event_loop().run_until_complete(main())
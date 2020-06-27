import asyncio
import  requests
import xlsxwriter
from lxml import etree
from pyppeteer import launch

#处理导出excel的数据
def exportExcel(title, rows):
    workbook = xlsxwriter.Workbook('d:\data.xlsx')  # 创建一个Excel文件
    worksheet = workbook.add_worksheet()  # 创建一个sheet
    worksheet.write_row("A1", title)
    for index, row in enumerate(rows):
        # print(row)
        for i, value in enumerate(row):
            print(value)
            worksheet.write_string(index+1,i, value)

    workbook.close()

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
                          'args': ['--no-sandbox',
                              '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                              '--disable-infobars', '--log-level=30', '--start-maximized']})
  page = await browser.newPage()
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

  await page.goto("https://txjichuan.en.alibaba.com/productlist.html?spm=a2700.icbuShop.88.30.4baccaf8HKh7Hl",options={'timeout': 10000})

  page_text = await page.content()
  tree = etree.HTML(page_text)
  while tree.xpath( "//button[@class='next-btn next-btn-normal next-btn-medium next-pagination-item next' and not(@disabled)]"):
      div_list = tree.xpath("//div[@class='component-product-list']/div/div/div/a/@href")
      for div in div_list:
          print("https://txjichuan.en.alibaba.com" + div)
      aa = await  page.xpath("//button[@class='next-btn next-btn-normal next-btn-medium next-pagination-item next' and not(@disabled)]")

      #点击事件后等待导航加载完页面
      await asyncio.wait([
          aa[0].click(),
          page.waitForNavigation({'timeout': 30000}),
      ])

      # 等待导航加载完毕
      # await page.waitForNavigation()
      #重新获取页面，刷新树结构数据

      page_text = await page.content()
      tree = etree.HTML(page_text)
      await asyncio.sleep(3)
  print("sdf")


  # print(div_list)
  # return ;
  # await browser.close()

  # await page.waitFor(10000)
  title = ['名称', '副标题']  # 表格title
  list = ["1","bb"]
  list1 = ["2","cc"]
  data=[]
  data.append( list)
  data.append(list1)
  # exportExcel(title,data)



asyncio.get_event_loop().run_until_complete(main())

print('完毕.....')

import asyncio
import re
import os
import configparser
import  json
import datetime
import shutil
import xlsxwriter
from lxml import etree
from pyppeteer import launch
from pyppeteer.connection import Connection
from pyppeteer.launcher import connect

#处理导出excel的数据
def exportExcel(title, rows,path):
    workbook = xlsxwriter.Workbook(path)  # 创建一个Excel文件
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

def correct_title(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title
# 设置保存地址
def mkdir( path ):
    path = 'd:/A'
    if not os.path.isdir(path):
        os.makedirs(path)  #


def deleteTemp(path):
    rootdir = path # 选取删除文件夹的路径,最终结果删除img文件夹
    if not os.path.exists(rootdir):
        print("路径不存在:"+path)
        return

    filelist = os.listdir(rootdir)  # 列出该目录下的所有文件名z
    for f in filelist:
        filepath = os.path.join(rootdir, f)  # 将文件名映射成绝对路劲
        if os.path.isfile(filepath):  # 判断该文件是否为文件或者文件夹
           os.remove(filepath)  # 若为文件，则直接删除
           # print(str(filepath) + " removed!")
        elif os.path.isdir(filepath):
           shutil.rmtree(filepath, True)  # 若为文件夹，则删除该文件夹及文件夹内所有文件
           # print("dir " + str(filepath) + " removed!")
    # shutil.rmtree(rootdir, True)  # 最后删除img总文件夹
    print("浏览器缓存清理成功")


# ,'userDataDir=D:\project_demo'
# "userDataDir ":"d:\chrome", 'slowMo': 30,
def readFile(path):
    data = []
    fp = open(path, "r")
    for line in fp.readlines():
        if line.strip()=='':
            continue ;
        data.append(line)
    fp.close()
    return data

# 请求过滤
async def request_check(req):
    # print(req)
    if req.resourceType in ['image', 'media', 'eventsource', 'websocket']:
        await req.abort()
    else:
        await req.continue_()

async def intercept_response(res):
    resourceType = res.request.resourceType
    if resourceType in ['xhr', 'fetch']:
        resp = await res.text()
        # print(resp)




async def main():

  config = configparser.ConfigParser()
  config.sections()
  config.read("config.ini",encoding='utf-8')
  config.sections()
  CHROME_PATH = config.get("baseconf", "chrome_path")
  CHROME_USER_TEMP = config.get("baseconf", "chrome_user_temp")
  EXPORT_PATH = config.get("baseconf", "export_path")
  READ_FILE_PATH = config.get("baseconf", "read_file_path")


  deleteTemp(CHROME_USER_TEMP)
  # browser = await launch({'headless': False,'devtools':True,'args': ['--no-sandbox', '--enable-automation','--disable-setuid-sandbox'],'executablePath': 'D:\金蚁软件\install\chrome\chrome.exe'})

  browser = await connect({'headless': False,'dumpio':True,'logLevel':3,'browserWSEndpoint': 'ws://localhost:9222/devtools/browser/e852519a-a9ea-45e2-9d06-cbf3bb12e13e'})

  # browser = await launch({'headless': False,  'dumpio': True, 'autoClose': False,
  #                         'executablePath': "C:\\Users\\rocky\\AppData\\Local\\Chromium\\Application\\chrome.exe",
  #                         'userDataDir':CHROME_USER_TEMP,
  # # # "--load-extension={}".format(chrome_extension_path),  设置插件
  #                         'args': ['--no-sandbox', '--disable-setuid-sandbox',
  #                             # '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
  #                             '--disable-infobars', "--log-level=3",'--no-first-run','--disable-notifications', '--start-maximized','--ignore-certificate-errors','--disable-web-security']})


  # 无痕模式，未解决打开两个浏览器 '--no-first-run',
  browser_context = await browser.createIncognitoBrowserContext()
  # pages = await browser_context.pages();
  # page = await browser_context.newPage();
  # browser_context = await browser.createIncognitoBrowserContext()
  # page = await browser.newPage()

  pages = await browser.pages();
  page = pages[0] ;

  await page.setRequestInterception(True)
  page.on('request', request_check)
  # page.on('response', intercept_response)

  await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'  '{ webdriver:{ get: () => false } }) }')  # 本页刷新后值不变

  width, height = screen_size()
  await page.setViewport({
      "width": width,
      "height": height
  })
  # 第二步，修改 navigator.webdriver检测
  # 其实各种网站的检测js是不一样的，这是比较通用的。有的网站会检测运行的电脑运行系统，cpu核心数量，鼠标运行轨迹等等。
  # 反爬js       Object.defineProperties(navigator,{ webdriver:{ get: () => false } });
  js_text = """
  () =>{ 
      window.navigator.chrome = { runtime: {},  };
      Object.defineProperties(navigator,'webdriver',{ get: () => false } );
      Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
      Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });
   }
      """
  await page.evaluateOnNewDocument(js_text)  # 本页刷新后值不变，自动执行js

  data = []
  urls = readFile(READ_FILE_PATH)
  for url  in urls:
      start = datetime.datetime.now()
      try:
          # page.goto(url,{'waitUntil':'load'})
          await page.goto(url, options={'timeout': 10000})
          # await page.evaluate() evaluateOnNewDocument('')
          # await page.waitForNavigation()
          # await page.waitFor(5)
      except Exception as r:
          print(r)
          print("访问链接超时:"+url)

      try:

          # start = datetime.datetime.now()
          await  page.waitForXPath("//img[@class='pdp-mod-common-image gallery-preview-panel__image']",timeout=3000)
          # await  page.waitFor(5000)
          # end = datetime.datetime.now()
          # print((end - start).seconds)  #秒

      except Exception as e:
          print(e)
          print("元素等待超时"+url)
          page_text = await page.content()
          # if page_text.find("dp-mod-common-image gallery-preview-panel__image") !=-1:
          #     print("存在"+page_text)
          # else :
          #     print(page_text)
          urls.append(url)
          continue

      page_text = await page.content()
      tree = etree.HTML(page_text)

      title =  tree.xpath("//div[@class='pdp-product-title']/div/span/text()")[0]

      bigUrl = tree.xpath("//img[@class='pdp-mod-common-image gallery-preview-panel__image']/@src")[0]
      bigUrl ='https:'+ bigUrl.replace('_340x340q80.jpg_.webp','')

      price = tree.xpath("//div[@class='pdp-product-price']/span/text()")[0]

      b = re.search('skuBase(.*)skus', page_text)
      skus = b.group(0)
      skus = skus.replace("skuBase\":","")
      skus = skus.replace(",\"skus", "}")
      print(skus)
      jsonData = json.loads(skus)

      color=''
      if len(jsonData['properties']) > 0:
          colorValues = jsonData['properties'][0]['values']
          color = ",".join(map(lambda s: s["name"] ,colorValues))

      size=''
      if len(jsonData['properties']) >1 :
         if  (jsonData['properties'][1]['values']) ==1:
             sizeValues =  jsonData['properties'][1]['values'][0]["value"]

         else :
             sizeValues = jsonData['properties'][1]['values']

         size  =  ",".join(map(lambda s: s["name"].replace('Int:','').replace('US:8','') ,sizeValues))
      #bloger[0].xpath('string(.)').strip() 获取标签下的所有的内容


      #中文的代码块, bytes 转成 string
      chineseE = tree.xpath("//div[@class ='html-content detail-content']")
      if len(chineseE) >0 :
          chineseE=chineseE[0]
          chineseHtml = etree.tostring(chineseE, encoding='utf-8').decode()

          # b = re.search('<img(.*)>', chineseHtml)
          # for g in b.groups() :
          #     print(g)
          # skus = b.group(0)

      else :
          chineseHtml=""
      # chineseStr = etree.tostring(chineseHtml, encoding='utf-8').decode()
      chineseHtml = chineseHtml.replace('<br/>','<br/>\n')
      dr = re.compile(r'<[^>]+>', re.S)
      chineseStr = dr.sub('', chineseHtml)

      # chineseStr = chinese.xpath('string(.)')

      chineseHtml = '\n'.join( map(lambda s: s.strip() if len(s.strip()) == 0 else '<div>' + s + '</div>', chineseStr.splitlines()))
      # print(chineseHtml)
      # chineseStr = "".join( map( lambda s:s,chinese))
      # print(chineseStr)
      detail = tree.xpath("//div[@class='pdp-product-detail']")[0]
      imgs = detail.xpath('.//img/@src')
      detailsStr = ','.join(imgs)  # 详情的图片

      # print(chineseHtml)

      list  = [url,title,bigUrl,price,size,color,chineseHtml,chineseStr,detailsStr]
      # print(tree.xpath("//span[@class='pre-inquiry-price' or @class='priceVal' ]") )
      # print(tree.xpath("//ul[@id='ladderPrice']/li[1]/div[@class='ma-spec-price ma-price-promotion']/span/@title"))
      # print(tree.xpath("//ul[@id='ladderPrice']/li[1]/div[@class='ma-spec-price ma-price-promotion']/text()"))
      # print("标题："+title)
      # 主图的链接
      # main_imgs =tree.xpath("//ul[@class='inav util-clearfix']/li/div/a[@rel='nofollow']/img/@src")

      # page_height = await page.evaluate(pageFunction='document.body.scrollHeight ', force_expr=True)
      data.append(list)
      end = datetime.datetime.now()
      print("耗时："+str((end - start).seconds) ) #秒

  title = ['链接','标题','主图链接','价格','尺码','颜色','代码','文字','详情图片链接']
  exportExcel(title, data,EXPORT_PATH)

  await page.close()
  await browser.close()
  print("运行完毕。。。。")

  # await page.waitFor(2000)
  # deleteTemp(CHROME_USER_TEMP)

asyncio.get_event_loop().run_until_complete(main())

print('***************运行完毕*********************')

import asyncio
import re
import os
import urllib
import time
import datetime
import shutil
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
    filelist = []
    rootdir = path # 选取删除文件夹的路径,最终结果删除img文件夹
    filelist = os.listdir(rootdir)  # 列出该目录下的所有文件名
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

CHROME_USER_TEMP = "D:\chrome_temp"
async def main():

  deleteTemp(CHROME_USER_TEMP)

  browser = await launch({'headless': False, 'dumpio': True, 'autoClose': False,
                          'userDataDir':r'D:\chrome_temp',
  # "--load-extension={}".format(chrome_extension_path),  设置插件
                          'args': ['--no-sandbox',
                              '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
                              '--disable-infobars', '--disable-notifications', '--start-maximized','--ignore-certificate-errors','--disable-web-security']})

  # 无痕模式，未解决打开两个浏览器
  browser_context = await browser.createIncognitoBrowserContext()
  pages = await browser_context.pages();
  # page = await browser_context.newPage();


  pages = await browser.pages();
  page = pages[0] ;

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

  with open("file.txt", "r") as f:
      urls = f.readlines()
      for url  in urls:

          try:
              # page.goto(url,{'waitUntil':'load'})
              await page.goto(url, options={'timeout': 1000})
              await page.waitForNavigation()
              # await page.waitFor(5)
          except Exception as r:
              print(r)
              print("访问链接超时:"+url)


          try:

              start = datetime.datetime.now()
              await  page.waitForXPath("//h1[@class='ma-title']",timeout=5000)
              # await  page.waitFor(5000)
              end = datetime.datetime.now()
              # print((end - start).seconds)  #秒

          except Exception as e:
              print(e)
              continue
          page_text = await page.content()

          # await  page.waitFor(5000)


          # print(page_text.find("ma-title"))


          # print(page_text)
          tree = etree.HTML(page_text)

# 获取页面的内容 content = await page.evaluate('document.body.textContent', force_expr=True)
          # 重新加载当前页面
          # await page.reload()

          # check = tree.xpath("//div[@class='ma-price-wrap']")
          # check[0].click()
          # await page.waitFor(1)
          # if len(price)==0 :
          #     print("价格不存在")
          #     page_text = await page.content()
          #     tree = etree.HTML(page_text)
          #     print(page_text)

          title = correct_title (tree.xpath("//h1[@class='ma-title']/text()")[0] )
          # print("价格1" )
          # print(tree.xpath("//span[@class='pre-inquiry-price']/text()") )
          # print("价格2")
          # print(tree.xpath("价格2"+"//span[@class='priceVal' ]/text()"))
          price = tree.xpath("//span[@class='pre-inquiry-price' or @class='priceVal' ]/text()")+ tree.xpath("//span[@class='ma-ref-price']/span/text()")+tree.xpath("//ul[@id='ladderPrice']/li[1]/div[@class='ma-spec-price ma-price-promotion']/span[@class='priceVal']/text()")

          if len(price)==0 :
              print("价格为空:"+url)
              continue
          # print(tree.xpath("//span[@class='pre-inquiry-price' or @class='priceVal' ]") )
          # print(tree.xpath("//ul[@id='ladderPrice']/li[1]/div[@class='ma-spec-price ma-price-promotion']/span/@title"))
          # print(tree.xpath("//ul[@id='ladderPrice']/li[1]/div[@class='ma-spec-price ma-price-promotion']/text()"))
          # print("标题："+title)
          # 主图的链接
          main_imgs =tree.xpath("//ul[@class='inav util-clearfix']/li/div/a[@rel='nofollow']/img/@src")
          for index, img in enumerate(main_imgs):
              if img.find('_50x50')<=0:
                  continue
              suffix = img.rsplit('.',1)[1]
              if suffix.lower()=="jpg":
                  img = "https:" + img.replace('_50x50.jpg', '')
              else :
                  img = "https:" + img.replace('_50x50.png', '')

              path = 'd:/AAA/' + title + "/主图-"+price[0]+"/"
              if not os.path.isdir(path):
                  os.makedirs(path)

              urllib.request.urlretrieve(img,  ('{}{}.'+suffix+'').format(path, index))

          #页面滚动到底部
          # await page.evaluate('window.scrollBy(0, window.innerHeight)')
          # await page.evaluate("{window.scrollBy(0, document.body.scrollHeight);}")
          page_height = await page.evaluate(pageFunction='document.body.scrollHeight ', force_expr=True)
          scrolls =int(  page_height/800)
          await page.evaluate("{window.scrollBy(0, document.body.scrollHeight);}")
          # for value in range(1,scrolls):
          #     await page.evaluate("{window.scrollBy(0,  "+str(value*800) +");}")
          #     print("page_height:" + str(value*800) )
          #     await page.waitFor(1000)
          #     page_height = await page.evaluate(pageFunction='document.body.scrollHeight ', force_expr=True)
          #     print("page_height:" + str(page_height))

          # 详情图片的链接
          detail_imgs = tree.xpath("//noscript/parent::p/img/@data-src") +tree.xpath("//noscript/parent::span/img/@src")

          for index,img in enumerate(detail_imgs):
              if(img.find('img-placeholder.png'))>0 :
                  continue
              img = "https:"+img

              path = 'd:/AAA/'+title+"/详情/"
              if not os.path.isdir(path):
                  os.makedirs(path)
              try :
                 urllib.request.urlretrieve(img, '{}{}.jpg'.format(path, index))
              except Exception as e:
                  print(e)
                  print("失败下载："+img)

      await page.waitFor(5000)
      await page.close()
      await browser.close()

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

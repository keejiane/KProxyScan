# KProxyScan
## 简介
### 工作机制
  通过浏览器代理的方式，采集需要的请求，并在后台进行漏洞检测，代理和漏洞检测模块完全分离，不影响代理速度。
  
### 支持漏洞类型
  目前支持SQL注入、XSS、DOM XSS、重定向等最常见的漏洞，检测模块可自行扩展。
  
### 系统特点
  1、完善的代理模块，支持HTTPS  
  2、支持伪静态SQL注入检测  
  3、使用Celery实现异步分发漏洞检测，可分布式部署  
  4、支持URL去重，避免重复检测，并可存储检测自定义URL  
  5、支持前端展示分析
  
### 部署
  1、Python版本：2.7  
  2、安装sqlmap  
  3、安装MITMProxy 0.16  
  https://github.com/mitmproxy/mitmproxy/tree/v0.16  
  4、安装casperjs  
  http://docs.casperjs.org/en/latest/installation.html  
  5、安装Python依赖模块  
  ```
  python -r ./Web/requirements.txt
  python -r ./requirements.txt
  ```
  
 ### 启动
  1、启动sqlmapapi  
  ```
  python sqlmapapi.py -s
  ```  
  2、启动MongoDB、Redis、Mysql服务器  
  
  3、启动合子任务模块  
  ```
  sh Task_sqli.sh
  sh ...
  ...
  ```  
  4、启动代理模块  
  修改config中代理地址端口，执行  
  ```
  python proxy_plugin.py
  ```  
  浏览器设置端口代理地址的时候要填写真实主机地址，不要填写127.0.0.1或者localhost，有可能出现bug，原因不详
  
  5、任务执行  
  ```
  python taskDispatch.py
  ```
  
  ### 查看Web页面
  1、查看Celery Web管理界面  
  ```
  flower --broker=redis://127.0.0.1:6379/0 --address=127.0.0.1
  ```
  
  2、查看Web管理界面
  ```
  python ./Web/run.py
  ```
  
  

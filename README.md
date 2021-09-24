# README

## 天天基金的API

天天基金网历史净值数据的页面地址是
```
http://fund.eastmoney.com/f10/F10DataApi.aspx?type=lsjz&code=110022&sdate=2018-02-22&edate=2018-03-02&per=20
```
参数说明如下：

type 类型，历史净值用lsjz表示
code 基金代码，六位数字
sdate 开始日期，格式是yyyy-mm-dd
edate 结束日期，格式是yyyy-mm-dd
per 一页显示多少条记录
为了便于分析页面数据，要保证所选择日期范围内的净值在一个页面全部显示，可以把per设成很大的值，比如65535。

返回的页面数据比较简单，只有一个历史净值的表格和总记录数，总页数和当前页数：[查看示例](https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code=000051&sdate=2018-01-22&edate=2018-03-02&per=20)。

用BeautifulSoup库的findAll找到tbody（表格主体）标签，然后在里面找tr（表格中的一行）标签，单元格内容是：

```
td:nth-of-type(1)（第1个单元格）是净值日期
td:nth-of-type(2)（第2个单元格）是单位净值
td:nth-of-type(3)（第3个单元格）是累计净值
td:nth-of-type(4)（第4个单元格）是日增长率
```

## 食用方法

### Requirements

- pandas
- requests
- bs4

`auto_invest_benchmark.py`是用来跑周几定投对应的收益的=-=，输入基金代码fund_code（比如000051）即可。

```shell
python auto_invest_benchmark.py --fund_code=[Your fund code]
```

`fund_nav.py` 获取某个基金的数据，作为DataFrame，最后保存到csv文件。

```shell
python fund_nav.py --fund_code=[Your fund code] --start_date=[YYYY-MM-DD] --end_date=[YYYY-MM-DD] --save=[true|false]
```

## 一些指数基金傻瓜式定投结果

|Fund code|基金名称|1年最佳定投日|3年最佳定投日|5年最佳定投日|
|:--:|:--:|:--:|:--:|:--:|
|000051|华夏沪深300ETF联接A|周五|周一|周五|
|217027|招商央视财经50指数A|周五|周一|周五|
|011613|华夏科创50联接C|周五|暂无|暂无|
|481012|工银深证红利ETF联接A|周四|周四|周五|
|006479|广发纳斯达克100指数C(QDII)|周一|周一|暂无|
|008764|天弘越南市场股票C(QDII)|周一|暂无|暂无|
|270023|广发全球精选股票(QDII)|周二|周一|周二|

## TO DO

咸鱼时间写的，等有空了再看看有什么新的想法吧。


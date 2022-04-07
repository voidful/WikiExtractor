# 📂 WikiExtractor 💡

Dumping hole wiki content,which can :

- clean unused symbol,mark,label
- extract knowledge - synonym,concept,relationship

這是一個 wiki 的預處理工具，可以:

- 清理 wiki 中沒有用的内容：標簽，符號...
- 提取出一些有用的知識：同義詞，關係，翻譯

## Usage

How to use:

```
pip install wikiext
wikiext -h
usage: wikiext [-h] [--lang LANG]
               [--dump {entity, redirect_pair,langlink,category,articles,all} [{redirect_pair,langlink,category,articles,all} ...]]
               [--savedir SAVEDIR] [--type {csv,dict}] [--s2t]

optional arguments:
  -h, --help            show this help message and exit
  --lang LANG           default:zhwiki, from
                        https://dumps.wikimedia.org/backup-index-bydb.html
  --dump {entity, redirect_pair,langlink,category,articles,all} [{redirect_pair,langlink,category,articles,all} ...]
                        select what to extract
  --savedir SAVEDIR     save dir, default /dump_result
  --type {csv,dict}
  --s2t                 simplify chinese to traditional chinese

```

# Function

### init

```
from wiki import WikiExt
wiki = WikiExt(language_source="zh_yuewiki", s2t=False)
```

Arguments

- `language_source(String)` : example:"zhwiki",all of the code can find it on https://dumps.wikimedia.org/backup-index-bydb.html
- `s2t(Boolean)` : translate all text to traditional or not

### dump_articles(outfile, type="csv")

Arguments

- `outfile(String)` : name of output file
- `type(String)` : csv or text
  Result

```
csv :
數學,"歐幾裏得，西元前三世紀的古希臘數學家，現在被認為是幾何之父，此畫為拉斐爾的作品《雅典學院》。
數學是利用符號語言研究數量、結構、變化以及空間等概念的一門學科，從某種角度看屬於形式科學的一種。數學透過抽象化和邏輯推理的使用，由計數、計算、量度和對物體形狀及運動的觀察而產生。數學家們拓展這些概念，為了公式化新的猜想以及從選定的公理及定義中建立起嚴謹推導出的定理。
......
text :
數學
歐幾裏得，西元前三世紀的古希臘數學家，現在被認為是幾何之父，此畫為拉斐爾的作品《雅典學院》。
數學是利用符號語言研究數量、結構、變化以及空間等概念的一門學科，從某種角度看屬於形式科學的一種。數學透過抽象化和邏輯推理的使用，由計數、計算、量度和對物體形狀及運動的觀察而產生。數學家們拓展這些概念，為了公式化新的猜想以及從選定的公理及定義中建立起嚴謹推導出的定理。

```

### dump_redirect_pair(outfile, type)

get all redirect pair
Arguments

- `outfile(String)` : name of output file
- `type(String)` : csv or dict
  Result

```
csv:
origin.redirect to
鋼の錬金術師,鋼之鍊金術師
香港仔海旁道,香港仔海傍道
飛機外部燈光,航行燈
螢幕八爪娛,熒幕八爪娛
司农卿,大司農
大司农卿,大司農
司農,大司農
司农,大司農
Earth 2160,地球2160
图勒凯尔姆,图勒凯尔姆省
盖勒吉利耶,盖勒吉利耶省
......
dict
鋼の錬金術師
鋼之鍊金術師
香港仔海旁道
香港仔海傍道
飛機外部燈光
航行燈
螢幕八爪娛
熒幕八爪娛
司农卿
大司農
大司农卿
大司農
司農
大司農
司农
大司農
Earth 2160
地球2160
图勒凯尔姆
图勒凯尔姆省
盖勒吉利耶
盖勒吉利耶省
```

### dump_entity(outfile, type):

Arguments

- `outfile(String)` : name of output file
- `type(String)` : csv or dict


### dump_langlink(outfile, type):

Arguments

- `outfile(String)` : name of output file
- `type(String)` : csv or dict

### dump_category(outfile, type="csv"):

use this to extract specific categories noun
Arguments

- `outfile(String)` : name of output file
- `type(String)` : csv or dict

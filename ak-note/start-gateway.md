# 啟動 gateway (research in progress)
1. 如果沒有啟動 gateway script只能取得資料，沒辦法正常下單
2. 如何啟動 gateway? (研究中) -> 用註解掉docker-compose.yaml 檔中 gateway 相關的部分就可以啟起來 gateway，但是仍然無法順利下單，懷疑是gateway裡面有某的部分有被內建的key 的設定所以下單用錯錢包地址就導致失敗，換把hyperliquild的 key交叉比對看看 -> 全部都簽名都是錯的所以錢包地址全部都錯誤
3. 使用原本default的 strategy(pure_market_making) 去測，在local跑的會失敗 (簽名一樣會亂簽) ![alt text](<2025-11-21 11_46_40-Window.png>)
4. 用乾淨的ubuntu環境去跑 default的 strategy(pure_market_making) 可以work 所以我推測可能是在哪一邊改到不可以改的東西了之類的  -> 先再弄一個全新的環境去跑跑看，交叉比對一下
5. 改用conda來準備開發環境
6. 
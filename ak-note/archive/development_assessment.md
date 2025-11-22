# 開發建倉機器人評估
1. 使用script開發我們要的建倉機器人可能可行(開發第一個hyperliquid 建倉機器人POC中)，但是開發過程中極度痛苦，而且我們不需要ui，所以這個ui對我們來說沒有加分反而是扣分
2. dubug模式啟動後如果要 stop再重新 start還沒有成功過，都只能關掉整個hummingbot後重新啟動，拖累整個開發腳步
3. hummingbot底層connector有一些限制和缺乏的功能，要補足這些功能還是要回去走交易所API再打一次，這樣就失去用hummingbot的意義了

-> 結論 先以hummingbot POC完最基礎的期現套利建倉程式在來想評估下一步和後續，scope聚焦。

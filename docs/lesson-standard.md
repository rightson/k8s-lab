# 單元、練習與實驗標準

## 每單元交付

`lessons/<id>/README.md` 記錄問題、先備、端到端模型、至少兩個關鍵機制、正常路徑、故障情境、量化與兩個合理替代方案。按需建立 manifests/、src/、exercises/、solutions/、runs/；輔助圖與解說亦放該目錄。公開文章的背景圖和機制圖隨文章提交網站 repo。

練習至少有：建立／操作、觀測／解釋、故障定位／恢復、設計變體。每題附完成條件及可核對的解答，測量題明確標示硬體與 baseline；不能只複製 YAML 當作理解驗收。

## 環境與執行

1. 記錄 OS、kernel、CPU/NUMA、RAM、設備、kubectl、Kubernetes、runtime、CNI/CSI、chart、映像 digest、feature gate 與測試拓樸；寫出與正式環境差異。
2. 全部工作在本單元的隔離環境，建立前檢查 context。清理只刪除本單元資源；避免 wildcard、刪除陌生 namespace 或使用預設 production context。
3. 指令附用途、前提、預期訊號和驗收條件；實際輸出另外保留，不預先生成「實測結果」。
4. 失敗案例需追蹤偵測、殘留狀態、使用者可見結果、恢復、恢復後不變量及限制。
5. 量化記錄 baseline、單位、樣本量、重複次數、負載、時間窗和干擾；假設算例不寫成 benchmark。
6. 真實觀測時間不回填為排程時間；raw logs 保留必要資訊並剔除秘密及私人資料。

## 狀態

learning-progress.json 的 unit status：planned、in_progress、blocked、complete。experiment_status 區分 not_started、partial、verified、blocked；source、build、deploy、public_verification 各記錄自己的證據，不能由一次 commit 推定全完成。

只有教材 source 回讀、必要實驗驗證、網站 source/build/deploy/public content 全成立才 complete。硬體不足列 blockers，已驗證部分保留，不抹除結果、不跳過必要深度。

歷史下架稿與實驗放 archive，不恢復發布、不以相似主題判定新課程已完成。

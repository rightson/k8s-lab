# K8s Lab — 教材與實驗規則

使用者明確指示優先。本 repo 保存 `k8s-hpc` 的所有輔助教材、練習、解答、manifest、程式與原始實驗證據。公開完整文章及其圖檔在 `rightson/rightson.github.io`，發布前完整讀取該 repo 最新 AGENTS.md；不得在這裡複製另一份網站發布規則。

## 開始前

1. 讀最新 default branch metadata、完整本檔、README、docs/learning-plan.md、docs/lesson-standard.md、docs/learning-progress.json 與相關單元。兩個 repo 各記錄 instruction commit SHA。
2. 對照網站 .github/K8S_HPC_SERIES_ROADMAP.md 與排程指令；新版 K082–K129 有明確穩定 ID，舊 #001–#006、K001–K081 是歷史，不恢復封存稿。
3. 用系列＋排定日期＋時段查 execution ledger；有既有成果先驗證及修復，不重建。

## 讀者與深度

假設讀者具備 OS、程式、基本網路與分散式原理，Kubernetes 從零學習。OS 基本名詞簡短銜接；新 K8s 概念須說明動機、模型、責任邊界與完整案例，不以術語密度代替解釋。每單元有正常路徑、至少兩個機制、失敗及恢復、量化與兩個合理替代方案。

## 實驗與證據

- 依 lesson-standard 明確鎖定 Kubernetes、kernel、runtime、插件、feature gate、硬體與依賴版本；來源用官方文件、原始碼或原始論文。
- 指令必須作用於明確的隔離測試環境；先確認 context，破壞性演練只作用於本單元建立的資源。不操作使用者既有 production cluster。
- 正常、故障、清理／恢復指令均有驗收條件；區分預期結果、實際觀測、假設算例及 reported result。
- 原始紀錄放 lessons/<id>/runs/<run-id>/，記錄執行時間、版本、硬體、指令、輸出、退出碼及限制。不提交憑證、kubeconfig/token、內部 endpoint、PDK、RTL/log 或私人資料。
- 沒有 GPU/RDMA/NUMA 或缺權限時標示未完成及受影響部分，不捏造 benchmark、不把模擬當硬體實測。
- archive 的舊觀測保留原文；遷移不改造成新測量，不算新單元完成。

## 寫入與驗收

每次寫入重讀最新 head 和目標 SHA，保留其他 agent 變更，不 force-push。先提交並回讀教材、程式及證據，再發布網站文章；兩個 repo 分別記錄完成階段。網站 build、deploy、正式正文與圖片核驗成功，且必要實驗已實跑，才將單元 status 設為 complete。未完成維持精確階段與 blockers。發布後再記錄穩定 ID、正式 URL、兩個 repo commit、驗證與下一單元。

不得自行新增、停用或重排雲端任務；不傳訊給第三人。公開文章禁止的職涯、私人及幕後流程內容不得搬進教材對外正文。

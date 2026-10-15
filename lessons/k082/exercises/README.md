# K082 練習

全部故障僅在 `cluster.sh` 建立的專用叢集；各步驟以 `record.py` 保存指令與退出碼。完成條件是待實跑的檢查項目，以下沒有預填觀測值。

1. 建立與操作：依環境文件建立一個控制平面、兩個 worker，部署兩副本 API。列出 Deployment、ReplicaSet、Pod、Service 的關係，確認兩個 Ready Pod 位於不同 worker，Service 有兩個 ready EndpointSlice 端點。解釋 apply 成功到 HTTP 成功之間的步驟。
2. 觀測與解釋：對明確的一個 Pod 呼叫 increment，再透過 Service 建立至少 20 個獨立 HTTP 請求，記錄回傳 Pod/UID。是否每次交替？為何無法由這組樣本推論負載平衡的嚴格公平性？完成條件是把 DNS 名稱、Service、後端 Pod 位址與 API server 控制請求分開說明。
3. 故障與修復：分別執行程序退出、刪 Pod、readiness 關閉、錯誤版本更新；每次保存前後 Pod UID、restartCount、Ready、EndpointSlice、版本、counter。完成條件見解答表，不以 Pod Running 當作業務正確性。
4. 節點失聯：只暫停已驗證屬於這個 kind 叢集的 worker 容器；記錄 Node Ready、Pod、端點及工作負載等待情形，再解除暫停。這是容器節點失聯演練，與實體主機斷電分開標示；兩種都尚未實跑。
5. 設計變體：假設每個 Pod 可承受 120 requests/s，外部流量 180 requests/s。計算單 Pod 故障後的容量缺口；比較加第三副本、減少流量，以及放寬節點分布的得失。指出需要量測哪些數值才可把假設轉為容量規劃。
6. 資料責任：兩個副本各自的記憶體 counter 為何不一致？程序重啟後為何歸零？提出持久化與冪等請求設計；此題只推導責任，不在 K082 部署資料庫。


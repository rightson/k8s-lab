# K082 解答與核對方式

以下是依官方語義推導的預期訊號，不是本次叢集實測。實際值必須另存 runs。

| 操作 | 預期觀測 | 負責的元件／應用責任 |
| --- | --- | --- |
| API 程序退出 17 | 原 Pod UID 保留，容器 restartCount 增加，counter 歸零，Ready 曾中斷 | kubelet 與 runtime 重啟同一 Pod 內的容器；應用的揮發狀態仍遺失 |
| 正常刪除一個受管理 Pod | 原 UID 消失，新 Pod 有新 UID，controller 再維持兩副本 | ReplicaSet 補 Pod；scheduler 做新 placement；這不是把原 Pod 搬到另一台 |
| /admin/not-ready | 程序仍回 /healthz 200，Pod Ready=False，對應 EndpointSlice ready=False | kubelet 執行 probe，端點 controller 更新資料，Service 資料平面後續採用；觀測有傳播時間 |
| 錯誤 rollout | 新版 Pod /readyz 503，舊兩副本在指定策略下繼續服務，rollout 等待逾時 | Deployment 依 maxUnavailable=0、maxSurge=1 控制更新；此策略需要額外容量 |
| rollout undo | template 回到前一 revision，新舊 ReplicaSet 收斂，版本回 v1 | 回復工作負載 template；資料庫 schema 與外部副作用需要應用處理 |
| 暫停 worker | Node 心跳中斷、狀態／taint／endpoint 逐步變化；替代 Pod 是否啟動受資源與分布規則限制 | node lifecycle、taint eviction、controller、scheduler 是不同步驟；先記錄實際時間再推論 |
| 清理 | 僅 k082-foundations kind 叢集消失，本單元 kubeconfig 被移除 | guard 先比對 kube-system UID；異常時停止，不接管陌生叢集 |

兩副本的 UID 不同、位於不同節點，只證明兩個執行實例與分布；業務資料一致性、跨實體主機容錯、外部入口可用性要另驗證。Service 以連線／資料平面行為選端點，20 次請求沒有嚴格交替也合理；長連線可能持續使用同一後端。測試程式每次回應關閉連線，降低這個教學干擾，仍沒有公平性保證。

假設算例：180 requests/s / 120 requests/s = 1.5 個副本的處理需求。兩副本健康時總容量 240 requests/s，失去一個後只剩 120 requests/s，缺口 60 requests/s；若等待佇列沒有上限，10 秒可累積 600 個請求，尚未計逾時及重試。三副本在一個故障後的假設剩餘容量 240 requests/s，但共同依賴故障、CPU throttling、記憶體、流量偏斜與擴縮延遲仍可能改變結果。

加第三副本增加資源預留；限流降低過載但犧牲可受理流量；允許剩餘節點承接多副本可減少 Pending，卻提高同節點故障的相關性。應先確認服務 SLO、實測單副本容量及失效範圍，再選策略。硬性 topology spread 是這個實驗刻意可見的配置，不是所有服務的通用答案。

counter 是單一程序記憶體；任何新程序都從 0 開始。需要保存業務資料時，必須引入獨立持久儲存及一致性策略；需要安全重試寫入時，還需設計 idempotency key／交易，而不能只增加 Pod 數。


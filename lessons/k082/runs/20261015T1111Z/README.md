# K082 本次觀測

run ID 是紀錄目錄識別，不用目錄名稱代替實際執行時間；原始時間以 commands.jsonl 每筆 started_utc／finished_utc 為準。

## 已執行

- 環境 preflight：退出碼 2，確認缺少 Docker、kind、kubectl，其他容器 runtime／socket 也未發現；CapEff／CapBnd 均為 0。
- Python HTTP 與 manifest 靜態意圖測試：9 項通過，退出碼 0。
- shell syntax check：bash -n 通過，退出碼 0。
- 安全 guard fixture 測試：結果以 commands.jsonl 為準，僅測本地腳本拒絕條件，沒有連接真實 API server。
- 本次所有可執行測試的完整 stdout／stderr 與退出碼見 [commands.jsonl](commands.jsonl)。

## 觀測性質

HTTP 測試真的啟動了本機 Python 子程序並發送 loopback 請求，確認應用的 readiness、存活、counter、退出碼及重啟後的揮發狀態。它沒有啟動容器、kubelet、scheduler、controller、DNS 或 Service；測試全過也不等於 Kubernetes 行為已驗證。

manifest 測試僅以 PyYAML 解析欄位，沒有取得 Kubernetes OpenAPI schema 或做 server-side dry-run。shell guard 使用假的 kubeconfig 字串與假的 kubectl 回應驗證拒絕路徑，不是叢集權限或 UID 實測。

兩張 SVG 已經執行網站的 svg_dark_mode.py、在淺色／深色轉成 PNG 並檢視；原圖保留於 assets。未建立網站文章，沒有網站 lint、Jekyll build、deploy 或公開內容驗證結果。

## 阻塞與下一步

必要的正常部署、容器退出、Pod 刪除、readiness 端點移除、錯誤 rollout／undo、節點失聯及清理全都待實跑。需要一台已授權、能執行 Docker/kind 的隔離測試主機；另須取得並審核 Python 基底映像 digest。沒有嘗試提權、建立替代雲端帳號、使用陌生叢集或變更任務設定。

單元保持 blocked、experiment_status=partial、next_unit=K082。先補真實叢集觀測、修正教材，再走公開長文的 source/build/deploy/public-content 驗證流程。


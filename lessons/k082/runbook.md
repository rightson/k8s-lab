# K082 隔離操作程序

以下叢集命令尚未實跑。只有離線測試及 preflight 有本次 raw output；不要把下列預期訊號當成觀測資料。從 repo 根目錄執行，先確認自己所在的測試主機已獲准建立及刪除專用 Docker 容器。

## 0. 離線檢查

```bash
python3 -m pip install -r lessons/k082/requirements.txt
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- python3 lessons/k082/src/preflight.py
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- python3 lessons/k082/src/test_offline.py
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash -n lessons/k082/src/cluster.sh
```

preflight 退出碼 2 代表缺工具。它只做唯讀環境檢查，不會連接 daemon 或讀 kubeconfig；缺工具或能力時停止叢集步驟。若不具建立隔離叢集的權限，記錄阻塞，不提權、不改用陌生叢集。

record.py 把指令、UTC 起迄時間、stdout、stderr、退出碼附加到 JSONL；只用於本教材明列且無秘密的命令。不要拿它記錄 kubeconfig、Secret、registry 認證、雲端帳號或環境變數全集。提交前人工檢查 raw logs。

## 1. 鎖定映像並建立專用叢集

先依 [環境要求](environment.md) 安裝並記錄 Docker、kind v0.33.0、kubectl。從可信 registry 取得適用架構的 Python 基底 digest，核對映像來源與安全性。此處沒有提供假 digest，未取得前無法建置。

```bash
# 先把下方值換成已核對的完整 reference；占位文字會被腳本拒絕。
K082_BASE_IMAGE='python:3.12.14-slim-bookworm@sha256:REPLACE_WITH_VERIFIED_DIGEST'
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh create --confirm-isolated "$K082_BASE_IMAGE"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
```

create 會拒絕既有同名叢集及已存在的本單元 credential/marker，不接管或覆寫。它使用 lessons/k082/.private/kubeconfig，固定 context kind-k082-foundations；建立後保存 kube-system UID，後續每個操作都先核對它。原本的預設 kubeconfig 不受影響。.private 不提交。

映像採來源內容與基底 digest 衍生的 tag，建立後另外保存 Docker image ID；kind load 載入該映像，manifest 的 imagePullPolicy 為 Never。原始 manifest 的 unbuilt 只是明示占位，render.py 會拒絕這個 tag。基底、應用 ID 與 Pod imageID 都要記錄，才能核對實際執行內容。

create 先建立本單元 namespace，再做 server-side dry-run，最後真正 apply。dry-run 檢查的是 API 是否接受物件；rollout 和 HTTP 仍要分開驗證。若中途失敗，保留紀錄，先查目前階段再處理；不要刪掉 marker 後盲目重跑。

完成條件：Deployment 兩副本 rollout 完成；兩個 Pod Ready 且位於不同 worker；EndpointSlice 有兩個 ready 端點。另保存實際 client/server、nodeInfo、系統映像 ID 及 feature gate 設定，見 environment.md。

## 2. 正常請求與程序退出

從 status 選一個明確 Pod 名稱，填入 K082_POD，不使用會誤選其他資源的 wildcard。每個故障案例前後都再跑 status。

```bash
K082_POD='REPLACE_WITH_EXACT_API_POD_NAME'
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh identity "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh increment "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh service-request "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh crash "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
```

crash 端點讓 API PID 1 退出 17；kubectl exec 可能因容器終止而收到非零退出碼，須保存而非抹去。以可接受的觀測間隔重跑 status，記錄最早及最晚觀測時間，不填入假設的固定重啟秒數。再次 identity 時，預期原 Pod UID 保留、restartCount 增加、counter 歸零。持續失敗則檢查事件與 previous container log，先定位原因，不重複注入故障。

## 3. Pod 刪除與替代實例

```bash
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh delete-pod "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
```

只刪指定且 label 屬於本單元的 Pod；不 force delete。預期原 UID 消失，替代 Pod 使用新 UID，最後回到兩個 Ready 端點。重新選取目前 Ready 的精確 Pod 名稱，避免沿用已刪除的名稱。不要把這個案例當成節點失聯。

## 4. Readiness 與 Service

```bash
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh not-ready "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh service-request "$K082_POD"
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh ready "$K082_POD"
```

此處故障 Pod 的程序仍存活，exec 仍可用；Service 請求會走穩定名稱並選可用後端。觀察 EndpointSlice 的 ready 欄位從 true 到 false，再回 true。讀 /healthz 與 /readyz 時應分別看到 200 與 503，不能只用一次 Service 成功代表所有副本健康。

## 5. 錯誤版本更新與回復

```bash
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh bad-rollout
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh undo
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
```

bad-rollout 只改本單元 Deployment 的 VERSION 與 FAIL_READINESS；rollout status 的 15 秒逾時是命令等待期限，不是自動回滾期限。預期新版不 Ready、舊版仍服務；若觀測不同，保留狀態並定位資源或策略原因。undo 後還要核對 v1、兩個 Ready 端點與實際回應。這裡沒有資料庫，所以沒有驗證 schema 回復。

## 6. Worker 容器失聯演練

這一段只在獨立測試主機、前面案例回復正常後操作。先執行 cluster.sh status 通過 UID 核對，再核對固定容器的 kind label。若任何值不同就停止。

```bash
bash lessons/k082/src/cluster.sh status
docker inspect k082-foundations-worker --format '{{ index .Config.Labels "io.x-k8s.kind.cluster" }}'
```

輸出必須是 k082-foundations。操作者另開一個終端準備解除暫停，再執行下列精確目標；不要改成任意容器名或批次操作。

```bash
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- docker pause k082-foundations-worker
# 在持續觀測端記錄 Node Ready、Pods、EndpointSlice、請求成功／失敗與時間戳。
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- docker unpause k082-foundations-worker
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh status
```

預期會經過心跳偵測、狀態與端點改變，但不要預填固定 failover 時間。記錄實際 tolerations、taint 時間和替代 Pod 的 Pending 原因；硬性分布與可用資源可能妨礙替代實例啟動。解除暫停後，核對節點重新 Ready、兩副本正常及新舊 UID。原節點資料、實體主機斷電與跨主機網路分割仍是不同實驗。

## 7. 清理

先確保暫停的 worker 已解除暫停，再清理本單元建立的整個 kind 叢集：

```bash
python3 lessons/k082/src/record.py --out lessons/k082/runs/local/commands.jsonl -- bash lessons/k082/src/cluster.sh cleanup --confirm-isolated
```

cleanup 會核對 kube-system UID，僅刪 k082-foundations，確認不再存在後移除本單元 kubeconfig 與 marker。這會刪除本單元所有容器、工作負載與揮發資料；raw run 與教材保留。它不刪其他叢集、不遞迴刪目錄，也不輸出 credential。若只完成部分建立而沒有可驗證 marker，停止自動清理並人工核對精確資源，不繞過 guard。

## 記錄格式與通過條件

每個故障案例至少保存一筆基線、一次故障、觀測過程與回復結果。功能性實驗至少獨立重複三次，記錄映像快取與其他干擾；小樣本只驗證行為，不宣稱 p99 或可用性 SLO。定量效能需另定負載產生器、request mix、期間與樣本量。

API、本單元物件、叢集版本及必要實驗都驗證後，再發布網站；source 回讀、build、deploy 與正式正文／圖檔確認成功後才 complete。目前所有叢集檢查均 pending。


# K082 版本與環境

## 教學叢集目標，尚未實跑

| 項目 | 鎖定／要求 | 本次實際狀態 |
| --- | --- | --- |
| kind | v0.33.0，官方 2026-08-26 release | 未安裝 |
| Kubernetes | v1.37.0，使用該 kind release 內建對應映像；不是最新修補版宣告 | 未建立 |
| node image | kindest/node:v1.37.0@sha256:a1ed56cfb0e7b93589bdf97c8cd566405a265939e3620fc4f5de89adff580ae5 | 未拉取 |
| kubectl | 目標 v1.37.0，至少須記錄實際 client version 並檢查相容性 | 未安裝 |
| runtime | 外層 Docker；節點內 runtime 由已鎖定映像提供，實際 containerd 版本須從 Node nodeInfo 擷取 | 無 daemon／runtime |
| 網路 | kind 預設 kindnet、kube-proxy、CoreDNS；必須記錄各 Pod 的 imageID | 未啟動 |
| 儲存 | 無 PVC／CSI 工作負載；不把預設 provisioner 當成 CSI 實測 | 不適用 |
| feature gates | 無額外覆寫；映像版本的預設值 | 未執行 |
| Python app | 基底目標 python:3.12.14-slim-bookworm，create 強制要求審核後 sha256 digest | digest 未取得，未建置 |
| 離線相依 | Python 3.12.14、PyYAML 6.0.3、Bash；unittest 為標準函式庫 | 已使用 |
| 拓樸 | 1 control-plane + 2 worker 容器，共用一實體主機 | 未建立 |

kind 官方鎖定來源：[release v0.33.0](https://github.com/kubernetes-sigs/kind/releases/tag/v0.33.0)。這是可重現教學目標，非正式環境部署建議；實際操作前需重新檢查版本安全性與相容性。Python 映像名稱只是候選，未確認 registry digest／架構可用性前不得宣稱已鎖定。

## 本次主機觀測

Ubuntu 24.04.3 LTS；x86_64；kernel 6.18.44；Python 3.12.14。程序可見 9 個邏輯 CPU，cgroup CPU quota 為 800000/100000（8 CPU 額度），memory.max 為 8589934592 bytes（8 GiB）；這些是容器視野，非獨占硬體或實體 NUMA 效能聲明。實際 NUMA 可見節點、capabilities 與工具路徑以 raw preflight 為準。

Docker／Podman／nerdctl／containerd／kind／kubectl 均不存在；未發現 daemon socket 或 KVM；CapEff 與 CapBnd 均為 0。沒有啟動容器、改 capabilities、嘗試提權或連接任何既有叢集。缺少叢集執行能力是目前必要實驗的阻塞，安裝 CLI 本身無法補足這個條件。

## 待補環境記錄

第一次成功建立叢集時保存：實際日期、CPU／NUMA／RAM、Docker 與 kind 版本、kubectl client/server、每個 Node 的 kernelVersion／containerRuntimeVersion／kubeletVersion、系統 Pod 的 imageID、應用 imageID 與基底 digest、feature gate 覆寫、拓樸與負載。使用專用 kubeconfig，但永不提交它；也不輸出 Secret、token、憑證、私有 registry 設定或使用者既有環境資料。


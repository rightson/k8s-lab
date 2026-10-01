# Kubernetes：從執行模型到平台工程

2026-10-01 核准的課程：具備資工、作業系統、程式與網路先備，從零建立 Kubernetes 能力。基本 OS 名詞按需簡短銜接；Kubernetes 初次出現的概念、責任與語義須清楚解釋。四十個核心單元後接八個 AI／HPC／EDA 進階單元，順序不可因合併排程而省略。

本檔是現行課程範圍與先備順序來源；[learning-progress.json](learning-progress.json) 是完成與驗證 ledger。[網站 roadmap](https://github.com/rightson/rightson.github.io/blob/main/.github/K8S_HPC_SERIES_ROADMAP.md) 是發布與排程入口。網站 `AGENTS.md` 管公開文章，本 repo `AGENTS.md` 管教材與實驗。

## ID、分工與接續

- series：`k8s-hpc`；公開分類「系統與平台」，domain `platform-engineering`。每週四 Asia/Taipei 19:00 執行既有技術課程分支；本文不建立或改動 scheduler。
- 歷史 #001–#006、K001–K081 均保留，不重編號、不重發；新穩定 ID K082–K129，對應課程單元 01–48。新文章 `series_order` 使用穩定 ID 的數值 82–129；可另用 `course_unit: 1` 表示課程順序。
- 下一單元 K082：以兩副本 API 服務的程序退出、節點失聯與版本更新問題建立完整背景；介紹控制平面／節點、Pod／Deployment／Service 的最小可用模型，細節依後續單元深入。
- 前置順序預設上一單元，必要引用不代表已完成實驗。Networking 負責通用協定；Distributed Systems 負責完整服務設計；TPU 負責加速器微架構。K8s 保有平台視角的獨立實驗與工程責任。
- 初始四十單元為完整核心課程；進階八單元亦按順序推進，硬體不足記錄阻塞，不宣稱實驗完成。大型單元可跨週，不用摘要冒充完整教材。

## 階段 1：建立 Kubernetes 全局模型

能力：建立測試叢集並部署前後端，解釋物件關係與成功條件。

實驗方向：追蹤兩副本服務，停止容器、刪除 Pod 並觀察控制迴路；辨認應用責任。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 01 | K082 | 從單機服務到叢集：Kubernetes 解決的問題與責任邊界 | OS、程式、網路先備；K8s 從零 |
| 02 | K083 | Object、API、YAML、label、selector 與 namespace | K082 |
| 03 | K084 | Pod、Deployment、ReplicaSet 與工作負載生命週期 | K083 |
| 04 | K085 | Service、DNS、ConfigMap、Secret：接起完整應用 | K084 |

## 階段 2：追蹤一次部署如何真正執行

能力：建立 API 到程序的完整時間線，辨識接受請求與執行完成的差距。

實驗方向：注入啟動失敗、readiness 失敗與終止逾時，依事件及元件紀錄定位責任。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 05 | K086 | kubectl apply 到 API server、admission 與 etcd | K085 |
| 06 | K087 | Controller 建立 Pod，scheduler 決定 placement | K086 |
| 07 | K088 | Kubelet、CRI、containerd 到容器程序 | K087 |
| 08 | K089 | Probes、終止、更新與 disruption | K088 |

## 階段 3：控制迴路與平台擴充

能力：實作能安全重試、恢復及刪除外部資源的 Operator。

實驗方向：在建立外部資源、寫入 status、刪除之間中斷；驗證重複執行及孤兒資源。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 09 | K090 | resourceVersion、watch、並行更新與 Server-Side Apply | K089 |
| 10 | K091 | Reconciliation、informer、workqueue、重試與冪等性 | K090 |
| 11 | K092 | CRD、Operator、spec/status 與版本演進 | K091 |
| 12 | K093 | Finalizer、garbage collection、leader election 與外部副作用 | K092 |

## 階段 4：節點資源與 Linux 效能

能力：由資源宣告追到 Linux 機制及硬體，解釋吞吐與尾延遲。

實驗方向：比較 quota、CPU 綁定、共享節點及記憶體壓力；測量 p99、throttling、回收與終止。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 13 | K094 | Namespace、cgroup v2、runtime 與隔離邊界 | K093 |
| 14 | K095 | Requests/limits、CPU quota、競爭與尾延遲 | K094 |
| 15 | K096 | QoS、reclaim、OOM、eviction 與 page cache | K095 |
| 16 | K097 | CPU Manager、NUMA、Topology Manager 與 hugepages | K096 |

## 階段 5：網路資料路徑與除錯

能力：從應用請求追到封包路徑，辨識政策、路由、Service 與重試問題。

實驗方向：注入 DNS、MTU、endpoint 與 conntrack 故障，對照封包、延遲及應用重試。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 17 | K098 | Pod 到 Pod：veth、routing 與 CNI | K097 |
| 18 | K099 | Service、EndpointSlice、NAT、conntrack 與 eBPF | K098 |
| 19 | K100 | DNS、Gateway／Ingress、NetworkPolicy 與連線生命週期 | K099 |
| 20 | K101 | Overlay、MTU、跨節點流量、壅塞與故障定位 | K100 |

## 階段 6：儲存與有狀態應用

能力：理解工作負載與資料的不同生命週期，驗收可恢復性。

實驗方向：演練節點失聯、volume attach 卡住及還原，驗證資料而非只看 Pod Running。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 21 | K102 | PV/PVC、StorageClass、CSI 與 provision/attach/mount | K101 |
| 22 | K103 | StatefulSet、儲存拓樸與重新排程 | K102 |
| 23 | K104 | Local、NFS、block、object storage 的效能與持久性 | K103 |
| 24 | K105 | Snapshot、備份、恢復與資料正確性 | K104 |

## 階段 7：排程、擴縮與容量管理

能力：比較資源政策對服務 SLO、工作等待時間及成本的影響。

實驗方向：以線上服務與批次工作競爭資源，測量擴縮延遲、p99、利用率及未排程原因。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 25 | K106 | Scheduling Framework、filter/score、affinity 與 taints | K105 |
| 26 | K107 | Priority、preemption、topology spread 與公平性 | K106 |
| 27 | K108 | HPA/VPA、節點擴縮與控制迴路互動 | K107 |
| 28 | K109 | Bin packing、碎片化、預留容量與成本 | K108 |

## 階段 8：安全與多租戶

能力：依威脅模型選隔離層級，驗證政策真正作用的路徑。

實驗方向：建立不同信任程度的測試租戶，檢查越權、跨租戶存取及資源耗盡。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 29 | K110 | 身分、ServiceAccount、RBAC 與權限模型 | K109 |
| 30 | K111 | Pod Security、seccomp、capabilities 與隔離 | K110 |
| 31 | K112 | Admission policy、Secret 管理、映像與供應鏈 | K111 |
| 32 | K113 | Namespace、quota、網路隔離與租戶控制平面選型 | K112 |

## 階段 9：交付與叢集生命週期

能力：完成可審核的應用發布和叢集升級，界定回復及回滾限制。

實驗方向：演練錯誤發布、容量不足的 drain、升級及憑證輪替，保留前後證據。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 33 | K114 | Helm/Kustomize、GitOps、狀態漂移與所有權 | K113 |
| 34 | K115 | Rolling/canary、回滾與設定／資料相容性 | K114 |
| 35 | K116 | HA 控制平面、bootstrap、節點映像與基礎設施管理 | K115 |
| 36 | K117 | 版本升級、API 移除、插件相容性、drain 與憑證輪替 | K116 |

## 階段 10：可靠性與完整平台設計

能力：交付可解釋容量、可靠性、安全、維運及成本的完整平台。

實驗方向：完成事故時間線、備份還原與容量驗收；區分叢集恢復和業務恢復。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 37 | K118 | SLI/SLO、metrics/logs/traces 與告警 | K117 |
| 38 | K119 | API、etcd、controller、scheduler 的效能與規模限制 | K118 |
| 39 | K120 | 控制平面故障、災難恢復與事故分析 | K119 |
| 40 | K121 | 多租戶平台整合設計與驗收 | K120 |

## 階段 11：AI／HPC 工作負載工程

能力：評估設備利用率、工作完成時間和故障重做成本。

實驗方向：依可用硬體比較 placement、queue 和恢復；無 GPU/RDMA 時僅驗證可執行部分。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 41 | K122 | GPU、device plugin、DRA 與設備生命週期 | K121 |
| 42 | K123 | Queue、gang scheduling、fair-share 與 backfill | K122 |
| 43 | K124 | GPU/NIC/NUMA 拓樸、RDMA 與 collective communication | K123 |
| 44 | K125 | 訓練 checkpoint、推論擴縮與資料供應 | K124 |

## 階段 12：EDA 與混合運算平台

能力：由工作形狀、資料及資源限制推導平台分工和導入順序。

實驗方向：使用公開或合成工作，不接觸 PDK、內部 RTL/log/license；比較混合方案。

| 單元 | 穩定 ID | 問題與範圍 | 先備 |
| --- | --- | --- | --- |
| 45 | K126 | EDA DAG、長時間工作、取消與重試 | K125 |
| 46 | K127 | License、大記憶體與資源 admission | K126 |
| 47 | K128 | Shared storage、artifact lineage、checkpoint 與恢復 | K127 |
| 48 | K129 | Kubernetes、Slurm/LSF、混合平台與多叢集選型 | K128 |

## 驗收與資源

每單元遵守 [lesson-standard.md](lesson-standard.md)：完整問題、端到端路徑、至少兩個關鍵機制、故障與恢復、量化分析、兩個合理替代方案。環境與 feature maturity 按單元鎖定，不把 alpha/beta 功能推定為通用 production 能力。輔助教材、練習、解答、manifest、程式及原始實驗紀錄只放本 repo；完整公開文章與文章圖放網站 repo。

官方閱讀入口：[元件](https://kubernetes.io/docs/concepts/overview/components/)、[API](https://kubernetes.io/docs/reference/using-api/api-concepts/)、[Operator](https://kubernetes.io/docs/concepts/extend-kubernetes/operator/)、[多租戶](https://kubernetes.io/docs/concepts/security/multi-tenancy/)、[升級](https://kubernetes.io/docs/tasks/administer-cluster/cluster-upgrade/)。每次研究另核對該單元的精確版本與原始碼。

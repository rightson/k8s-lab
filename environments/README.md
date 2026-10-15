# 實驗環境

目前尚未建立新課程的 Kubernetes cluster，也未鎖定新單元的版本或執行實驗。每個單元開始時，依官方支援狀態核對並記錄精確版本、映像 digest、feature gates 與硬體。

- 一般 API／controller／workload 實驗可選獨立本機或 VM 測試叢集，交代與正式環境差異。
- Kernel／cgroup／kubelet 實驗需要可觀測 Linux 節點；macOS 上容器叢集的 VM 邊界須標明。
- NUMA、GPU、RDMA、HA 和多區域實驗各列設備／拓樸要求；缺設備就記錄阻塞，不捏造輸出。
- K001 的歷史環境與 raw output 位於 archive/k001，僅代表原實驗，不是新課程環境。

## K082 目前狀態

已完成 [環境需求與版本目標](../lessons/k082/environment.md) 及 [唯讀 preflight 與離線測試](../lessons/k082/runs/20261015T1111Z/README.md)。目前執行環境缺少容器 runtime、kind、kubectl 與必要能力，尚未建立叢集；Python 基底映像 digest 尚待核對。沒有把離線測試計入真實 K8s 實驗完成。


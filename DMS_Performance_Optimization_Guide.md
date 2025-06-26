# AWS DMS 性能优化指南

## 问题概述

当AWS DMS在同步MySQL到Redshift时，如果swap交换区满了，系统会从并行处理降级为串行操作，导致同步延迟越来越严重。

## 问题分析

当DMS复制实例的swap交换区满时，系统会从并行处理降级为串行操作，原因包括：
- 内存不足导致频繁的磁盘交换
- DMS的内存缓冲区（incoming buffer、outgoing buffer、sorter）压力过大
- 事务处理从内存转移到磁盘，性能急剧下降

## 立即恢复措施

### 1. 升级复制实例类型

**推荐使用内存优化实例（R5/R6i系列）**：

```bash
# 查看当前可用的实例类型
aws dms describe-orderable-replication-instances --region your-region

# 修改复制实例到更大内存的类型
aws dms modify-replication-instance \
    --replication-instance-arn your-replication-instance-arn \
    --replication-instance-class dms.r5.xlarge \
    --apply-immediately
```

**内存优化实例推荐**：
- 当前如果是dms.t3.large (8GB)，升级到dms.r5.large (16GB)
- 高负载场景推荐dms.r5.xlarge (32GB) 或更大

### 2. 优化任务设置

修改任务的内存相关参数：

```json
{
  "ChangeProcessingTuning": {
    "MemoryLimitTotal": 2048,        // 增加到2GB（默认1024MB）
    "MemoryKeepTime": 30,            // 减少到30秒（默认60秒）
    "BatchApplyMemoryLimit": 1000,   // 增加批处理内存限制
    "BatchSplitSize": 10000,         // 设置批处理大小限制
    "StatementCacheSize": 100        // 增加语句缓存
  }
}
```

### 3. 启用批量应用模式

对于Redshift目标，启用批量处理可以显著提升性能：

```json
{
  "TargetMetadata": {
    "BatchApplyEnabled": true,
    "BatchApplyPreserveTransaction": false  // 牺牲事务完整性换取性能
  }
}
```

## 长期优化策略

### 1. 监控和告警设置

设置CloudWatch告警监控关键指标：

```bash
# 创建内存使用率告警
aws cloudwatch put-metric-alarm \
    --alarm-name "DMS-Memory-High" \
    --alarm-description "DMS replication instance memory usage high" \
    --metric-name FreeableMemory \
    --namespace AWS/DMS \
    --statistic Average \
    --period 300 \
    --threshold 500000000 \
    --comparison-operator LessThanThreshold \
    --evaluation-periods 2
```

### 2. 源端优化

**MySQL端优化**：
- 启用binlog压缩：`binlog_transaction_compression=ON`
- 调整binlog格式：使用ROW格式但限制行大小
- 设置合适的事务大小，避免长事务

### 3. 目标端优化

**Redshift端优化**：
- 使用COPY命令批量加载
- 合理设置分布键和排序键
- 在迁移期间暂时禁用外键约束

### 4. 网络优化

- 确保DMS复制实例与源/目标数据库在同一可用区
- 使用专用网络连接减少延迟

## 恢复正常状态的步骤

### 1. 立即行动

```bash
# 暂停任务
aws dms stop-replication-task --replication-task-arn your-task-arn

# 升级实例
aws dms modify-replication-instance \
    --replication-instance-arn your-instance-arn \
    --replication-instance-class dms.r5.xlarge \
    --apply-immediately
```

### 2. 修改任务配置

- 更新任务设置中的内存参数
- 启用批量应用模式

### 3. 重启任务

```bash
# 重启任务
aws dms start-replication-task \
    --replication-task-arn your-task-arn \
    --start-replication-task-type resume-processing
```

### 4. 监控恢复

- 观察CDCLatencySource和CDCLatencyTarget指标
- 确认swap使用率下降
- 验证同步延迟恢复正常

## 预防措施

- **容量规划**：根据源数据库的TPS选择合适的实例类型
- **定期监控**：设置内存、CPU、网络的CloudWatch告警
- **测试验证**：在生产环境前进行充分的性能测试
- **分批迁移**：对于大表考虑分批迁移减少内存压力

## DMS 实例类型参考

### 内存优化实例类型 (推荐用于高TPS场景)

| 实例类型 | vCPU | 内存 (GiB) | 适用场景 |
|---------|------|-----------|----------|
| dms.r5.large | 2 | 16 | 中等负载 |
| dms.r5.xlarge | 4 | 32 | 高负载推荐 |
| dms.r5.2xlarge | 8 | 64 | 超高负载 |
| dms.r5.4xlarge | 16 | 128 | 企业级负载 |
| dms.r6i.large | 2 | 16 | 新一代中等负载 |
| dms.r6i.xlarge | 4 | 32 | 新一代高负载 |
| dms.r6i.2xlarge | 8 | 64 | 新一代超高负载 |

### 计算优化实例类型

| 实例类型 | vCPU | 内存 (GiB) | 适用场景 |
|---------|------|-----------|----------|
| dms.c5.large | 2 | 4 | CPU密集型 |
| dms.c5.xlarge | 4 | 8 | 高CPU需求 |
| dms.c6i.large | 2 | 4 | 新一代CPU密集型 |
| dms.c6i.xlarge | 4 | 8 | 新一代高CPU需求 |

## 关键配置参数说明

### ChangeProcessingTuning 参数详解

| 参数 | 默认值 | 推荐值 | 说明 |
|------|--------|--------|------|
| MemoryLimitTotal | 1024 MB | 2048 MB | 所有事务在内存中的最大占用 |
| MemoryKeepTime | 60秒 | 30秒 | 事务在内存中保持的最大时间 |
| BatchApplyMemoryLimit | 500 MB | 1000 MB | 批处理模式下的内存限制 |
| BatchSplitSize | 0 | 10000 | 单个批次的最大变更数量 |
| StatementCacheSize | 50 | 100 | 预编译语句缓存大小 |

### BatchApply 相关参数

| 参数 | 默认值 | 推荐值 | 说明 |
|------|--------|--------|------|
| BatchApplyEnabled | false | true | 启用批量应用模式 |
| BatchApplyPreserveTransaction | true | false | 是否保持事务完整性 |
| BatchApplyTimeoutMin | 1秒 | 1秒 | 批处理最小等待时间 |
| BatchApplyTimeoutMax | 30秒 | 30秒 | 批处理最大等待时间 |

## AWS 官方文档链接

### 核心配置和最佳实践
- **DMS最佳实践**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_BestPractices.html
- **复制实例类型选择**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.Types.html
- **变更处理调优设置**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.ChangeProcessingTuning.html

### 监控和故障排除
- **DMS任务监控**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Monitoring.html
- **故障排除指南**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Troubleshooting.html

### 源和目标配置
- **MySQL作为源端配置**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Source.MySQL.html
- **Redshift作为目标端配置**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Target.Redshift.html

### 性能优化相关
- **任务设置配置**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_Tasks.CustomizingTasks.TaskSettings.html
- **网络配置**: https://docs.aws.amazon.com/dms/latest/userguide/CHAP_ReplicationInstance.VPC.html

### AWS CLI 参考
- **DMS CLI命令参考**: https://docs.aws.amazon.com/cli/latest/reference/dms/
- **CloudWatch CLI参考**: https://docs.aws.amazon.com/cli/latest/reference/cloudwatch/

### 定价信息
- **DMS定价页面**: https://aws.amazon.com/dms/pricing/

## 常见问题和解决方案

### Q: 如何判断当前是否处于串行模式？
A: 通过CloudWatch监控以下指标：
- `CDCLatencySource` 和 `CDCLatencyTarget` 持续增长
- `FreeableMemory` 接近0
- `SwapUsage` 接近实例内存大小

### Q: 升级实例类型会中断服务吗？
A: 使用 `--apply-immediately` 参数会立即重启实例，建议在维护窗口期间执行。

### Q: 批量模式会影响数据一致性吗？
A: 设置 `BatchApplyPreserveTransaction=false` 会牺牲事务完整性换取性能，适合可以容忍短暂不一致的场景。

### Q: 如何监控优化效果？
A: 关注以下关键指标：
- CDC延迟是否下降
- 内存使用率是否稳定
- Swap使用率是否降低
- 吞吐量是否提升

---

**文档创建时间**: 2025-06-25  
**适用版本**: AWS DMS 3.5+  
**更新频率**: 建议定期检查AWS官方文档获取最新信息

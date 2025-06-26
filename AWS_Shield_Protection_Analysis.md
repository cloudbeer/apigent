# AWS Shield DDoS 防护能力分析报告

## 概述

AWS Shield 是 Amazon Web Services 提供的托管式 DDoS 防护服务，分为 Shield Standard（免费版）和 Shield Advanced（付费版）两个版本。

## AWS Shield Standard（免费版）

### 基本信息
- **费用**: 免费，所有 AWS 客户自动获得
- **启用方式**: 自动启用，无需手动配置
- **防护范围**: 所有 AWS 服务，包括 Network Load Balancer (NLB)

### 防护能力
- **防护层级**: 
  - Layer 3（网络层）：防护网络容量攻击
  - Layer 4（传输层）：防护网络协议攻击，如 TCP SYN 洪水攻击
- **攻击类型**: 防御最常见、频繁发生的网络和传输层 DDoS 攻击
- **特别优化**: Route 53 托管区域、CloudFront 分发和 Global Accelerator 获得更全面的可用性保护

### 对 Network Load Balancer (NLB) 的防护
- ✅ **四层防护**: 提供 Layer 3 和 Layer 4 的 DDoS 防护
- ✅ **自动保护**: 无需额外配置
- ✅ **基础防护**: 覆盖常见的四层攻击向量

### 防护容量限制
⚠️ **重要**: AWS 官方**未公布** Shield Standard 的具体防护容量数据（如能防御多少 Gbps 或 Tbps 的攻击）

**官方描述**:
- "防御最常见、频繁发生的网络和传输层 DDoS 攻击"
- "为所有 AWS 客户提供自动保护"
- "基础的网络层和传输层防护"

## AWS Shield Advanced（付费版）

### 增强防护能力
- **多层防护**: 覆盖 Layer 3、Layer 4 和 Layer 7
- **防护容量**: 文档明确提到可在 AWS 网络边界处理 **"multiple terabytes of traffic"（多TB级别的流量）**
- **专家支持**: 24/7 DDoS 响应团队支持

### 对 NLB 的 Shield Advanced 保护
- **保护方式**: NLB 需要通过**关联 Elastic IP 地址**来获得 Shield Advanced 保护
- **边界防护**: 在 AWS 网络边界进行防护，而不是在 VPC 内部
- **网络 ACL 提升**: 攻击期间自动将网络 ACL 部署到 AWS 网络边界

### 受保护的资源类型
Shield Advanced 支持以下资源类型：
- Amazon CloudFront 分发
- Amazon Route 53 托管区域
- AWS Global Accelerator 标准加速器
- Amazon EC2 Elastic IP 地址
- Amazon EC2 实例（通过关联的 Elastic IP 地址）
- Elastic Load Balancing 负载均衡器：
  - Application Load Balancers
  - Classic Load Balancers
  - **Network Load Balancers**（通过关联的 Elastic IP 地址）

## 攻击类型防护

AWS Shield 能够防护以下类型的攻击：

### 1. 网络容量攻击（Layer 3）
- 试图饱和目标网络或资源容量
- 拒绝合法用户的服务访问

### 2. 网络协议攻击（Layer 4）
- 滥用协议拒绝目标资源服务
- 如 TCP SYN 洪水攻击，耗尽服务器、负载均衡器或防火墙的连接状态

### 3. 应用层攻击（Layer 7）
- **仅 Shield Advanced 支持**
- 通过有效查询洪水攻击应用程序
- 如 Web 请求洪水攻击

## 重要限制和要求

### Shield Standard
- 无具体防护容量保证
- 仅提供基础防护
- 无法获得专家支持

### Shield Advanced
- **Elastic IP 要求**: NLB 必须关联 Elastic IP 地址才能获得保护
- **手动配置**: 某些扩展工具（如 Elastic Beanstalk）不会自动为 NLB 附加 Elastic IP，需要手动配置
- **资源限制**: 每个 AWS 账户每种资源类型最多可保护 1,000 个资源
- **IPv4 支持**: 支持 IPv4，不支持 IPv6

## 官方文档链接

### Shield Standard 相关
- [Shield Standard 概述](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-standard-summary.html)
- [Shield 工作原理](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-overview.html)

### Shield Advanced 相关
- [NLB Shield Advanced 保护详细说明](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-protections-ec2-nlb.html)
- [Shield 支持的资源类型列表](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-protections-by-resource-type.html)
- [Shield Advanced 概述](https://docs.aws.amazon.com/waf/latest/developerguide/ddos-advanced-summary.html)

### 最佳实践
- [AWS DDoS 最佳实践白皮书](https://docs.aws.amazon.com/whitepapers/latest/aws-best-practices-ddos-resiliency/mitigation-techniques.html)

## 总结

### 对于 NLB 的四层防护
- ✅ **Shield Standard**: 提供基础的 Layer 3 和 Layer 4 DDoS 防护，免费且自动启用
- ✅ **Shield Advanced**: 提供增强的多层防护，可处理多 TB 级别攻击，需要通过 Elastic IP 关联

### 防护容量
- **Shield Standard**: AWS 未公布具体防护容量数据
- **Shield Advanced**: 可在 AWS 网络边界处理多 TB 级别的攻击流量

### 建议
- 如需明确的防护容量保证，建议升级到 Shield Advanced
- 如有具体防护需求，建议联系 AWS 技术支持获取详细信息

---

*报告生成时间: 2025-06-25*  
*基于 AWS 官方文档分析*

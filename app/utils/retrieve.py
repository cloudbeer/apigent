import logging
from typing import List, Dict, Any, Optional
from app.utils.pg import query_dict, QueryCondition
from app.utils.ai import get_embedding
from app.models.tool import AbigentTool
import re
from collections import Counter
import jieba

logger = logging.getLogger(__name__)

# 中文停用词列表
CHINESE_STOPWORDS = {
    "的",
    "了",
    "和",
    "与",
    "或",
    "在",
    "是",
    "有",
    "这",
    "那",
    "我",
    "你",
    "他",
    "她",
    "它",
    "们",
    "一个",
    "一些",
    "一样",
    "一种",
    "一直",
    "一般",
    "一起",
    "一边",
    "一面",
    "上",
    "上下",
    "上述",
    "上面",
    "下",
    "下列",
    "下面",
    "不",
    "不仅",
    "不但",
    "不光",
    "不单",
    "不只",
    "不同",
    "不如",
    "不妨",
    "不尽",
    "不得",
    "不怕",
    "不惟",
    "不成",
    "不拘",
    "不敢",
    "不料",
    "不断",
    "不是",
    "不比",
    "不然",
    "不特",
    "不独",
    "不管",
    "不至",
    "不若",
    "不论",
    "不过",
    "不问",
    "与",
    "与其",
    "与否",
    "与此同时",
    "且",
    "两者",
    "个",
    "个别",
    "中",
    "临",
    "为",
    "为了",
    "为什么",
    "为何",
    "为着",
    "乃",
    "乃至",
    "么",
    "之",
    "之一",
    "之所以",
    "之类",
    "乎",
    "乘",
    "也",
    "也好",
    "也罢",
    "了",
    "于",
    "于是",
    "于是乎",
    "云云",
    "些",
    "亦",
    "人",
    "人们",
    "人家",
    "什么",
    "什么样",
    "今",
    "介于",
    "仍",
    "仍旧",
    "从",
    "以",
    "以上",
    "以为",
    "以便",
    "以免",
    "以及",
    "以至",
    "以至于",
    "以致",
    "们",
    "任",
    "任何",
    "任凭",
    "会",
    "似的",
    "但",
    "但是",
    "何",
    "何况",
    "何处",
    "何时",
    "作为",
    "你",
    "你们",
    "使得",
    "例如",
    "依",
    "依照",
    "俺",
    "俺们",
    "倘",
    "倘使",
    "倘或",
    "倘然",
    "倘若",
    "借",
    "假使",
    "假如",
    "假若",
    "像",
    "儿",
    "先不先",
    "光是",
    "全体",
    "全部",
    "兮",
    "关于",
    "其",
    "其一",
    "其中",
    "其二",
    "其他",
    "其余",
    "其它",
    "其次",
    "具体地说",
    "具体说来",
    "兼之",
    "内",
    "再",
    "再其次",
    "再则",
    "再有",
    "再者",
    "再者说",
    "再说",
    "冒",
    "冲",
    "况且",
    "几",
    "几时",
    "凡",
    "凡是",
    "凭",
    "凭借",
    "出于",
    "出来",
    "分别",
    "则",
    "别",
    "别人",
    "别处",
    "别是",
    "别的",
    "别管",
    "别说",
    "到",
    "前后",
    "前者",
    "加之",
    "即",
    "即令",
    "即使",
    "即便",
    "即如",
    "即或",
    "即若",
    "却",
    "去",
    "又",
    "又及",
    "及",
    "及其",
    "及至",
    "反之",
    "反过来",
    "反过来说",
    "另",
    "另一方面",
    "另外",
    "另悉",
    "只",
    "只当",
    "只怕",
    "只是",
    "只有",
    "只消",
    "只要",
    "只限",
    "叫",
    "叮咚",
    "可",
    "可以",
    "可是",
    "可见",
    "各",
    "各个",
    "各位",
    "各种",
    "各自",
    "同",
    "同时",
    "后",
    "后者",
    "向",
    "向着",
    "吓",
    "吗",
    "否则",
    "吧",
    "吧哒",
    "吱",
    "呀",
    "呃",
    "呕",
    "呗",
    "呜",
    "呜呼",
    "呢",
    "呵",
    "呵呵",
    "呸",
    "呼哧",
    "咋",
    "和",
    "咚",
    "咦",
    "咧",
    "咱",
    "咱们",
    "咳",
    "哇",
    "哈",
    "哈哈",
    "哉",
    "哎",
    "哎呀",
    "哎哟",
    "哗",
    "哟",
    "哦",
    "哩",
    "哪",
    "哪个",
    "哪些",
    "哪儿",
    "哪天",
    "哪年",
    "哪怕",
    "哪样",
    "哪边",
    "哪里",
    "哼",
    "哼唷",
    "唉",
    "唯有",
    "啊",
    "啐",
    "啥",
    "啦",
    "啪达",
    "啷当",
    "喂",
    "喏",
    "喔唷",
    "喽",
    "嗡",
    "嗡嗡",
    "嗬",
    "嗯",
    "嗳",
    "嘎",
    "嘎登",
    "嘘",
    "嘛",
    "嘻",
    "嘿",
    "因",
    "因为",
    "因此",
    "因而",
    "固然",
    "在",
    "在下",
    "地",
    "多",
    "多少",
    "她",
    "她们",
    "如",
    "如上所述",
    "如下",
    "如何",
    "如其",
    "如果",
    "如此",
    "如若",
    "始而",
    "孰知",
    "宁",
    "宁可",
    "宁愿",
    "宁肯",
    "它",
    "它们",
    "对",
    "对于",
    "对待",
    "对方",
    "对比",
    "将",
    "小",
    "尔",
    "尔后",
    "尔尔",
    "尚且",
    "就",
    "就是",
    "就是了",
    "就是说",
    "就算",
    "就要",
    "尽",
    "尽管",
    "尽管如此",
    "岂但",
    "己",
    "已",
    "已矣",
    "巴",
    "巴巴",
    "并",
    "并且",
    "并非",
    "庶乎",
    "庶几",
    "开外",
    "开始",
    "归",
    "归齐",
    "当",
    "当地",
    "当然",
    "当着",
    "彼",
    "彼此",
    "往",
    "待",
    "很",
    "得",
    "得了",
    "怎",
    "怎么",
    "怎么办",
    "怎么样",
    "怎奈",
    "怎样",
    "总之",
    "总的来看",
    "总的来说",
    "总的说来",
    "总而言之",
    "恰恰相反",
    "您",
    "惟其",
    "慢说",
    "我",
    "我们",
    "或",
    "或则",
    "或是",
    "或曰",
    "或者",
    "截至",
    "所",
    "所以",
    "所在",
    "所幸",
    "所有",
    "才",
    "才能",
    "打",
    "打从",
    "把",
    "抑或",
    "拿",
    "按",
    "按照",
    "换句话说",
    "换言之",
    "据",
    "据此",
    "接着",
    "故",
    "故此",
    "故而",
    "旁人",
    "无",
    "无宁",
    "无论",
    "既",
    "既往",
    "既是",
    "既然",
    "日",
    "时",
    "时候",
    "是",
    "是以",
    "是的",
    "更",
    "曾",
    "替",
    "替代",
    "最",
    "有",
    "有些",
    "有关",
    "有及",
    "有时",
    "有的",
    "望",
    "朝",
    "朝着",
    "本",
    "本人",
    "本地",
    "本着",
    "本身",
    "来",
    "来着",
    "来自",
    "来说",
    "极了",
    "果然",
    "果真",
    "某",
    "某个",
    "某些",
    "某某",
    "根据",
    "欤",
    "正值",
    "正如",
    "正巧",
    "正是",
    "此",
    "此地",
    "此处",
    "此外",
    "此时",
    "此次",
    "此间",
    "毋宁",
    "每",
    "每当",
    "比",
    "比及",
    "比如",
    "比方",
    "没奈何",
    "沿",
    "沿着",
    "漫说",
    "焉",
    "然则",
    "然后",
    "然而",
    "照",
    "照着",
    "犹且",
    "犹自",
    "甚且",
    "甚么",
    "甚或",
    "甚而",
    "甚至",
    "甚至于",
    "用",
    "用来",
    "由",
    "由于",
    "由此",
    "由此可见",
    "的",
    "的确",
    "的话",
    "直到",
    "相对而言",
    "省得",
    "看",
    "眨眼",
    "着",
    "着呢",
    "矣",
    "矣乎",
    "矣哉",
    "离",
    "竟而",
    "第",
    "等",
    "等到",
    "等等",
    "简言之",
    "管",
    "类如",
    "紧接着",
    "纵",
    "纵令",
    "纵使",
    "纵然",
    "经",
    "经过",
    "结果",
    "给",
    "继之",
    "继后",
    "继而",
    "综上所述",
    "罢了",
    "者",
    "而",
    "而且",
    "而况",
    "而后",
    "而外",
    "而已",
    "而是",
    "而言",
    "能",
    "能否",
    "腾",
    "自",
    "自个儿",
    "自从",
    "自各儿",
    "自后",
    "自家",
    "自己",
    "自打",
    "自身",
    "至",
    "至于",
    "至今",
    "至若",
    "致",
    "般的",
    "若",
    "若夫",
    "若是",
    "若果",
    "若非",
    "莫不然",
    "莫如",
    "莫若",
    "虽",
    "虽则",
    "虽然",
    "虽说",
    "被",
    "要",
    "要不",
    "要不是",
    "要不然",
    "要么",
    "要是",
    "譬喻",
    "譬如",
    "让",
    "许多",
    "论",
    "设使",
    "设或",
    "设若",
    "诚如",
    "诚然",
    "该",
    "说",
    "说来",
    "请",
    "诸",
    "诸位",
    "诸如",
    "谁",
    "谁人",
    "谁料",
    "谁知",
    "贼死",
    "赖以",
    "赶",
    "起",
    "起见",
    "趁",
    "趁着",
    "越是",
    "距",
    "跟",
    "较",
    "较之",
    "边",
    "过",
    "还",
    "还是",
    "还有",
    "还要",
    "这",
    "这一来",
    "这个",
    "这么",
    "这么些",
    "这么样",
    "这么点儿",
    "这些",
    "这会儿",
    "这儿",
    "这就是说",
    "这时",
    "这样",
    "这次",
    "这般",
    "这边",
    "这里",
    "进而",
    "连",
    "连同",
    "逐步",
    "通过",
    "遵循",
    "遵照",
    "那",
    "那个",
    "那么",
    "那么些",
    "那么样",
    "那些",
    "那会儿",
    "那儿",
    "那时",
    "那样",
    "那般",
    "那边",
    "那里",
    "都",
    "鄙人",
    "鉴于",
    "针对",
    "阿",
    "除",
    "除了",
    "除外",
    "除开",
    "除此之外",
    "除非",
    "随",
    "随后",
    "随时",
    "随着",
    "难道说",
    "非但",
    "非徒",
    "非特",
    "非独",
    "靠",
    "顺",
    "顺着",
    "首先",
    "！",
    "，",
    "：",
    "；",
    "？",
}


def calculate_keyword_similarity(query: str, text: str) -> float:
    """
    计算查询文本和目标文本的关键词相似度（优化中文支持）
    """
    # 检测是否为阿拉伯语
    arabic_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]')
    if arabic_pattern.search(query) or arabic_pattern.search(text):
        return 1.0

    # 使用jieba进行中文分词
    query_words = set(jieba.cut(query))
    text_words = set(jieba.cut(text))


    # 过滤停用词和空白字符
    query_words = {
        word for word in query_words if word.strip() and word not in CHINESE_STOPWORDS
    }
    text_words = {
        word for word in text_words if word.strip() and word not in CHINESE_STOPWORDS
    }

    print(f"query_words: {query_words}")
    print(f"text_words: {text_words}")
    
    # 如果分词后没有有效词汇，回退到字符级匹配
    if not query_words:
        query_words = set(query)
        query_words = {
            char
            for char in query_words
            if char.strip() and char not in CHINESE_STOPWORDS
        }

    if not text_words:
        text_words = set(text)
        text_words = {
            char
            for char in text_words
            if char.strip() and char not in CHINESE_STOPWORDS
        }

    if not query_words or not text_words:
        return 0.0

    intersection = query_words.intersection(text_words)
    return len(intersection) / len(query_words)


def rerank_tools(
    tools: List[Dict[str, Any]],
    query: str,
    weights: Dict[str, float] = {
        "vector_similarity": 0.7,  # 增加向量相似度的权重
        "keyword_similarity": 0.3,  # 降低关键词相似度的权重
    },
) -> List[Dict[str, Any]]:
    """
    对召回的工具进行重排序

    Args:
        tools: 召回的工具列表
        query: 用户查询
        weights: 各评分维度的权重

    Returns:
        重排序后的工具列表
    """
    for tool in tools:
        # 计算关键词相似度
        keyword_sim = calculate_keyword_similarity(
            query,
            f"{tool['name']} {tool['description']} {tool.get('text_variant', '')}",
        )

        # 计算综合得分
        tool["score"] = (
            weights["vector_similarity"] * tool["similarity"]
            + weights["keyword_similarity"] * keyword_sim
        )

    # 按综合得分排序
    return sorted(tools, key=lambda x: x["score"], reverse=True)


def retrieve_tools_by_text(
    text: str,
    limit: int = 5,
    similarity_threshold: float = 0.4,
    use_tool_embedding: bool = True,
    rerank: bool = True,
) -> List[Dict[str, Any]]:
    """
    根据输入文本检索最相似的工具

    Args:
        text: 用户输入的查询文本
        limit: 返回结果的最大数量
        similarity_threshold: 相似度阈值，低于此值的结果将被过滤
        use_tool_embedding: 是否使用工具的变体嵌入向量表进行检索
        rerank: 是否对结果进行重排序

    Returns:
        List[Dict[str, Any]]: 匹配的工具列表，按相似度降序排序
    """
    # 动态调整相似度阈值
    if len(text) < 5:
        similarity_threshold = max(0.3, similarity_threshold - 0.1)
    elif len(text) > 20:
        similarity_threshold = min(0.8, similarity_threshold + 0.1)

    # 获取文本的嵌入向量
    text_embedding = get_embedding(text)

    if use_tool_embedding:
        # 使用工具变体嵌入表进行检索
        sql = """
        WITH ranked_tools AS (
            SELECT 
                t.id,
                t.name,
                t.description,
                t.url,
                t.http_method,
                t.http_context,
                t.category_id,
                te.text_variant,
                1 - (te.embedding <=> %s::vector) AS similarity,
                ROW_NUMBER() OVER (PARTITION BY t.id ORDER BY 1 - (te.embedding <=> %s::vector) DESC) AS rank
            FROM 
                apigent_tool_embedding te
            JOIN 
                apigent_tool t ON te.tool_id = t.id
            WHERE 
                1 - (te.embedding <=> %s::vector) > %s
        )
        SELECT 
            id,
            name,
            description,
            url,
            http_method,
            http_context,
            category_id,
            text_variant,
            similarity
        FROM 
            ranked_tools
        WHERE 
            rank = 1
        ORDER BY 
            similarity DESC
        LIMIT %s
        """
        params = (
            text_embedding,
            text_embedding,
            text_embedding,
            similarity_threshold,
            limit * 2,
        )  # 召回更多结果用于重排序
    else:
        # 直接使用工具表进行检索
        sql = """
        SELECT 
            id,
            name,
            description,
            url,
            http_method,
            http_context,
            category_id,
            1 - (embedding <=> %s::vector) AS similarity
        FROM 
            apigent_tool
        WHERE 
            embedding IS NOT NULL
            AND 1 - (embedding <=> %s::vector) > %s
        ORDER BY 
            similarity DESC
        LIMIT %s
        """
        params = (text_embedding, text_embedding, similarity_threshold, limit * 2)

    # 执行查询
    results = query_dict(sql, params)

    if rerank and results:
        results = rerank_tools(results, text)
        results = results[:limit]  # 重排序后取前limit个结果

    logger.info(f"Retrieved {len(results)} tools for text: {text}")
    return results


def retrieve_tool_by_id(tool_id: int) -> Optional[Dict[str, Any]]:
    """
    根据工具ID获取工具详情

    Args:
        tool_id: 工具ID

    Returns:
        Optional[Dict[str, Any]]: 工具详情，如果不存在则返回None
    """
    sql = """
    SELECT 
        id,
        name,
        description,
        url,
        http_method,
        http_context,
        category_id
    FROM 
        apigent_tool
    WHERE 
        id = %s
    """

    results = query_dict(sql, (tool_id,))
    if results:
        return results[0]
    return None

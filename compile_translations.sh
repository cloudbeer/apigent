#!/bin/bash

# 设置翻译文件的基础目录
TRANSLATIONS_DIR="app/translations"

# 检查目录是否存在
if [ ! -d "$TRANSLATIONS_DIR" ]; then
    echo "错误：翻译目录 $TRANSLATIONS_DIR 不存在"
    exit 1
fi

# 遍历所有语言目录
for lang_dir in "$TRANSLATIONS_DIR"/*/; do
    if [ -d "$lang_dir" ]; then
        lang=$(basename "$lang_dir")
        po_file="$lang_dir/LC_MESSAGES/messages.po"
        mo_file="$lang_dir/LC_MESSAGES/messages.mo"
        
        # 检查 .po 文件是否存在
        if [ -f "$po_file" ]; then
            echo "正在编译 $lang 翻译..."
            msgfmt -o "$mo_file" "$po_file"
            if [ $? -eq 0 ]; then
                echo "✓ $lang 翻译编译成功"
            else
                echo "✗ $lang 翻译编译失败"
            fi
        else
            echo "警告：$lang 的翻译文件 $po_file 不存在"
        fi
    fi
done

echo "翻译文件编译完成！" 
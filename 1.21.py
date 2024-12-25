import streamlit as st
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
from pyecharts.charts import WordCloud, Bar, Pie, Line, Radar, Scatter, Funnel
from pyecharts import options as opts
from streamlit_echarts import st_pyecharts

# 配置 Streamlit 页面
st.set_page_config(page_title="文章词频分析", layout="wide", page_icon="📊")

# 页面标题与介绍
st.title("📊 文章词频分析与可视化")
st.markdown("""
欢迎使用文章词频分析工具！✨  
您可以输入网页链接，我们会自动抓取文章内容并为您生成各种词频统计图表。
""")

# 定义函数：抓取网页文本内容
@st.cache_data
def fetch_text_from_url(url):
    """
    根据用户输入的 URL 抓取网页内容，并提取正文文本。
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        # 提取 body 中的文Q本内容
        body_text = soup.body.get_text(separator="\n", strip=True)
        return body_text
    except Exception as e:
        st.error(f"❌ 抓取内容失败: {e}")
        return ""


# 定义函数：分词与词频统计
def analyze_text(text, min_freq=1):
    """
    使用 Jieba 对文本进行分词，并计算词频。
    """
    words = jieba.lcut(text)
    # 过滤掉长度小于 2 的词
    filtered_words = [word for word in words if len(word) > 1]
    word_counts = Counter(filtered_words)
    # 过滤低频词
    filtered_word_counts = {word: count for word, count in word_counts.items() if count >= min_freq}
    return filtered_word_counts


# 定义函数：绘制词云
def create_wordcloud(word_counts):
    wordcloud = (
        WordCloud()
        .add("", [list(item) for item in word_counts.items()], word_size_range=[20, 100])
        .set_global_opts(title_opts=opts.TitleOpts(title="词云图", subtitle="最常出现的词汇可视化"))
    )
    return wordcloud


# 定义函数：绘制柱状图
def create_bar_chart(word_counts):
    bar = (
        Bar()
        .add_xaxis(list(word_counts.keys()))
        .add_yaxis("词频", list(word_counts.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图", subtitle="前 20 高频词柱状图"))
    )
    return bar


# 定义函数：绘制饼图
def create_pie_chart(word_counts):
    pie = (
        Pie()
        .add("", [list(item) for item in word_counts.items()])
        .set_global_opts(title_opts=opts.TitleOpts(title="词频饼图", subtitle="前 20 高频词分布"))
    )
    return pie


# 定义函数：绘制折线图
def create_line_chart(word_counts):
    line = (
        Line()
        .add_xaxis(list(word_counts.keys()))
        .add_yaxis("词频", list(word_counts.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="词频折线图", subtitle="前 20 高频词变化趋势"))
    )
    return line


# 定义函数：绘制雷达图
def create_radar_chart(word_counts):
    words = list(word_counts.keys())
    values = list(word_counts.values())
    max_val = max(values)
    radar = (
        Radar()
        .add_schema(
            schema=[{"name": word, "max": max_val} for word in words[:7]],
            shape="circle"
        )
        .add("词频", [values[:7]])
        .set_global_opts(title_opts=opts.TitleOpts(title="词频雷达图", subtitle="前 7 高频词雷达图"))
    )
    return radar


# 定义函数：绘制散点图
def create_scatter_chart(word_counts):
    scatter = (
        Scatter()
        .add_xaxis(list(word_counts.keys()))
        .add_yaxis("词频", list(word_counts.values()))
        .set_global_opts(title_opts=opts.TitleOpts(title="词频散点图", subtitle="前 20 高频词分布"))
    )
    return scatter


# 定义函数：绘制漏斗图
def create_funnel_chart(word_counts):
    funnel = (
        Funnel()
        .add("", [list(item) for item in word_counts.items()])
        .set_global_opts(title_opts=opts.TitleOpts(title="词频漏斗图", subtitle="前 20 高频词漏斗分布"))
    )
    return funnel


# 用户输入文章 URL
url = st.text_input("请输入文章 URL:", value="")

# 词频最低过滤值
st.sidebar.header("⚙️ 参数设置")
min_freq = st.sidebar.slider("设置最低词频过滤值:", min_value=1, max_value=10, value=1, step=1)

# 图表类型选择
chart_type = st.sidebar.selectbox(
    "选择图表类型:",
    ["词云图", "柱状图", "饼图", "折线图", "雷达图", "散点图", "漏斗图"]
)

# 分析流程
if url:
    st.write(f"🔗 正在分析文章内容：{url}")
    with st.spinner("抓取和分析中，请稍候..."):
        text = fetch_text_from_url(url)
        if text:
            # 分析词频
            word_counts = analyze_text(text, min_freq)
            # 提取前 20 词频
            top_20_words = dict(Counter(word_counts).most_common(20))
            st.success("🎉 成功抓取并分析文章内容！")

            # 显示词频结果
            st.subheader("📋 词频排名前 20 的词汇:")
            st.write(top_20_words)

            # 绘制图表
            st.subheader("📊 数据可视化")
            if chart_type == "词云图":
                chart = create_wordcloud(top_20_words)
            elif chart_type == "柱状图":
                chart = create_bar_chart(top_20_words)
            elif chart_type == "饼图":
                chart = create_pie_chart(top_20_words)
            elif chart_type == "折线图":
                chart = create_line_chart(top_20_words)
            elif chart_type == "雷达图":
                chart = create_radar_chart(top_20_words)
            elif chart_type == "散点图":
                chart = create_scatter_chart(top_20_words)
            elif chart_type == "漏斗图":
                chart = create_funnel_chart(top_20_words)
            else:
                chart = None

            # 显示图表
            if chart:
                st_pyecharts(chart)
        else:
            st.error("❌ 未能成功抓取文章内容，请检查 URL 是否有效。")

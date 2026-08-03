import streamlit as st
import pandas as pd
import os
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet



st.set_page_config(
    page_title="劳动补偿辅助系统",
    layout="wide"
)


st.title("劳动补偿辅助系统 V3.2")


st.warning(
"""
本工具用于劳动解除补偿估算。

计算参考：
《中华人民共和国劳动合同法》

结果仅作为参考。
实际案件需结合合同、解除理由及证据。
"""
)



# =========================
# 工作时间
# =========================

st.header("一、劳动关系信息")


c1,c2=st.columns(2)


with c1:

    join_year=st.number_input(
        "入职年份",
        1970,
        2100,
        2020
    )

    join_month=st.number_input(
        "入职月份",
        1,
        12,
        1
    )


with c2:

    leave_year=st.number_input(
        "离职年份",
        1970,
        2100,
        2026
    )

    leave_month=st.number_input(
        "离职月份",
        1,
        12,
        8
    )



def calc_N():

    months=(leave_year-join_year)*12+(leave_month-join_month)

    if months<6:
        return 0.5

    year=months//12

    remain=months%12

    if remain==0:
        return year

    if remain<6:
        return year+0.5

    return year+1



N=calc_N()



# =========================
# 工资
# =========================

st.header("二、12个月工资")


upload=st.file_uploader(
    "上传工资Excel（可选）",
    type=["xlsx"]
)



if upload:


    salary=pd.read_excel(upload)

    st.write("读取工资：")

    st.dataframe(salary)



    avg_salary=salary["工资"].mean()


else:


    salary=pd.DataFrame(

    {

    "月份":[f"第{i}个月" for i in range(1,13)],

    "基本工资":[5000]*12,

    "绩效":[0]*12,

    "奖金":[0]*12,

    "津贴":[0]*12,

    "提成":[0]*12,

    "加班":[0]*12

    })


    salary=st.data_editor(
        salary,
        use_container_width=True
    )


    salary["工资"]=(
        salary["基本工资"]
        +
        salary["绩效"]
        +
        salary["奖金"]
        +
        salary["津贴"]
        +
        salary["提成"]
        +
        salary["加班"]
    )


    avg_salary=salary["工资"].mean()



# =========================
# 工资封顶
# =========================

st.header("三、工资基数限制")


social_avg=st.number_input(
    "当地上年度平均工资",
    value=8000
)


max_salary=social_avg*3


actual_salary=avg_salary



if avg_salary>max_salary:

    st.warning(
        f"""
        当前平均工资：
        {avg_salary:.2f}

        超过当地平均工资3倍：

        按 {max_salary:.2f} 元计算
        """
    )

    actual_salary=max_salary



# =========================
# 法律判断
# =========================

st.header("四、解除风险判断")


case=st.selectbox(

"解除情况",

[
"公司正常解除",
"公司未提前30天通知",
"公司违法解除",
"员工主动辞职",
"协商解除"
]

)


if case=="公司正常解除":

    months=N

    reason="按照N计算"


elif case=="公司未提前30天通知":

    months=N+1

    reason="N+1"


elif case=="公司违法解除":

    months=N*2

    reason="违法解除，2N"


elif case=="员工主动辞职":

    months=0

    reason="通常无补偿"


else:

    months=N

    reason="协商解除"



money=months*actual_salary



# =========================
# 输出
# =========================


st.header("五、计算结果")


result=f"""
劳动补偿计算报告

入职：
{join_year}-{join_month}

离职：
{leave_year}-{leave_month}


N：
{N}个月


平均工资：
{actual_salary:.2f}元/月


计算方式：
{reason}


补偿月份：
{months}个月


预计金额：
{money:.2f}元
"""



st.success(result)



# =========================
# PDF生成
# =========================


st.header("六、生成报告")


if st.button("生成PDF报告"):


    if not os.path.exists("reports"):
        os.makedirs("reports")


    filename=f"reports/劳动补偿报告_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"



    doc=SimpleDocTemplate(filename)


    styles=getSampleStyleSheet()


    story=[]


    for line in result.split("\n"):

        story.append(
            Paragraph(
                line,
                styles["Normal"]
            )
        )

        story.append(
            Spacer(1,12)
        )


    doc.build(story)



    with open(filename,"rb") as f:


        st.download_button(

            "下载PDF报告",

            f,

            file_name=os.path.basename(filename)

        )
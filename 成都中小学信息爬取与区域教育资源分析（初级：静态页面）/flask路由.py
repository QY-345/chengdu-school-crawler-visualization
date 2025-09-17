from flask import Flask, render_template, jsonify

from school_datas import mysql_data

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index():
    return render_template("ECharts form.html")


@app.route("/api/school_data")
def get_school_data():
    area,count_numb = mysql_data()  # 调用爬虫获取数据
    return jsonify({
        "areas": area,
        "counts": count_numb
    })  # 以 JSON 格式返回


if __name__ == '__main__':
    app.run(debug=True)

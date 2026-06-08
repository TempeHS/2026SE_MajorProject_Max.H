from flask import Flask
from flask import render_template
from flask import request
import database_manager as dbhandler

app = Flask(
    __name__,
    template_folder="Flaskapp/templates",
    static_folder="Flaskapp/static",
)


@app.route("/")
@app.route("/search", methods=["GET"])
def search():
    search = request.args.get("search", "").strip()
    results = []
    leaderboards = dbhandler.get_leaderboards(search)

    if search:
        results = dbhandler.search_servers(search)
        leaderboards = dbhandler.get_leaderboards(search)

    return render_template(
        "search.html", search=search, results=results, leaderboards=leaderboards
    )


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)

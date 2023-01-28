from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, username "
        "FROM post p "
        "LEFT JOIN user u ON p.author_id = u.id "
        "ORDER BY created DESC; ").fetchall()

    return render_template("blog/index.html.jinja", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)"
                " VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html.jinja")


def get_post(post_id, check_author=True):
    """
    Gets a Post by id and verifys the post exists and post author is the current session user.
    """

    post = (get_db().execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id=?",
        (post_id, ),
    ).fetchone())

    if post is None:
        abort(404, f"Post id {post_id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/<int:id_>/update", methods=("GET", "POST"))
def update(id_):
    post = get_post(id_)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute("UPDATE post SET title = ?, body = ?"
                       " WHERE id = ?", (title, body, id_))
            db.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html.jinja", post=post)


@bp.route("/<int:id_>/delete", methods=("POST", ))
@login_required
def delete(id_):
    get_post(id_)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id_, ))
    db.commit()
    return redirect(url_for("blog.index"))

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db


bp = Blueprint('blog', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.j2', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.j2')


def get_post(id, check_author=True):
    params = (id,)
    post = get_db().execute(
        'SELECT p.id, p.title, p.body, p.created, p.author_id, u.username '
        'FROM post p JOIN user u ON p.author_id = u.id '
        'WHERE p.id = ?',
        params
    ).fetchone()

    if post is None:
        abort(404, f'Post with id {id} does not exist.')

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            params = (title, body, id)
            db.execute('UPDATE post SET title = ?, body = ? WHERE id = ?',
                params
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.j2', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    params = (id,)
    db.execute('DELETE FROM post WHERE id = ?', params)
    db.commit()
    return redirect(url_for('blog.index'))
